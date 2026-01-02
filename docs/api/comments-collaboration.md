# Comments and Collaboration API

## Overview

The Comments and Collaboration API enables multi-user collaboration on summaries through a comprehensive system of comments, sharing, and user interaction tracking. The system supports role-based access control, version-controlled comments, and detailed audit trails for all collaborative activities.

## Collaboration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Summary       │    │   Comments      │    │  User Prompts   │
│   (Content)     │◀──▶│   (Feedback)    │    │  (AI History)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Summaries Users                              │
│              (Sharing & Permissions)                            │
└─────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Comments**: Feedback and discussion on summaries
2. **Summaries Users**: Sharing and role-based permissions
3. **User Prompts**: AI interaction history and audit trail
4. **Version Control**: Complete history of all collaborative changes

## Role-Based Access Control

### User Roles

| Role | Value | Permissions |
|------|-------|-------------|
| `OWNER` | 0 | Full control: edit, share, delete, manage permissions |
| `EDITOR` | 1 | Edit content, add comments, view all versions |
| `VIEWER` | 2 | Read-only access, add comments |
| `ADMIN` | 3 | System-wide administrative privileges |

### Permission Matrix

| Action | Owner | Editor | Viewer | Admin |
|--------|-------|--------|--------|-------|
| View Summary | ✓ | ✓ | ✓ | ✓ |
| Edit Summary | ✓ | ✓ | ✗ | ✓ |
| Add Comments | ✓ | ✓ | ✓ | ✓ |
| Edit Own Comments | ✓ | ✓ | ✓ | ✓ |
| Delete Comments | ✓ | ✗ | ✗ | ✓ |
| Share Summary | ✓ | ✗ | ✗ | ✓ |
| Manage Permissions | ✓ | ✗ | ✗ | ✓ |
| View User Prompts | ✓ | ✓ | ✗ | ✓ |

## Comments API

### 1. Create Comment

Add a new comment to a summary.

**Endpoint:** `POST /api/v1/comments`

**Request Body:**
```json
{
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This section needs more detail about the technical challenges faced."
}
```

**Response:**
```json
{
  "comment_sk": 12345,
  "comment_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This section needs more detail about the technical challenges faced.",
  "is_active": true,
  "created_by": "user-uuid",
  "created_date": "2024-01-15T10:30:00Z",
  "effective_from": "2024-01-15T10:30:00Z",
  "effective_to": null
}
```

### 2. Edit Comment

Modify an existing comment (creates new version).

**Endpoint:** `PUT /api/v1/comments`

**Request Body:**
```json
{
  "comment_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",
  "content": "This section needs more detail about the technical challenges faced and how they were resolved."
}
```

**Response:**
```json
{
  "comment_sk": 12346,
  "comment_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "This section needs more detail about the technical challenges faced and how they were resolved.",
  "is_active": true,
  "created_by": "original-user-uuid",
  "created_date": "2024-01-15T10:30:00Z",
  "modified_by": "editing-user-uuid",
  "effective_from": "2024-01-15T11:00:00Z",
  "effective_to": null
}
```

### 3. Fetch Comments

Retrieve comments with filtering and sorting options.

**Endpoint:** `GET /api/v1/comments`

**Query Parameters:**
- `summary_id` (UUID, optional): Filter by summary
- `comment_id` (UUID, optional): Get specific comment
- `comment_sk` (int, optional): Get specific comment version
- `is_active` (bool, optional): Filter by active status
- `effective_only` (bool, optional): Show only current versions (default: true)
- `sort` (string, optional): Sort specification (e.g., "-created_date")

**Examples:**

```bash
# Get all comments for a summary, newest first
GET /api/v1/comments?summary_id=123e4567-e89b-12d3-a456-426614174000&sort=-created_date

# Get all versions of a specific comment
GET /api/v1/comments?comment_id=987fcdeb-51a2-43d7-8f9e-123456789abc&effective_only=false

# Get active comments only
GET /api/v1/comments?is_active=true&sort=created_date
```

