# API Models and Validation

## Overview

Saaransh Backend uses Pydantic models for comprehensive API request/response validation and serialization. The system implements a structured approach with separate request and response models, built-in validation, and support for complex data structures including nested objects and SCD2 filtering.

## Model Architecture

### Model Organization

```
app/models/
├── request/           # API request models with validation
├── response/          # API response models with serialization
├── orm/              # SQLAlchemy database models
├── task_data.py      # Complex nested data structures
├── keycloak_models.py # External service integration models
└── constants.py      # System constants and enums
```

### Validation Strategy

1. **Input Validation**: Pydantic models validate all incoming requests
2. **Type Safety**: Strong typing with UUID, datetime, and custom types
3. **Business Rules**: Custom validators for business logic
4. **Serialization**: Automatic JSON serialization/deserialization
5. **Documentation**: Auto-generated OpenAPI schemas

## Request Models

### 1. Summary Request Models

#### StagingCreateRequest
```python
class StagingCreateRequest(BaseModel):
    model: Optional[str] = None                    # LLM model to use
    user_prompt: Optional[str] = None              # User instructions
    user_data: UserData                            # Complex nested task data

# Example usage:
{
  "model": "gemini/gemini-2.5-flash",
  "user_prompt": "Focus on technical achievements",
  "user_data": {
    "employee": {
      "name": "John Doe",
      "role": "Senior Engineer"
    },
    "tasks": [
      {
        "title": "API Development",
        "description": "Built REST API",
        "comments": [{"text": "Added OAuth2"}],
        "logs": [{"content": "95% test coverage"}]
      }
    ]
  }
}
```

#### SummaryCreateRequest
```python
class SummaryCreateRequest(BaseModel):
    model: Optional[str] = None                    # LLM model override
    summary_id: UUID4                              # Required summary ID
    summary_sk: Optional[int] = None               # Specific version
    user_prompt: Optional[str] = None              # Refinement instructions

# Validation:
# - summary_id must be valid UUID4
# - Either summary_sk or summary_id required for version identification
```

#### SummaryEditRequest
```python
class SummaryEditRequest(BaseModel):
    summary_id: UUID4                              # Required summary ID
    summary_sk: Optional[int] = None               # Specific version
    content: Optional[str] = None                  # Current content
    user_prompt: str                               # Required edit instructions
    staging: bool                                  # Staging vs final mode

# Validation:
# - user_prompt is required (cannot be empty)
# - staging flag determines prompt template used
```

#### SummarySaveRequest
```python
class SummarySaveRequest(BaseModel):
    summary_sk: Optional[int] = None               # Version identifier
    summary_id: Optional[UUID4] = None             # Summary identifier
    content: str                                   # Required content

# Validation:
# - Either summary_sk or summary_id must be provided
# - content cannot be empty
```

### 2. Comment Request Models

#### CommentCreateRequest
```python
class CommentCreateRequest(BaseModel):
    summary_id: UUID4                              # Required summary reference
    content: str                                   # Required comment text

# Validation:
# - summary_id must exist and be accessible
# - content cannot be empty
```

#### CommentEditRequest
```python
class CommentEditRequest(BaseModel):
    comment_id: UUID4                              # Required comment ID
    content: str                                   # Required new content

# Validation:
# - comment_id must exist and be editable by user
# - content cannot be empty
```

### 3. User Request Models

#### UserCreateRequest
```python
class UserCreateRequest(BaseModel):
    user_email: str                                # Required unique email
    first_name: Optional[str] = None               # Optional first name
    last_name: Optional[str] = None                # Optional last name
    is_active: bool = True                         # Default active status
    is_admin: bool = False                         # Default non-admin

# Validation:
# - user_email must be valid email format
# - user_email must be unique in system
# - is_active and is_admin have sensible defaults
```

