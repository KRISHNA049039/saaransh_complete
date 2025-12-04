from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


class KeycloakCreateUser(BaseModel):
    username: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    enabled: bool = True
    emailVerified: bool = False


class KeycloakUserRepresentation(BaseModel):
    id: Optional[str]
    username: Optional[str]
    email: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    enabled: Optional[bool] = None
    emailVerified: Optional[bool] = None


class PartialImportUserRepresentation(BaseModel):
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    enabled: Optional[bool] = True
    emailVerified: Optional[bool] = False
    realmRoles: Optional[List[str]] = None

class ResourceExistBehavior(str, Enum):
    FAIL = "FAIL"
    SKIP = "SKIP"
    OVERWRITE = "OVERWRITE"

class PartialImportUsersPayload(BaseModel):
    users: List[PartialImportUserRepresentation]
    ifResourceExists: ResourceExistBehavior

class PartialImportResult(BaseModel):
    action: str
    resourceType: str
    resourceName: str
    id: str

class PartialImportResponse(BaseModel):
    overwritten: int
    added: int
    skipped: int
    results: List[PartialImportResult]