**Response:**
```json
[
  {
    "comment_sk": 12346,
    "comment_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "This section needs more detail about the technical challenges faced and how they were resolved.",
    "is_active": true,
    "created_by": "original-user-uuid",
    "created_date": "2024-01-15T10:30:00Z",
    "modified_by": "editing-user-uuid",
    "effective_from": "2024-01-15T11:00:00Z",
    "effective_to": null
  }
]
```

## Summary Sharing API

### 1. Share Summary

Grant access to a summary with specific role permissions.

**Endpoint:** `POST /api/v1/share`

**Request Body:**
```json
{
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-f12b-34c5-d678-901234567890",
  "role_id": 1
}
```

**Response:**
```json
{
  "summaries_users_sk": 789,
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "456e7890-f12b-34c5-d678-901234567890",
  "role_id": 1,
  "reviewed": false,
  "is_active": true,
  "created_by": "owner-user-uuid",
  "created_date": "2024-01-15T12:00:00Z"
}
```

### 2. Fetch Shared Summaries (Minimal)

Get basic sharing information.

**Endpoint:** `GET /api/v1/share/minimal`

**Query Parameters:**
- `summary_id` (UUID, optional): Filter by summary
- `user_id` (UUID, optional): Filter by user
- `role_id` (int, optional): Filter by role
- `reviewed` (bool, optional): Filter by review status
- `is_active` (bool, optional): Filter by active status
- `sort` (string, optional): Sort specification

**Response:**
```json
[
  {
    "summaries_users_sk": 789,
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "456e7890-f12b-34c5-d678-901234567890",
    "role_id": 1,
    "reviewed": false,
    "is_active": true,
    "created_by": "owner-user-uuid",
    "created_date": "2024-01-15T12:00:00Z"
  }
]
```

### 3. Fetch Shared Summaries (Full)

Get complete sharing information with user and summary details.

**Endpoint:** `GET /api/v1/share`

**Response:**
```json
[
  {
    "summaries_users_sk": 789,
    "role_id": 1,
    "reviewed": false,
    "is_active": true,
    "created_by": "owner-user-uuid",
    "created_date": "2024-01-15T12:00:00Z",
    "user": {
      "user_sk": 456,
      "user_id": "456e7890-f12b-34c5-d678-901234567890",
      "user_name": "jane.doe",
      "user_email": "jane.doe@example.com",
      "first_name": "Jane",
      "last_name": "Doe",
      "is_admin": false,
      "is_active": true
    },
    "summary": {
      "summary_sk": 12346,
      "summary_id": "123e4567-e89b-12d3-a456-426614174000",
      "start_date": null,
      "end_date": null,
      "status_id": 1,
      "meta_data": {
        "model": "gemini/gemini-2.5-flash"
      },
      "is_active": true,
      "created_date": "2024-01-15T10:30:00Z",
      "created_by": "owner-user-uuid",
      "effective_from": "2024-01-15T11:00:00Z",
      "effective_to": null
    }
  }
]
```

## User Prompts API

Track AI interaction history for audit and analysis purposes.

### 1. Create User Prompt

Record a user's AI interaction prompt.

**Endpoint:** `POST /api/v1/userprompts`

**Request Body:**
```json
{
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "content": "Add more details about the technical challenges and how they were resolved"
}
```

**Response:**
```json
{
  "user_prompt_sk": 567,
  "content": "Add more details about the technical challenges and how they were resolved",
  "summary_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_active": true,
  "created_by": "user-uuid",
  "created_date": "2024-01-15T13:00:00Z"
}
```

### 2. Fetch User Prompts

Retrieve AI interaction history.

**Endpoint:** `GET /api/v1/userprompts`

**Query Parameters:**
- `summary_id` (UUID, optional): Filter by summary
- `user_prompt_sk` (int, optional): Get specific prompt
- `is_active` (bool, optional): Filter by active status
- `sort` (string, optional): Sort specification

**Response:**
```json
[
  {
    "user_prompt_sk": 567,
    "content": "Add more details about the technical challenges and how they were resolved",
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "is_active": true,
    "created_by": "user-uuid",
    "created_date": "2024-01-15T13:00:00Z"
  }
]
```

## Collaboration Workflows

### 1. Summary Sharing Workflow