#### UserEditRequest
```python
class UserEditRequest(BaseModel):
    user_id: UUID                                  # Required user identifier
    first_name: Optional[str] = None               # Optional name update
    last_name: Optional[str] = None                # Optional name update
    is_active: bool = True                         # Required status
    is_admin: bool = False                         # Required admin flag

# Validation:
# - user_id must exist in system
# - is_active and is_admin are required (no defaults)
```

### 4. Sharing Request Models

#### SummariesUsersCreateRequest
```python
class SummariesUsersCreateRequest(BaseModel):
    summary_id: UUID4                              # Required summary ID
    user_id: UUID4                                 # Required user ID
    role_id: int                                   # Required role (0-3)

# Validation:
# - summary_id must exist and be owned by requester
# - user_id must exist and be active
# - role_id must be valid (0=OWNER, 1=EDITOR, 2=VIEWER, 3=ADMIN)
```

### 5. Filter Models

#### SCD2Filter (Base Class)
```python
class SCD2Filter(BaseModel):
    effective_only: bool = True                    # Show only current versions

# Used by all versioned entities for consistent filtering
```

#### SummaryFetchFilter
```python
class SummaryFetchFilter(SCD2Filter):
    summary_sk: Optional[int] = None               # Specific version
    summary_id: Optional[UUID4] = None             # Summary identifier
    is_active: Optional[bool] = None               # Active status filter
    status_id: Optional[int] = None                # Status filter (0-5)

# Inherits effective_only from SCD2Filter
# All filters are optional for flexible querying
```

## Response Models

### 1. Summary Response Models

#### SummaryResponse
```python
class SummaryResponse(BaseModel):
    summary_sk: int                                # Version identifier
    summary_id: UUID                               # Business identifier
    content: Optional[str]                         # HTML content
    start_date: Optional[datetime]                 # Period start
    end_date: Optional[datetime]                   # Period end
    status_id: Optional[int]                       # Current status
    meta_data: Optional[Dict[str, Any]]            # JSON metadata
    is_active: Optional[bool]                      # Active flag
    created_date: Optional[datetime]               # Creation timestamp
    created_by: Optional[UUID]                     # Creator user ID
    modified_by: Optional[UUID]                    # Last modifier
    effective_from: Optional[datetime]             # SCD2 start
    effective_to: Optional[datetime]               # SCD2 end
    entity_type_id: Optional[int]                  # Entity classification

    class Config:
        from_attributes = True                     # Enable ORM serialization
```

### 2. User Response Models

#### UserResponse
```python
class UserResponse(BaseModel):
    user_sk: int | None = None                     # Version identifier
    user_id: UUID | None = None                    # Business identifier
    user_name: str | None = None                   # Username
    user_email: str | None = None                  # Email address
    first_name: str | None = None                  # First name
    last_name: str | None = None                   # Last name
    is_active: bool | None = None                  # Active status
    is_admin: bool | None = None                   # Admin privileges
    effective_from: datetime | None = None         # SCD2 start
    effective_to: datetime | None = None           # SCD2 end
    created_by: UUID | None = None                 # Creator
    created_date: datetime | None = None           # Creation date
    error: str | None = None                       # Error message (bulk ops)

    model_config = {"from_attributes": True}
```

#### BulkUserCreateResponse
```python
class BulkUserCreateResponse(BaseModel):
    success: bool                                  # All operations successful
    partial: bool                                  # Some succeeded, some failed
    results: list[UserResponse]                    # Individual results

# Supports partial success scenarios in bulk operations
```

### 3. Collaboration Response Models

#### SummariesUsersFullResponse
```python
class SummariesUsersFullResponse(BaseModel):
    summaries_users_sk: Optional[int] = None       # Relationship ID
    summary: SummaryExpanded                       # Embedded summary data
    user: UserResponse                             # Embedded user data
    role_id: Optional[int] = None                  # User role
    reviewed: Optional[bool] = None                # Review status
    is_active: Optional[bool] = None               # Active status
    created_by: Optional[UUID] = None              # Who shared
    created_date: Optional[datetime] = None        # When shared

# Provides complete relationship data with embedded objects
```

