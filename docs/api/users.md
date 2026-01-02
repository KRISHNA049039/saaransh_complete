# User Management API

## Overview

The User Management API provides comprehensive user lifecycle management with integrated Keycloak authentication. The system supports bulk user operations, role-based administration, and seamless synchronization between the local database and Keycloak identity provider.

## User Management Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Saaransh      │    │    Keycloak     │    │   Local User    │
│   Admin UI      │    │   Identity      │    │   Database      │
│                 │    │   Provider      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    User Builder                                 │
│              (Orchestrates User Operations)                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Dual System Integration**: Synchronizes users between Keycloak and local database
2. **Bulk Operations**: Create multiple users in a single transaction
3. **Role Management**: Admin role assignment with Keycloak realm roles
4. **Version Control**: Complete user history using SCD2 pattern
5. **Error Handling**: Comprehensive rollback and cleanup mechanisms
6. **Audit Trail**: Track all user modifications and administrative actions

## User Roles and Permissions

### System Roles

| Role | Description | Keycloak Role | Permissions |
|------|-------------|---------------|-------------|
| **Regular User** | Standard user with basic access | `USER` (default) | Create summaries, collaborate |
| **Admin User** | Administrative privileges | `SAARANSH_ADMIN` | User management, system administration |

### Admin Capabilities

- Create and manage user accounts
- Assign and revoke admin privileges
- View all user information
- Perform bulk user operations
- Access system-wide analytics

## API Endpoints

### 1. Create Users (Bulk)

Create multiple users in a single operation with automatic Keycloak integration.

**Endpoint:** `POST /api/v1/users`

**Request Body:**
```json
[
  {
    "user_email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_admin": false
  },
  {
    "user_email": "jane.admin@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "is_active": true,
    "is_admin": true
  }
]
```

**Response (Success):**
```json
{
  "success": true,
  "partial": false,
  "results": [
    {
      "user_sk": 123,
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_name": "john.doe",
      "user_email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_admin": false,
      "effective_from": "2024-01-15T10:30:00Z",
      "created_by": "admin-user-uuid",
      "created_date": "2024-01-15T10:30:00Z",
      "error": null
    },
    {
      "user_sk": 124,
      "user_id": "456e7890-f12b-34c5-d678-901234567890",
      "user_name": "jane.admin",
      "user_email": "jane.admin@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_active": true,
      "is_admin": true,
      "effective_from": "2024-01-15T10:30:00Z",
      "created_by": "admin-user-uuid",
      "created_date": "2024-01-15T10:30:00Z",
      "error": null
    }
  ]
}
```

**Response (Partial Failure):**
```json
{
  "success": false,
  "partial": true,
  "results": [
    {
      "user_sk": 123,
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "user_name": "john.doe",
      "user_email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_admin": false,
      "effective_from": "2024-01-15T10:30:00Z",
      "created_by": "admin-user-uuid",
      "created_date": "2024-01-15T10:30:00Z",
      "error": null
    },
    {
      "user_name": "jane.admin@example.com",
      "user_email": "jane.admin@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "is_admin": true,
      "error": "Email already exists in Keycloak"
    }
  ]
}
```

**Process Flow:**
1. **Username Generation**: Extract username from email (e.g., `john.doe` from `john.doe@example.com`)
2. **Keycloak User Creation**: Create user in Keycloak with generated username
3. **Role Assignment**: Assign `SAARANSH_ADMIN` role if `is_admin: true`
4. **Local Database Storage**: Store user information with Keycloak user ID
5. **Error Handling**: Rollback both Keycloak and database changes on failure

### 2. Fetch Users

Retrieve users with comprehensive filtering and sorting options.

**Endpoint:** `GET /api/v1/users`

**Query Parameters:**
- `user_id` (UUID, optional): Filter by specific user ID
- `user_sk` (int, optional): Filter by specific user surrogate key
- `user_name` (string, optional): Filter by username
- `user_email` (string, optional): Filter by email
- `first_name` (string, optional): Filter by first name
- `last_name` (string, optional): Filter by last name
- `is_active` (bool, optional): Filter by active status
- `is_admin` (bool, optional): Filter by admin status
- `created_by` (UUID, optional): Filter by creator
- `effective_only` (bool, optional): Show only current versions (default: true)
- `sort` (string, optional): Sort specification (e.g., "-created_date")

**Examples:**