```python
async def share_summary_workflow():
    headers = {"Authorization": "Bearer owner-jwt-token"}
    base_url = "https://api.saaransh.com/api/v1"
    
    # 1. Owner shares summary with editor
    share_request = {
        "summary_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "456e7890-f12b-34c5-d678-901234567890",
        "role_id": 1  # EDITOR role
    }
    
    async with httpx.AsyncClient() as client:
        share_response = await client.post(
            f"{base_url}/share",
            json=share_request,
            headers=headers
        )
        
        # 2. Editor adds comment
        editor_headers = {"Authorization": "Bearer editor-jwt-token"}
        comment_request = {
            "summary_id": "123e4567-e89b-12d3-a456-426614174000",
            "content": "Great work! Consider adding metrics to quantify the impact."
        }
        
        comment_response = await client.post(
            f"{base_url}/comments",
            json=comment_request,
            headers=editor_headers
        )
        
        # 3. Editor makes AI-assisted edit
        edit_request = {
            "summary_id": "123e4567-e89b-12d3-a456-426614174000",
            "user_prompt": "Add specific metrics and quantified results",
            "staging": False
        }
        
        edit_response = await client.put(
            f"{base_url}/summaries/edit",
            json=edit_request,
            headers=editor_headers
        )
        
        return {
            "shared": share_response.json(),
            "comment": comment_response.json(),
            "edited_summary": edit_response.json()
        }
```

### 2. Comment Thread Workflow

```python
async def comment_thread_workflow():
    headers = {"Authorization": "Bearer user-jwt-token"}
    base_url = "https://api.saaransh.com/api/v1/comments"
    
    async with httpx.AsyncClient() as client:
        # 1. Create initial comment
        initial_comment = {
            "summary_id": "123e4567-e89b-12d3-a456-426614174000",
            "content": "This section could use more detail."
        }
        
        comment_response = await client.post(
            base_url,
            json=initial_comment,
            headers=headers
        )
        comment_id = comment_response.json()["comment_id"]
        
        # 2. Edit comment to add more context
        edit_comment = {
            "comment_id": comment_id,
            "content": "This section could use more detail about the specific technical challenges and solutions implemented."
        }
        
        edit_response = await client.put(
            base_url,
            json=edit_comment,
            headers=headers
        )
        
        # 3. Fetch comment history
        history_response = await client.get(
            f"{base_url}?comment_id={comment_id}&effective_only=false",
            headers=headers
        )
        
        return {
            "original": comment_response.json(),
            "edited": edit_response.json(),
            "history": history_response.json()
        }
```

## Data Models

### Comment Model

```json
{
  "comment_sk": "integer (primary key)",
  "comment_id": "uuid (business key)",
  "summary_id": "uuid (foreign key)",
  "content": "string (comment text)",
  "is_active": "boolean",
  "created_by": "uuid (user who created)",
  "created_date": "datetime",
  "modified_by": "uuid (user who last modified)",
  "effective_from": "datetime (SCD2 start)",
  "effective_to": "datetime (SCD2 end, null for current)"
}
```

### Summaries Users Model

```json
{
  "summaries_users_sk": "integer (primary key)",
  "summary_id": "uuid (foreign key)",
  "user_id": "uuid (foreign key)",
  "role_id": "integer (0=OWNER, 1=EDITOR, 2=VIEWER, 3=ADMIN)",
  "reviewed": "boolean (has user reviewed the summary)",
  "is_active": "boolean",
  "created_by": "uuid (user who shared)",
  "created_date": "datetime"
}
```

### User Prompt Model

```json
{
  "user_prompt_sk": "integer (primary key)",
  "content": "string (prompt text)",
  "summary_id": "uuid (foreign key)",
  "meta_data": "object (additional metadata)",
  "is_active": "boolean",
  "created_by": "uuid (user who created prompt)",
  "created_date": "datetime"
}
```

## Version Control Features

### Comment Versioning (SCD2)

Comments use Slowly Changing Dimensions Type 2 for complete edit history:

- **Current Version**: `effective_to = NULL`
- **Historical Versions**: `effective_to = timestamp`
- **Edit Chain**: Same `comment_id`, different `comment_sk`

### Version Tracking