## Complex Data Structures

### 1. UserData (Nested Structure)

```python
class Employee(BaseModel):
    name: str                                      # Employee name
    role: str                                      # Job title/role

class Comment(BaseModel):
    text: str                                      # Comment content

class Log(BaseModel):
    content: str                                   # Log entry content

class Task(BaseModel):
    title: str                                     # Task title
    description: str                               # Task description
    comments: List[Comment]                        # Associated comments
    logs: List[Log]                                # Activity logs

class UserData(BaseModel):
    employee: Employee                             # Employee information
    tasks: List[Task]                              # List of tasks

# Example structure:
{
  "employee": {
    "name": "John Doe",
    "role": "Senior Software Engineer"
  },
  "tasks": [
    {
      "title": "API Development",
      "description": "Developed REST API for user management",
      "comments": [
        {"text": "Implemented OAuth2 authentication"},
        {"text": "Added comprehensive error handling"}
      ],
      "logs": [
        {"content": "Started API design phase"},
        {"content": "Completed endpoint implementation"},
        {"content": "Achieved 95% test coverage"}
      ]
    }
  ]
}
```

### 2. Keycloak Integration Models

```python
class KeycloakCreateUser(BaseModel):
    username: str                                  # Required username
    email: str                                     # Required email
    firstName: Optional[str] = None                # Optional first name
    lastName: Optional[str] = None                 # Optional last name
    enabled: bool = True                           # Account enabled status
    emailVerified: bool = False                    # Email verification status

class KeycloakEditUser(BaseModel):
    firstName: Optional[str] = None                # Update first name
    lastName: Optional[str] = None                 # Update last name
    enabled: Optional[bool] = None                 # Update enabled status

# Separate models for create vs update operations
```

## Validation Patterns

### 1. Built-in Pydantic Validation

```python
from pydantic import BaseModel, UUID4, validator, Field
from typing import Optional
from datetime import datetime

class ExampleModel(BaseModel):
    # Type validation
    user_id: UUID4                                 # Validates UUID format
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')  # Email format
    age: int = Field(..., ge=0, le=150)           # Range validation
    
    # Optional with defaults
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Custom validation
    @validator('email')
    def validate_email_domain(cls, v):
        if not v.endswith('@company.com'):
            raise ValueError('Must use company email')
        return v
```

### 2. SCD2 Filter Pattern

```python
class SCD2Filter(BaseModel):
    effective_only: bool = True                    # Default to current versions

# Usage in all versioned entities:
class SummaryFetchFilter(SCD2Filter):
    summary_id: Optional[UUID4] = None
    status_id: Optional[int] = None
    # Inherits effective_only for consistent behavior
```

### 3. Bulk Operation Pattern

```python
# Request: List of individual requests
requests: List[UserCreateRequest]

# Response: Structured result with success indicators
class BulkUserCreateResponse(BaseModel):
    success: bool                                  # Overall success
    partial: bool                                  # Partial success
    results: List[UserResponse]                    # Individual results

# Each result can contain either data or error
```

## Serialization Configuration

### 1. ORM Integration

```python
class ResponseModel(BaseModel):
    model_config = {"from_attributes": True}       # Pydantic v2 syntax
    
    # Or legacy syntax:
    class Config:
        from_attributes = True                     # Enable ORM serialization
```

### 2. JSON Serialization

```python
# Automatic handling of complex types
class SummaryResponse(BaseModel):
    created_date: Optional[datetime]               # Auto ISO format
    meta_data: Optional[Dict[str, Any]]            # JSON serialization
    summary_id: UUID                               # String representation

# Custom serialization
def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, UUID):
        return str(obj)
    return obj
```

## Error Handling in Models

### 1. Validation Errors

