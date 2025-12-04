import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.accessors.keycloak_accessor import get_keycloak_accessor, KeycloakCreateUser
from app.accessors.user_accessor import UserAccessor
from app.models.orm.users import User
from app.models.request.users_request import UserCreateRequest
from app.models.response.users_response import BulkUserCreateResponse, UserResponse
from app.utils.string_util import get_username_from_email

logger = logging.getLogger(__name__)


class UserBuilder:
    def __init__(self, session: AsyncSession, accessor: UserAccessor | None = None):
        self.session = session
        self.user_accessor = accessor or UserAccessor()
        self.kc = get_keycloak_accessor()

    async def build_create_users(self, requests: list[UserCreateRequest], created_by: UUID) -> BulkUserCreateResponse:
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
                    enabled=request.enabled,
                    )

                keycloak_user_id = await self.kc.create_user(kc_user, request.is_admin)

                model = User(
                    user_id=keycloak_user_id,
                    user_name=user_name,
                    user_email=request.user_email,
                    first_name=request.first_name,
                    last_name=request.last_name,
                    is_admin=request.is_admin,
                    is_active=request.enabled,
                    effective_from=datetime.now(timezone.utc),
                    created_by=created_by
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