```python
# When editing a comment:
# 1. Close current version
await self.comments_accessor.close_active_record(comment_id, session)

# 2. Create new version
new_comment = Comment(
    comment_id=comment_id,  # Same business key
    summary_id=old_record.summary_id,
    content=new_content,
    created_by=old_record.created_by,
    modified_by=current_user,
    effective_from=datetime.now(timezone.utc),
    effective_to=None  # New active version
)
```

## Security and Permissions

### Access Control Implementation

```python
async def check_summary_access(user_id: UUID, summary_id: UUID, required_role: int):
    # Check if user has access to summary
    access_query = select(SummariesUsers).where(
        SummariesUsers.summary_id == summary_id,
        SummariesUsers.user_id == user_id,
        SummariesUsers.is_active == True
    )
    
    access_record = await session.execute(access_query)
    user_access = access_record.scalars().first()
    
    if not user_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_access.role_id > required_role:  # Higher number = less permissions
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return user_access
```

### Permission Validation

- **Comments**: Users can comment if they have any access to the summary
- **Editing**: Only OWNER and EDITOR roles can modify summaries
- **Sharing**: Only OWNER and ADMIN roles can share summaries
- **User Prompts**: Tracked for all users with access

## Error Handling

### Common Errors

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `Invalid request data` | Malformed request body |
| 401 | `Authentication required` | Missing or invalid token |
| 403 | `Access denied` | User lacks access to summary |
| 403 | `Insufficient permissions` | User role insufficient for action |
| 404 | `Comment not found` | Comment ID doesn't exist |
| 404 | `Summary not found` | Summary ID doesn't exist |
| 404 | `User not found` | User ID doesn't exist |
| 422 | `Validation error` | Invalid field values |

### Error Response Examples

```json
{
  "detail": "Access denied to summary 123e4567-e89b-12d3-a456-426614174000",
  "type": "access_denied"
}
```

```json
{
  "detail": "Insufficient permissions. Required role: EDITOR or higher",
  "type": "insufficient_permissions"
}
```

## Usage Examples

### Complete Collaboration Example

```bash
# 1. Share summary with editor
curl -X POST "https://api.saaransh.com/api/v1/share" \
  -H "Authorization: Bearer owner-token" \
  -H "Content-Type: application/json" \
  -d '{
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "456e7890-f12b-34c5-d678-901234567890",
    "role_id": 1
  }'

# 2. Editor adds comment
curl -X POST "https://api.saaransh.com/api/v1/comments" \
  -H "Authorization: Bearer editor-token" \
  -H "Content-Type: application/json" \
  -d '{
    "summary_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "Consider adding more quantified results"
  }'

# 3. Get all comments for summary
curl -X GET "https://api.saaransh.com/api/v1/comments?summary_id=123e4567-e89b-12d3-a456-426614174000&sort=-created_date" \
  -H "Authorization: Bearer user-token"

# 4. Get sharing information
curl -X GET "https://api.saaransh.com/api/v1/share?summary_id=123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer owner-token"
```

## Performance Considerations

### Optimization Strategies

1. **Indexing**: Proper indexes on `summary_id`, `user_id`, and `comment_id`
2. **Pagination**: Use sorting and limiting for large comment threads
3. **Caching**: Cache user permissions for frequently accessed summaries
4. **Batch Operations**: Group related operations in single transactions

### Query Optimization

```sql
-- Optimized query for user's accessible summaries
SELECT s.*, su.role_id 
FROM summaries s
JOIN summaries_users su ON s.summary_id = su.summary_id
WHERE su.user_id = $1 
  AND su.is_active = true 
  AND s.effective_to IS NULL
ORDER BY s.created_date DESC;
```

## Best Practices

### 1. Permission Management
- Always validate user permissions before operations
- Use role hierarchy for flexible access control
- Audit permission changes for security

### 2. Comment Threading
- Implement proper sorting for chronological order
- Consider comment nesting for complex discussions
- Provide clear edit history for transparency

### 3. Version Control
- Preserve complete edit history for audit trails
- Implement soft deletes for data integrity
- Use effective dating for point-in-time queries

### 4. User Experience
- Provide real-time notifications for new comments
- Implement comment mentions and notifications
- Show clear indicators for edited content