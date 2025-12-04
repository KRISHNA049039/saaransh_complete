from typing import Optional
from uuid import UUID
from app.config.security.oauth2_client import kc_admin_client
from app.settings import settings
from app.models.keycloak_models import (
    KeycloakCreateUser,
    KeycloakEditUser,
    KeycloakUserRepresentation,
    PartialImportResponse,
    PartialImportUsersPayload,
)

KEYCLOAK_BASE_URL = settings.KEYCLOAK_URL
RESOURCE_REALM = settings.KEYCLOAK_RESOURCE_REALM

ADMIN_ROLE = settings.KC_SAARANSH_ADMIN_ROLE

USERS_URL = f"{KEYCLOAK_BASE_URL}/admin/realms/{RESOURCE_REALM}/users"
USER_URL = f"{KEYCLOAK_BASE_URL}/admin/realms/{RESOURCE_REALM}/users/{{user_id}}"
USER_ROLE_MAPPINGS_URL = f"{KEYCLOAK_BASE_URL}/admin/realms/{RESOURCE_REALM}/users/{{user_id}}/role-mappings/realm"
ROLE_BY_NAME_URL = (
    f"{KEYCLOAK_BASE_URL}/admin/realms/{RESOURCE_REALM}/roles/{{role_name}}"
)
PARTIAL_IMPORT_URL = f"{KEYCLOAK_BASE_URL}/admin/realms/{RESOURCE_REALM}/partialImport"


class KeycloakAccessor:
    async def create_user(self, payload: KeycloakCreateUser, is_admin: bool) -> UUID:

        resp = await kc_admin_client.post(USERS_URL, json=payload.model_dump())

        if resp.status_code not in (201, 204):
            raise Exception(f"Failed to create user: {resp.text}")

        location = resp.headers.get("Location")
        if not location:
            raise Exception("Keycloak did not return user location header.")

        user_id = location.rstrip("/").split("/")[-1]

        if is_admin:
            await self.assign_realm_role(user_id, ADMIN_ROLE)

        return user_id

    async def assign_realm_role(self, user_id: UUID, role_name: str):
        role_resp = await kc_admin_client.get(
            ROLE_BY_NAME_URL.format(role_name=role_name)
        )

        if role_resp.status_code != 200:
            raise Exception(f"Failed to fetch role '{role_name}': {role_resp.text}")

        role_data = role_resp.json()

        resp = await kc_admin_client.post(
            USER_ROLE_MAPPINGS_URL.format(user_id=user_id),
            json=[role_data],
        )

        if resp.status_code not in (201, 204):
            raise Exception(
                f"Failed to assign role '{role_name}' to user {user_id}: {resp.text}"
            )

    async def remove_realm_role(self, user_id: UUID, role_name: str):

        role_response = await kc_admin_client.get(
            ROLE_BY_NAME_URL.format(role_name=role_name)
        )
        if role_response.status_code != 200:
            raise Exception(f"Failed to fetch role '{role_name}': {role_response.text}")

        role_data = role_response.json()

        response = await kc_admin_client.request(
            "DELETE",
            USER_ROLE_MAPPINGS_URL.format(user_id=user_id),
            json=[role_data],
        )

        if response.status_code not in (204, 200):
            raise Exception(
                f"Failed to remove role '{role_name}' from user {user_id}: {response.text}"
            )

    async def get_user(self, user_id: UUID) -> Optional[KeycloakUserRepresentation]:
        response = await kc_admin_client.get(USER_URL.format(user_id=user_id))

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise Exception(f"Failed to fetch user {user_id}: {response.text}")

        return KeycloakUserRepresentation.model_validate(response.json())

    async def delete_user(self, user_id: UUID) -> None:
        response = await kc_admin_client.request(
            "DELETE", USER_URL.format(user_id=user_id)
        )

        if response.status_code == 404:
            raise Exception(f"User {user_id} not found.")

        if response.status_code not in (204, 202):
            raise Exception(f"Failed to delete user {user_id}: {response.text}")

    async def partial_import(
        self, payload: PartialImportUsersPayload
    ) -> PartialImportResponse:
        response = await kc_admin_client.post(
            PARTIAL_IMPORT_URL, json=payload.model_dump()
        )

        if response.status_code not in (200, 201):
            raise Exception(f"Partial import failed: {response.text}")

        return PartialImportResponse.model_validate(response.json())

    async def set_user_enabled(self, user_id: UUID, enabled: bool) -> None:
        response = await kc_admin_client.put(
            USER_URL.format(user_id=str(user_id)),
            json={"enabled": enabled},
        )

        if response.status_code not in (204, 200):
            raise Exception(
                f"Failed to set enabled={enabled} for user {user_id}: {response.text}"
            )

    async def update_user_fields(
        self,
        user_id: UUID,
        payload: KeycloakEditUser,
    ) -> None:
        update_body = payload.model_dump(exclude_unset=True)
        if not update_body:
            return

        response = await kc_admin_client.put(
            USER_URL.format(user_id=str(user_id)),
            json=update_body,
        )

        if response.status_code not in (204, 200):
            raise Exception(f"Failed to update user {user_id}: {response.text}")

    async def get_user_raw(self, user_id: UUID) -> Optional[dict]:
        response = await kc_admin_client.get(USER_URL.format(user_id=user_id))

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise Exception(f"Failed to fetch user {user_id}: {response.text}")

        return response.json()


def get_keycloak_accessor():
    return KeycloakAccessor()
