from fastapi import APIRouter, Depends, HTTPException, Query
from app.accessors.keycloak_accessor import KeycloakAccessor
from app.models.keycloak_models import KeycloakCreateUser, PartialImportUsersPayload


router = APIRouter(prefix="/keycloak", tags=["test"])


@router.post("/")
async def create_user(request: KeycloakCreateUser,
                      is_admin: bool =  Query(default = False)):
    keycloak_accessor = KeycloakAccessor()
    try:
        user_id = await keycloak_accessor.create_user(
            request,
            is_admin
            )

        return {"message": "insertion successful", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/")
async def delete_user(user_id):
    keycloak_accessor = KeycloakAccessor()
    try:
        await keycloak_accessor.delete_user(user_id)

        return {"message": "deletion successful"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
async def get_user(user_id):
    try:
        keycloak_accessor = KeycloakAccessor()
        return await keycloak_accessor.get_user(user_id)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


@router.post("/partial")
async def partial_import(request: PartialImportUsersPayload):
    try:
        keycloak_accessor = KeycloakAccessor()
        return await keycloak_accessor.partial_import(request)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))