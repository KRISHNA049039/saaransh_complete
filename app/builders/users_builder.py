import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app import settings
from app.accessors.keycloak_accessor import get_keycloak_accessor, KeycloakCreateUser
from app.accessors.user_accessor import UserAccessor
from app.models.keycloak_models import KeycloakEditUser
from app.models.orm.users import User
from app.models.request.users_request import (
    UserCreateRequest,
    UserEditRequest,
    UserFetchFilter,
)
from app.models.response.users_response import BulkUserCreateResponse, UserResponse
from app.settings import settings
from app.utils.string_util import get_username_from_email

logger = logging.getLogger(__name__)


class UserBuilder:
    def __init__(self, session: AsyncSession, accessor: UserAccessor | None = None):
        self.session = session
        self.user_accessor = accessor or UserAccessor()
        self.kc = get_keycloak_accessor()

    async def build_create_users(
        self, requests: list[UserCreateRequest], created_by: UUID
    ) -> BulkUserCreateResponse:
        results = []
        any_errors = False
        any_success = False

        for request in requests:
            keycloak_user_id = None

            try:
                user_name = get_username_from_email(request.user_email)

                kc_user = KeycloakCreateUser(
                    username=user_name,
                    email=request.user_email,
                    firstName=request.first_name,
                    lastName=request.last_name,
                    enabled=request.is_active,
                )

                keycloak_user_id = await self.kc.create_user(kc_user, request.is_admin)

                model = User(
                    user_id=keycloak_user_id,
                    user_name=user_name,
                    user_email=request.user_email,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    external_user_id=request.external_user_id,
                    is_admin=request.is_admin,
                    is_active=request.is_active,
                    effective_from=datetime.now(timezone.utc),
                    created_by=created_by,
                )

                db_user = await self.user_accessor.insert_commit(model, self.session)
                any_success = True

                results.append(UserResponse.model_validate(db_user))

            except Exception as e:
                logger.exception("Failed to create user")
                any_errors = True

                try:
                    await self.session.rollback()
                except Exception:
                    pass

                if keycloak_user_id:
                    try:
                        await self.kc.delete_user(keycloak_user_id)
                    except Exception as delete_err:
                        logger.error(f"Failed to cleanup Keycloak user: {delete_err}")

                results.append(
                    UserResponse(
                        user_name=request.user_email,
                        user_email=request.user_email,
                        first_name=request.first_name,
                        last_name=request.last_name,
                        external_user_id=request.external_user_id,
                        is_admin=request.is_admin,
                        error=str(e),
                    )
                )

        success = not any_errors
        partial = any_success and any_errors

        return BulkUserCreateResponse(
            success=success,
            partial=partial,
            results=results,
        )

    async def build_update_users(
        self, request: UserEditRequest, created_by: UUID
    ) -> UserResponse:
        user_id = request.user_id

        filters = UserFetchFilter(user_id=user_id)
        records = await self.user_accessor.fetch(filters=filters, session=self.session)
        if not records:
            raise Exception("User not found")

        existing_record: User = records[0]

        original_first = existing_record.first_name
        original_last = existing_record.last_name
        original_active = existing_record.is_active
        original_admin = existing_record.is_admin

        try:
            kc_update = KeycloakEditUser(
                firstName=request.first_name,
                lastName=request.last_name,
                enabled=request.is_active,
            )

            await self.kc.update_user_fields(user_id, kc_update)

            if request.is_admin != original_admin:
                if request.is_admin:
                    await self.kc.assign_realm_role(
                        user_id, settings.KC_SAARANSH_ADMIN_ROLE
                    )
                else:
                    await self.kc.remove_realm_role(
                        user_id, settings.KC_SAARANSH_ADMIN_ROLE
                    )
        except Exception as kc_err:
            raise Exception(f"Keycloak update failed: {kc_err}") from kc_err

        try:
            await self.user_accessor.close_active_record(user_id, self.session)
            model = User(
                user_id=user_id,
                user_name=existing_record.user_name,
                user_email=existing_record.user_email,
                first_name=(
                    request.first_name
                    if request.first_name is not None
                    else existing_record.first_name
                ),
                last_name=(
                    request.last_name
                    if request.last_name is not None
                    else existing_record.last_name
                ),
                is_admin=request.is_admin,
                is_active=request.is_active,
                external_user_id=request.external_user_id,
                effective_from=datetime.now(timezone.utc),
                created_by=existing_record.created_by,
                modified_by=created_by,
            )

            db_user = await self.user_accessor.insert_flush(model, self.session)

            await self.session.commit()
            return UserResponse.model_validate(db_user)

        except Exception as db_err:
            await self.session.rollback()
            try:
                if request.is_admin != original_admin:
                    if original_admin:
                        await self.kc.assign_realm_role(
                            user_id, settings.KC_SAARANSH_ADMIN_ROLE
                        )
                    else:
                        await self.kc.remove_realm_role(
                            user_id, settings.KC_SAARANSH_ADMIN_ROLE
                        )

                revert_payload = KeycloakEditUser(
                    firstName=original_first,
                    lastName=original_last,
                    enabled=original_active,
                )
                await self.kc.update_user_fields(user_id, revert_payload)

            except Exception as revert_err:
                logger.error(
                    f"FAILED to revert Keycloak after DB rollback: {revert_err}"
                )

            raise Exception(f"Database update failed: {db_err}") from db_err