```bash
# Get all active users, newest first
GET /api/v1/users?is_active=true&sort=-created_date

# Get admin users only
GET /api/v1/users?is_admin=true

# Search users by name
GET /api/v1/users?first_name=John&last_name=Doe

# Get all versions of a specific user
GET /api/v1/users?user_id=123e4567-e89b-12d3-a456-426614174000&effective_only=false
```

**Response:**
```json
[
  {
    "user_sk": 123,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_name": "john.doe",
    "user_email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_admin": false,
    "effective_from": "2024-01-15T10:30:00Z",
    "effective_to": null,
    "created_by": "admin-user-uuid",
    "created_date": "2024-01-15T10:30:00Z"
  }
]
```

### 3. Update User

Modify user information with automatic Keycloak synchronization.

**Endpoint:** `PUT /api/v1/users`

**Request Body:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "Jonathan",
  "last_name": "Doe",
  "is_active": true,
  "is_admin": true
}
```

**Response:**
```json
{
  "user_sk": 125,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_name": "john.doe",
  "user_email": "john.doe@example.com",
  "first_name": "Jonathan",
  "last_name": "Doe",
  "is_active": true,
  "is_admin": true,
  "effective_from": "2024-01-15T11:00:00Z",
  "effective_to": null,
  "created_by": "admin-user-uuid",
  "created_date": "2024-01-15T10:30:00Z"
}
```

**Update Process:**
1. **Validation**: Verify user exists and is accessible
2. **Keycloak Update**: Update user fields in Keycloak
3. **Role Management**: Add/remove `SAARANSH_ADMIN` role as needed
4. **Version Control**: Close current version and create new one
5. **Rollback Handling**: Revert Keycloak changes if database update fails

## User Creation Workflow

### Detailed Process Flow

```python
async def create_user_workflow(user_request: UserCreateRequest):
    keycloak_user_id = None
    
    try:
        # 1. Generate username from email
        user_name = get_username_from_email(user_request.user_email)
        
        # 2. Create Keycloak user
        kc_user = KeycloakCreateUser(
            username=user_name,
            email=user_request.user_email,
            firstName=user_request.first_name,
            lastName=user_request.last_name,
            enabled=user_request.is_active,
        )
        
        keycloak_user_id = await keycloak_accessor.create_user(kc_user, user_request.is_admin)
        
        # 3. Create local database record
        model = User(
            user_id=keycloak_user_id,  # Use Keycloak UUID
            user_name=user_name,
            user_email=user_request.user_email,
            first_name=user_request.first_name,
            last_name=user_request.last_name,
            is_admin=user_request.is_admin,
            is_active=user_request.is_active,
            effective_from=datetime.now(timezone.utc),
            created_by=admin_user_id,
        )
        
        db_user = await user_accessor.insert_commit(model, session)
        return UserResponse.model_validate(db_user)
        
    except Exception as e:
        # 4. Cleanup on failure
        await session.rollback()
        
        if keycloak_user_id:
            try:
                await keycloak_accessor.delete_user(keycloak_user_id)
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup Keycloak user: {cleanup_error}")
        
        return UserResponse(
            user_email=user_request.user_email,
            first_name=user_request.first_name,
            last_name=user_request.last_name,
            is_admin=user_request.is_admin,
            error=str(e)
        )
```

### Bulk Operation Benefits

1. **Atomic Operations**: Each user creation is independent
2. **Partial Success Handling**: Continue processing even if some users fail
3. **Comprehensive Cleanup**: Automatic rollback of failed operations
4. **Detailed Error Reporting**: Individual error messages for each failure

## User Update Workflow

### Synchronization Process

```python
async def update_user_workflow(user_request: UserEditRequest):
    # 1. Get current user state
    existing_user = await get_current_user(user_request.user_id)
    
    # 2. Update Keycloak first
    kc_update = KeycloakEditUser(
        firstName=user_request.first_name,
        lastName=user_request.last_name,
        enabled=user_request.is_active,
    )
    
    await keycloak_accessor.update_user_fields(user_request.user_id, kc_update)
    
    # 3. Handle role changes
    if user_request.is_admin != existing_user.is_admin:
        if user_request.is_admin:
            await keycloak_accessor.assign_realm_role(user_request.user_id, "SAARANSH_ADMIN")
        else:
            await keycloak_accessor.remove_realm_role(user_request.user_id, "SAARANSH_ADMIN")
    
    # 4. Update local database with version control
    await user_accessor.close_active_record(user_request.user_id, session)
    
    new_user = User(
        user_id=user_request.user_id,
        user_name=existing_user.user_name,
        user_email=existing_user.user_email,
        first_name=user_request.first_name or existing_user.first_name,
        last_name=user_request.last_name or existing_user.last_name,
        is_admin=user_request.is_admin,
        is_active=user_request.is_active,
        effective_from=datetime.now(timezone.utc),
        created_by=existing_user.created_by,
        modified_by=current_admin_id,
    )
    
    updated_user = await user_accessor.insert_flush(new_user, session)
    await session.commit()
    
    return UserResponse.model_validate(updated_user)
