# Asana Integration Architecture Documentation

## Overview

This document provides comprehensive documentation for the Asana integration in the Saaransh backend, including architecture, implementation steps, API endpoints, and usage patterns.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Structure](#component-structure)
3. [Implementation Steps](#implementation-steps)
4. [API Endpoints](#api-endpoints)
5. [Data Flow](#data-flow)
6. [GID Hierarchy System](#gid-hierarchy-system)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)

## Architecture Overview

The Asana integration follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Controllers                      │
│              (asana_integration_controllers.py)            │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                            │
│                 (asana_accessor.py)                         │
├─────────────────────────────────────────────────────────────┤
│                  Pipeline Layer                             │
│              (asana_nirdesh_pipeline.py)                    │
├─────────────────────────────────────────────────────────────┤
│                   Asana REST API                            │
│              (https://app.asana.com/api/1.0)               │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Dependency Injection**: Components are loosely coupled through the pipeline
3. **Error Isolation**: Failures in Asana don't crash the main application
4. **Configuration-Driven**: Integration can be enabled/disabled via environment variables
5. **RESTful Design**: API endpoints follow REST conventions

## Component Structure

### 1. Pipeline Layer (`asana_nirdesh_pipeline.py`)

**Purpose**: Factory pattern for creating and managing Asana accessor instances

```python
def get_asana_accessor():
    """Return AsanaAccessor if enabled, None otherwise"""
    
    # Check if Asana integration is enabled
    if not os.getenv("ENABLE_ASANA", "false").lower() == "true":
        return None
    
    try:
        from app.accessors.asana_accessor import AsanaAccessor
        accessor = AsanaAccessor()
        return accessor
    except Exception as e:
        logger.error(f"Failed to initialize Asana accessor: {e}")
        return None
```

**Key Features**:
- Environment-based enablement
- Graceful failure handling
- Singleton-like behavior
- Import isolation

### 2. Service Layer (`asana_accessor.py`)

**Purpose**: Core business logic for Asana API interactions

```python
class AsanaAccessor:
    """Asana REST API accessor"""
    
    def __init__(self):
        self.access_token = os.getenv("ASANA_ACCESS_TOKEN", "")
        self.base_url = "https://app.asana.com/api/1.0"
        self.session = requests.Session()
```

**Key Methods**:
- `get_current_user()`: Authentication and user info
- `get_workspaces()`: User's accessible workspaces
- `get_projects(workspace_gid)`: Projects in workspace
- `get_tasks_for_user(user_gid, workspace_gid)`: User tasks
- `get_task_stories(task_gid)`: Task comments/activities
- `get_user_data_for_report(user_email)`: Comprehensive data aggregation

**Features**:
- Async/await pattern for non-blocking operations
- HTTP session reuse for performance
- Comprehensive error handling
- Bearer token authentication

### 3. Controller Layer (`asana_integration_controllers.py`)

**Purpose**: FastAPI endpoints exposing Asana functionality

**Simplified Endpoint Design**:
- 4 core endpoints covering all use cases
- RESTful URL patterns
- Consistent response formats
- Proper HTTP status codes

## Implementation Steps

### Step 1: Environment Configuration

Create or update `.env` file:

```bash
# Enable Asana Integration
ENABLE_ASANA=true

# Asana API Configuration
ASANA_ACCESS_TOKEN=your_personal_access_token_here
```

### Step 2: Dependency Installation

Add to `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies
    "asana>=5.2.2",
]
```

Install dependencies:

```bash
uv sync
```

### Step 3: Pipeline Integration

The pipeline is already integrated in `asana_nirdesh_pipeline.py` and provides:

- Conditional initialization based on `ENABLE_ASANA`
- Error handling and logging
- Graceful degradation if Asana is unavailable

### Step 4: Service Implementation

The `AsanaAccessor` class provides:

- REST API client setup
- Async method implementations
- Data aggregation for reports
- Health checking capabilities

### Step 5: Controller Registration

Controllers are registered in `main.py`:

```python
from app.accessors.asana_integration_controllers import router as integration_router

protected_router.include_router(integration_router)
```

### Step 6: Testing and Validation

Use the built-in endpoints to validate:

1. `/api/v1/asana/status` - Health check
2. `/api/v1/asana/overview` - Full data test

## API Endpoints

### 1. Health Check Endpoint

```http
GET /api/v1/asana/status
```

**Response**:
```json
{
  "status": "healthy",
  "message": "Connection successful",
  "enabled": true,
  "user_name": "Chaitanya"
}
```

**Use Cases**:
- System health monitoring
- Integration status verification
- Quick connectivity test

### 2. Complete Overview Endpoint

```http
GET /api/v1/asana/overview
```

**Response Structure**:
```json
{
  "user": {
    "gid": "1212000333310446",
    "name": "Chaitanya",
    "email": "chaitanya.krishna@icloudlogic.com"
  },
  "workspaces": [
    {
      "gid": "1205513962325788",
      "name": "icloudlogic.com"
    }
  ],
  "projects": [
    {
      "gid": "1212000280291519",
      "name": "integrating asana to db",
      "workspace_name": "icloudlogic.com",
      "workspace_gid": "1205513962325788"
    }
  ],
  "tasks": [
    {
      "gid": "1212000280291534",
      "name": "Draft project brief",
      "workspace_name": "icloudlogic.com",
      "workspace_gid": "1205513962325788"
    }
  ],
  "summary": {
    "total_workspaces": 1,
    "total_projects": 1,
    "total_tasks": 3,
    "completed_tasks": 0
  }
}
```

**Use Cases**:
- Dashboard data loading
- Complete user context
- Report generation
- Initial data synchronization

### 3. Workspace-Specific Endpoint

```http
GET /api/v1/asana/workspace/{workspace_gid}
```

**Response Structure**:
```json
{
  "workspace": {
    "gid": "1205513962325788",
    "name": "icloudlogic.com"
  },
  "projects": [...],
  "tasks": [...],
  "summary": {
    "total_projects": 1,
    "total_tasks": 3,
    "completed_tasks": 0,
    "overdue_tasks": 0
  }
}
```

**Use Cases**:
- Workspace-focused views
- Team-specific data
- Filtered project management

### 4. Task Details Endpoint

```http
GET /api/v1/asana/task/{task_gid}?include_stories=true
```

**Response Structure**:
```json
{
  "task_gid": "1212000280291534",
  "stories": [
    {
      "gid": "1212000336269036",
      "text": "Chaitanya added this task to integrating asana to db",
      "type": "system",
      "created_at": "2025-11-20T03:28:47.692Z"
    }
  ],
  "stories_count": 3
}
```

**Use Cases**:
- Task detail views
- Comment/activity tracking
- Audit trails

## Data Flow

### 1. Authentication Flow

```
Client Request → Controller → Pipeline → Accessor → Asana API
                                      ↓
Environment Check ← Token Validation ← Bearer Auth
```

### 2. Data Retrieval Flow

```
1. Client calls /asana/overview
2. Controller validates Asana integration
3. Accessor gets current user (authentication)
4. Accessor gets workspaces for user
5. For each workspace:
   - Get projects in workspace
   - Get tasks for user in workspace
6. Aggregate and enrich data
7. Return structured response
```

### 3. Error Handling Flow

```
API Error → Accessor Logging → Graceful Degradation → Client Response
    ↓
Exception Handling → Error Response → HTTP Status Code
```

## GID Hierarchy System

Asana uses Global IDs (GIDs) to create a hierarchical data structure:

### Hierarchy Levels

```
User GID (Root)
├── Workspace GID 1
│   ├── Project GID 1.1
│   ├── Project GID 1.2
│   └── Task GID 1.x (assigned to user)
├── Workspace GID 2
│   ├── Project GID 2.1
│   └── Task GID 2.x (assigned to user)
└── Task GID (any workspace)
    ├── Story GID 1
    ├── Story GID 2
    └── Story GID N
```

### Dynamic Querying Pattern

1. **User Authentication**: Get user GID from token
2. **Workspace Discovery**: User GID → Available workspaces
3. **Project Enumeration**: Workspace GID → Projects in workspace
4. **Task Assignment**: User GID + Workspace GID → User's tasks
5. **Activity Tracking**: Task GID → Stories/comments

### GID Usage Examples

```python
# Get user's workspaces
user_gid = "1212000333310446"
workspaces = await accessor.get_workspaces()

# Get projects in specific workspace
workspace_gid = "1205513962325788"
projects = await accessor.get_projects(workspace_gid)

# Get user's tasks in workspace
tasks = await accessor.get_tasks_for_user(user_gid, workspace_gid)

# Get task activities
task_gid = "1212000280291534"
stories = await accessor.get_task_stories(task_gid)
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_ASANA` | Yes | `false` | Enable/disable Asana integration |
| `ASANA_ACCESS_TOKEN` | Yes | - | Personal Access Token from Asana |

### Asana Access Token Setup

1. Go to [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Click "Create New Token"
3. Enter token name (e.g., "Saaransh Integration")
4. Copy the generated token
5. Add to `.env` file

### Security Considerations

- Store tokens in environment variables, never in code
- Use `.env` files for development
- Use secure secret management in production
- Tokens are user-specific and inherit user permissions
- Consider token rotation policies

## Usage Examples

### Basic Health Check

```python
import requests

response = requests.get("http://localhost:8000/api/v1/asana/status")
if response.json()["status"] == "healthy":
    print("Asana integration is working!")
```

### Get Complete User Data

```python
import requests

response = requests.get("http://localhost:8000/api/v1/asana/overview")
data = response.json()

print(f"User: {data['user']['name']}")
print(f"Workspaces: {data['summary']['total_workspaces']}")
print(f"Projects: {data['summary']['total_projects']}")
print(f"Tasks: {data['summary']['total_tasks']}")
```

### Workspace-Specific Data

```python
import requests

workspace_gid = "1205513962325788"
response = requests.get(f"http://localhost:8000/api/v1/asana/workspace/{workspace_gid}")
data = response.json()

print(f"Workspace: {data['workspace']['name']}")
for project in data['projects']:
    print(f"  Project: {project['name']}")
```

### Task Details with Comments

```python
import requests

task_gid = "1212000280291534"
response = requests.get(f"http://localhost:8000/api/v1/asana/task/{task_gid}")
data = response.json()

print(f"Task has {data['stories_count']} activities:")
for story in data['stories']:
    print(f"  {story['type']}: {story['text']}")
```

## Error Handling

### Error Types and Responses

1. **Integration Disabled**
   ```json
   {
     "status": "disabled",
     "message": "Asana integration not enabled",
     "enabled": false
   }
   ```

2. **Authentication Error**
   ```json
   {
     "detail": "Asana integration not enabled",
     "status_code": 503
   }
   ```

3. **API Error**
   ```json
   {
     "detail": "Failed to fetch workspaces: Invalid token",
     "status_code": 500
   }
   ```

4. **Not Found Error**
   ```json
   {
     "detail": "Workspace not found",
     "status_code": 404
   }
   ```

### Error Handling Strategy

1. **Graceful Degradation**: App continues working without Asana
2. **Detailed Logging**: All errors logged for debugging
3. **User-Friendly Messages**: Clear error descriptions
4. **Proper HTTP Status**: Correct status codes for different errors

## Performance Considerations

### Optimization Strategies

1. **HTTP Session Reuse**: Single session for all API calls
2. **Async Operations**: Non-blocking API calls
3. **Data Aggregation**: Minimize API calls by batching
4. **Error Caching**: Avoid repeated failed calls

### Rate Limiting

- Asana API: 150 requests per minute per token
- Implementation handles rate limits gracefully
- Consider caching for frequently accessed data

### Response Times

- Health check: ~100ms
- Overview (full data): ~2-5 seconds (depends on data volume)
- Workspace data: ~1-3 seconds
- Task details: ~200-500ms

### Scalability Considerations

1. **Token Management**: Consider OAuth for multi-user scenarios
2. **Caching Strategy**: Implement Redis for frequently accessed data
3. **Background Jobs**: Use Celery for large data synchronization
4. **Database Storage**: Consider storing Asana data locally for performance

## Troubleshooting

### Common Issues

1. **"Asana integration not enabled"**
   - Check `ENABLE_ASANA=true` in `.env`
   - Restart the server after changes

2. **"Failed to get current user"**
   - Verify `ASANA_ACCESS_TOKEN` is correct
   - Check token hasn't expired
   - Ensure token has proper permissions

3. **"No workspaces found"**
   - User may not have access to any workspaces
   - Check Asana account permissions

4. **Rate limit errors**
   - Implement exponential backoff
   - Consider caching strategies
   - Reduce API call frequency

### Debug Endpoints

Use the status endpoint for debugging:

```bash
curl -X GET "http://localhost:8000/api/v1/asana/status"
```

### Logging

Enable debug logging in `.env`:

```bash
LOG_LEVEL=DEBUG
```

Check logs for detailed error information and API call traces.

## Future Enhancements

### Planned Features

1. **Webhook Support**: Real-time updates from Asana
2. **Data Caching**: Redis-based caching for performance
3. **Bulk Operations**: Batch API calls for large datasets
4. **OAuth Integration**: Multi-user token management
5. **Custom Fields**: Support for Asana custom fields
6. **Advanced Filtering**: Query parameters for data filtering

### Integration Opportunities

1. **LLM Context**: Use Asana data in AI prompts
2. **Report Generation**: Automated project reports
3. **Dashboard Widgets**: Real-time Asana metrics
4. **Notification System**: Task deadline alerts
5. **Analytics**: Project performance insights

---

*This documentation is maintained alongside the codebase and should be updated when the integration evolves.*