```python
from pydantic import ValidationError

try:
    model = UserCreateRequest(**data)
except ValidationError as e:
    # Detailed error information
    errors = e.errors()
    # [
    #   {
    #     'loc': ('user_email',),
    #     'msg': 'field required',
    #     'type': 'value_error.missing'
    #   }
    # ]
```

### 2. Custom Validation

```python
class SummaryEditRequest(BaseModel):
    user_prompt: str
    content: Optional[str] = None
    
    @validator('user_prompt')
    def validate_prompt_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('User prompt cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content_length(cls, v):
        if v and len(v) > 100000:  # 100KB limit
            raise ValueError('Content too large')
        return v
```

### 3. Business Logic Validation

```python
class SummariesUsersCreateRequest(BaseModel):
    summary_id: UUID4
    user_id: UUID4
    role_id: int
    
    @validator('role_id')
    def validate_role_id(cls, v):
        valid_roles = [0, 1, 2, 3]  # OWNER, EDITOR, VIEWER, ADMIN
        if v not in valid_roles:
            raise ValueError(f'Invalid role_id. Must be one of {valid_roles}')
        return v
```

## API Documentation Generation

### 1. OpenAPI Schema

Pydantic models automatically generate OpenAPI schemas:

```json
{
  "SummaryCreateRequest": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "title": "Model"
      },
      "summary_id": {
        "type": "string",
        "format": "uuid",
        "title": "Summary Id"
      },
      "user_prompt": {
        "type": "string",
        "title": "User Prompt"
      }
    },
    "required": ["summary_id"],
    "title": "SummaryCreateRequest"
  }
}
```

### 2. Field Documentation

```python
from pydantic import Field

class UserCreateRequest(BaseModel):
    user_email: str = Field(
        ..., 
        description="User's email address (must be unique)",
        example="john.doe@example.com"
    )
    is_admin: bool = Field(
        False,
        description="Whether user has admin privileges"
    )
```

## Testing Models

### 1. Model Validation Tests

```python
import pytest
from pydantic import ValidationError

def test_user_create_request_valid():
    data = {
        "user_email": "test@example.com",
        "first_name": "Test",
        "is_active": True
    }
    request = UserCreateRequest(**data)
    assert request.user_email == "test@example.com"
    assert request.is_admin == False  # Default value

def test_user_create_request_invalid_email():
    data = {"user_email": "invalid-email"}
    with pytest.raises(ValidationError) as exc_info:
        UserCreateRequest(**data)
    
    errors = exc_info.value.errors()
    assert any(error['loc'] == ('user_email',) for error in errors)
```

### 2. Serialization Tests

```python
def test_summary_response_serialization():
    # Test ORM to Pydantic conversion
    orm_summary = Summary(
        summary_sk=123,
        summary_id=uuid4(),
        content="Test content",
        created_date=datetime.now()
    )
    
    response = SummaryResponse.from_orm(orm_summary)
    assert response.summary_sk == 123
    assert response.content == "Test content"
    
    # Test JSON serialization
    json_data = response.model_dump()
    assert isinstance(json_data['summary_id'], str)
    assert isinstance(json_data['created_date'], str)
```

## Best Practices

### 1. Model Design
- Use separate request and response models
- Implement proper validation with meaningful error messages
- Use optional fields with sensible defaults
- Document fields with descriptions and examples

### 2. Validation Strategy
- Validate at the API boundary (request models)
- Use built-in Pydantic validators when possible
- Implement custom validators for business rules
- Provide clear error messages for validation failures

### 3. Serialization
- Configure `from_attributes = True` for ORM integration
- Handle complex types (UUID, datetime) automatically
- Use consistent naming conventions
- Test serialization/deserialization thoroughly

### 4. Error Handling
- Catch and handle ValidationError appropriately
- Provide user-friendly error messages
- Log validation errors for debugging
- Return structured error responses

### 5. Documentation
- Use Field descriptions for API documentation
- Provide realistic examples in field definitions
- Keep model documentation up to date
- Generate and review OpenAPI schemas regularly