```

## Data Models

### User Model

```json
{
  "user_sk": "integer (primary key, auto-increment)",
  "user_id": "uuid (business key, from Keycloak)",
  "user_name": "string (generated from email)",
  "user_email": "string (unique identifier)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "is_active": "boolean (account status)",
  "is_admin": "boolean (admin privileges)",
  "entity_type_id": "integer (default: 0)",
  "created_by": "uuid (admin who created user)",
  "created_date": "datetime (creation timestamp)",
  "modified_by": "uuid (admin who last modified)",
  "effective_from": "datetime (SCD2 start)",
  "effective_to": "datetime (SCD2 end, null for current)"
}
```

### Request Models

#### UserCreateRequest
```json
{
  "user_email": "string (required, unique)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "is_active": "boolean (default: true)",
  "is_admin": "boolean (default: false)"
}
```

#### UserEditRequest
```json
{
  "user_id": "uuid (required)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "is_active": "boolean (required)",
  "is_admin": "boolean (required)"
}
```

### Response Models

#### BulkUserCreateResponse
```json
{
  "success": "boolean (true if all users created successfully)",
  "partial": "boolean (true if some succeeded, some failed)",
  "results": [
    {
      "user_sk": "integer (null if failed)",
      "user_id": "uuid (null if failed)",
      "user_name": "string",
      "user_email": "string",
      "first_name": "string",
      "last_name": "string",
      "is_active": "boolean",
      "is_admin": "boolean",
      "effective_from": "datetime (null if failed)",
      "created_by": "uuid (null if failed)",
      "created_date": "datetime (null if failed)",
      "error": "string (null if successful)"
    }
  ]
}
```

## Version Control (SCD2)

### User History Tracking

All user changes are tracked using Slowly Changing Dimensions Type 2:

- **Current Record**: `effective_to = NULL`
- **Historical Records**: `effective_to = timestamp`
- **Version Chain**: Same `user_id`, different `user_sk`

### Version Management Example

```sql
-- Current user record
SELECT * FROM users 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000' 
  AND effective_to IS NULL;

-- Complete user history
SELECT * FROM users 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000' 
ORDER BY effective_from DESC;

-- User state at specific time
SELECT * FROM users 
WHERE user_id = '123e4567-e89b-12d3-a456-426614174000' 
  AND effective_from <= '2024-01-15T12:00:00Z'
  AND (effective_to IS NULL OR effective_to > '2024-01-15T12:00:00Z');
```

## Keycloak Integration

### User Synchronization

The system maintains synchronization between Keycloak and the local database:

#### Keycloak User Creation
```json
{
  "username": "john.doe",
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "enabled": true,
  "emailVerified": false
}
```

#### Role Management
```python
# Assign admin role
await keycloak_accessor.assign_realm_role(user_id, "SAARANSH_ADMIN")

# Remove admin role
await keycloak_accessor.remove_realm_role(user_id, "SAARANSH_ADMIN")
```

### Error Handling and Rollback

```python
async def handle_keycloak_failure(user_id: UUID, original_state: dict):
    """Rollback Keycloak changes after database failure."""
    try:
        # Revert role changes
        if original_state["was_admin"] != current_state["is_admin"]:
            if original_state["was_admin"]:
                await keycloak_accessor.assign_realm_role(user_id, "SAARANSH_ADMIN")
            else:
                await keycloak_accessor.remove_realm_role(user_id, "SAARANSH_ADMIN")
        
        # Revert user fields
        revert_payload = KeycloakEditUser(
            firstName=original_state["first_name"],
            lastName=original_state["last_name"],
            enabled=original_state["is_active"],
        )
        await keycloak_accessor.update_user_fields(user_id, revert_payload)
        
    except Exception as revert_error:
        logger.error(f"CRITICAL: Failed to revert Keycloak after DB rollback: {revert_error}")
```

## Security and Access Control

### Admin-Only Operations

All user management operations require admin privileges:

```python
@router.post("/users")
async def create_users(
    requests: list[UserCreateRequest],
    context: SecurityContext = Depends(get_security_context),
):
    # Verify admin privileges
    if not context.is_admin():
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required for user management"
        )
    
    # Proceed with user creation
    builder = UserBuilder(session)
    return await builder.build_create_users(requests, context.user_id)
```

### Audit Trail

All user operations are logged with:
- **Who**: Admin user performing the operation
- **What**: Type of operation (create, update, deactivate)
- **When**: Timestamp of the operation
- **Details**: What changed (stored in version history)

## Error Handling

### Common Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `Invalid email format` | Email doesn't contain @ symbol |
| 400 | `Email already exists` | User with email already exists |
| 400 | `Bulk operation failed` | Some or all users failed to create |
| 401 | `Authentication required` | Missing or invalid token |
| 403 | `Admin privileges required` | Non-admin user attempting user management |
| 404 | `User not found` | User ID doesn't exist |
| 422 | `Validation error` | Invalid field values |
| 500 | `Keycloak service error` | Keycloak unavailable or error |
| 503 | `Service unavailable` | External service failure |

### Error Response Examples

```json
{
  "detail": "Admin privileges required for user management",
  "type": "insufficient_permissions"
}
```

```json
{
  "success": false,
  "partial": true,
  "results": [
    {
      "user_email": "duplicate@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_admin": false,
      "error": "Email already exists in Keycloak"
    }
  ]
}
```

## Usage Examples

### Complete User Management Workflow

```python
import httpx
import asyncio

async def user_management_workflow():
    admin_headers = {"Authorization": "Bearer admin-jwt-token"}
    base_url = "https://api.saaransh.com/api/v1/users"
    
    async with httpx.AsyncClient() as client:
        # 1. Create multiple users
        create_request = [
            {
                "user_email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_admin": False
            },
            {
                "user_email": "jane.admin@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "is_active": True,
                "is_admin": True
            }
        ]
        
        create_response = await client.post(
            base_url,
            json=create_request,
            headers=admin_headers
        )
        
        users_created = create_response.json()
        user_id = users_created["results"][0]["user_id"]
        
        # 2. Update user to admin
        update_request = {
            "user_id": user_id,
            "first_name": "Jonathan",
            "last_name": "Doe",
            "is_active": True,
            "is_admin": True
        }
        
        update_response = await client.put(
            base_url,
            json=update_request,
            headers=admin_headers
        )
        
        # 3. Fetch all admin users
        admin_users_response = await client.get(
            f"{base_url}?is_admin=true&sort=-created_date",
            headers=admin_headers
        )
        
        return {
            "created": users_created,
            "updated": update_response.json(),
            "admin_users": admin_users_response.json()
        }
```

### Bulk User Creation with Error Handling

```bash
# Create multiple users
curl -X POST "https://api.saaransh.com/api/v1/users" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "user_email": "user1@example.com",
      "first_name": "User",
      "last_name": "One",
      "is_active": true,
      "is_admin": false
    },
    {
      "user_email": "admin@example.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "is_admin": true
    }
  ]'

# Update user information
curl -X PUT "https://api.saaransh.com/api/v1/users" \
  -H "Authorization: Bearer admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "Updated",
    "last_name": "Name",
    "is_active": true,
    "is_admin": true
  }'

# Fetch users with filtering
curl -X GET "https://api.saaransh.com/api/v1/users?is_admin=true&is_active=true&sort=-created_date" \
  -H "Authorization: Bearer admin-token"
```

## Performance Considerations

### Optimization Strategies

1. **Batch Processing**: Process multiple users in parallel where possible
2. **Connection Pooling**: Reuse Keycloak connections for multiple operations
3. **Caching**: Cache user permissions and roles for frequently accessed data
4. **Indexing**: Proper database indexes on `user_id`, `user_email`, and `effective_to`

### Monitoring and Metrics

- **User Creation Rate**: Track successful vs failed user creations
- **Keycloak Response Times**: Monitor external service performance
- **Database Performance**: Track query execution times
- **Error Rates**: Monitor and alert on high failure rates

## Best Practices

### 1. User Creation
- Always validate email format before processing
- Use meaningful error messages for bulk operations
- Implement proper cleanup for failed operations
- Log all administrative actions for audit

### 2. Role Management
- Follow principle of least privilege
- Regularly audit admin user assignments
- Implement approval workflows for admin role changes
- Monitor admin user activities

### 3. Data Consistency
- Maintain synchronization between Keycloak and local database
- Implement proper rollback mechanisms
- Use transactions for multi-step operations
- Regular data consistency checks

### 4. Security
- Require strong authentication for admin operations
- Log all user management activities
- Implement rate limiting for bulk operations
- Regular security audits of user permissions