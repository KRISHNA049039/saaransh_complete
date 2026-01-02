# External Integrations Architecture

## Overview

Saaransh Backend implements a flexible integration architecture that connects with external project management and collaboration tools. The system currently supports Asana and Nirdesh integrations, providing unified access to project data, tasks, and user activities for comprehensive summary generation.

## Integration Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Integration   │    │   Integration   │    │   Data          │
│   Controllers   │───▶│   Accessors     │───▶│   Formatters    │
│   (API Layer)   │    │   (Data Access) │    │   (LLM Ready)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Health Check  │    │   Pipeline      │    │   Summary       │
│   & Status      │    │   Management    │    │   Generation    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │    │   Configuration │    │   User Data     │
│   APIs          │    │   Management    │    │   Aggregation   │
│ (Asana, Nirdesh)│    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

1. **Multi-Platform Support**: Unified interface for different project management tools
2. **Conditional Loading**: Integrations enabled/disabled via environment configuration
3. **Health Monitoring**: Real-time status checking and error handling
4. **Data Formatting**: Transform external data for AI consumption
5. **Async Operations**: Non-blocking API calls with proper error handling
6. **Graceful Degradation**: System continues to function when integrations are unavailable

## Asana Integration

### Configuration

```python
# Environment variables
ENABLE_ASANA = "true"  # Enable/disable Asana integration
ASANA_ACCESS_TOKEN = "2/1212000333310446/1212371107783289:00bf8b93d27be1eb951707d09509979f"
```

### Asana Accessor Implementation

```python
class AsanaAccessor:
    """Asana REST API accessor"""
    
    def __init__(self):
        """Initialize Asana client using REST API"""
        self.access_token = os.getenv("ASANA_ACCESS_TOKEN", "")
        self.base_url = "https://app.asana.com/api/1.0"
        
        if not self.access_token:
            logger.warning("ASANA_ACCESS_TOKEN not provided - Asana integration disabled")
            self.client = None
            return
        
        try:
            # Set up headers for API requests
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Create a session for connection pooling
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            
            # Mark as initialized
            self.client = self.session
            
            logger.info("Initialized Asana REST API client")
            
        except Exception as e:
            logger.error(f"Failed to initialize Asana client: {e}")
            self.client = None
```

### Core API Methods

#### User Information
```python
async def get_current_user(self) -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    if not self.client:
        return None
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            self.session.get, 
            f"{self.base_url}/users/me"
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data")
        else:
            logger.error(f"Failed to get current user: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        return None
```

#### Workspace Management
```python
async def get_workspaces(self) -> List[Dict[str, Any]]:
    """Get all workspaces"""
    if not self.client:
        return []
    
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            self.session.get, 
            f"{self.base_url}/workspaces"
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            logger.error(f"Failed to get workspaces: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get workspaces: {e}")
        return []
```

#### Project Data
```python
async def get_projects(self, workspace_gid: str) -> List[Dict[str, Any]]:
    """Get projects in workspace"""
    if not self.client:
        return []
    
    try:
        params = {
            'workspace': workspace_gid,
            'opt_fields': 'name,notes,due_date,completed,created_at,modified_at,owner'
        }
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: self.session.get(f"{self.base_url}/projects", params=params)
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            logger.error(f"Failed to get projects: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        return []
```

#### Task Management
```python
async def get_tasks_for_user(self, user_gid: str, workspace_gid: str) -> List[Dict[str, Any]]:
    """Get tasks assigned to user"""
    if not self.client:
        return []
    
    try:
        params = {
            'assignee': user_gid,
            'workspace': workspace_gid,
            'completed_since': 'now',
            'opt_fields': 'name,notes,completed,completed_at,due_date,created_at,modified_at,projects,tags'
        }
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.session.get(f"{self.base_url}/tasks", params=params)
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            logger.error(f"Failed to get tasks: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get tasks for user: {e}")
        return []
```

#### Task Comments and Stories
```python
async def get_task_stories(self, task_gid: str) -> List[Dict[str, Any]]:
    """Get task stories/comments"""
    if not self.client:
        return []
    
    try:
        params = {
            'opt_fields': 'text,type,created_at,created_by'
        }
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.session.get(f"{self.base_url}/tasks/{task_gid}/stories", params=params)
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            logger.error(f"Failed to get task stories: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Failed to get task stories: {e}")
        return []
```

### Comprehensive Data Aggregation

```python
async def get_user_data_for_report(self, user_email: str) -> Dict[str, Any]:
    """Get comprehensive user data for reports"""
    try:
        # Get current user (assuming authenticated user is the one we want)
        user = await self.get_current_user()
        if not user:
            return {"error": "Could not get user data"}
        
        user_gid = user["gid"]
        
        # Get workspaces
        workspaces = await self.get_workspaces()
        
        all_projects = []
        all_tasks = []
        
        for workspace in workspaces:
            workspace_gid = workspace["gid"]
            
            # Get projects
            projects = await self.get_projects(workspace_gid)
            all_projects.extend(projects)
            
            # Get tasks
            tasks = await self.get_tasks_for_user(user_gid, workspace_gid)
            
            # Enrich tasks with stories
            for task in tasks:
                task["stories"] = await self.get_task_stories(task["gid"])
            
            all_tasks.extend(tasks)
        
        return {
            "user_email": user_email,
            "user": user,
            "workspaces": workspaces,
            "projects": all_projects,
            "tasks": all_tasks,
            "total_projects": len(all_projects),
            "total_tasks": len(all_tasks)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user data: {e}")
        return {
            "user_email": user_email,
            "error": str(e),
            "projects": [],
            "tasks": [],
            "total_projects": 0,
            "total_tasks": 0
        }
```

## Data Formatting for AI

### Asana Data Formatter

```python
class AsanaDataFormatter:
    """Formats Asana data for LLM"""
    
    @staticmethod
    def format_user_data_for_llm(asana_data: Dict[str, Any]) -> str:
        """Convert Asana data to text"""
        
        if not asana_data or "error" in asana_data:
            return ""
        
        output = []
        output.append("=" * 80)
        output.append("ASANA PROJECT DATA")
        output.append("=" * 80)
        output.append("")
        
        # User info
        user = asana_data.get("user", {})
        output.append(f"Employee: {user.get('name', 'Unknown')}")
        output.append(f"Total Projects: {asana_data.get('total_projects', 0)}")
        output.append(f"Total Tasks: {asana_data.get('total_tasks', 0)}")
        output.append("")
        
        # Projects
        projects = asana_data.get("projects", [])
        if projects:
            output.append("PROJECTS:")
            for i, project in enumerate(projects, 1):
                output.append(f"{i}. {project.get('name', 'Untitled')}")
                if project.get('notes'):
                    output.append(f"   Description: {project['notes']}")
                status = "Completed" if project.get('completed') else "Active"
                output.append(f"   Status: {status}")
                output.append("")
        
        # Tasks
        tasks = asana_data.get("tasks", [])
        if tasks:
            output.append("TASKS:")
            for i, task in enumerate(tasks, 1):
                output.append(f"Task {i}: {task.get('name', 'Untitled')}")
                status = "Completed" if task.get('completed') else "In Progress"
                output.append(f"  Status: {status}")
                
                if task.get('notes'):
                    output.append(f"  Description: {task['notes']}")
                
                # Comments
                stories = task.get('stories', [])
                comments = [s for s in stories if s.get('type') == 'comment']
                if comments:
                    output.append(f"  Comments ({len(comments)}):")
                    for comment in comments[:2]:
                        text = comment.get('text', '').strip()
                        if text:
                            output.append(f"    - {text}")
                
                output.append("")
        
        output.append("=" * 80)
        
        return "\n".join(output)
```

### Example Formatted Output

```
================================================================================
ASANA PROJECT DATA
================================================================================

Employee: John Doe
Total Projects: 3
Total Tasks: 12

PROJECTS:
1. Q4 Product Launch
   Description: Launch new product features for Q4
   Status: Active

2. API Modernization
   Description: Upgrade legacy API to REST standards
   Status: Completed

3. Team Onboarding
   Status: Active

TASKS:
Task 1: Implement OAuth2 Authentication
  Status: Completed
  Description: Add OAuth2 authentication to user management API
  Comments (2):
    - Added JWT token validation
    - Integrated with Keycloak successfully

Task 2: Database Migration
  Status: In Progress
  Description: Migrate user data to new schema
  Comments (1):
    - Started migration scripts, 60% complete

================================================================================
```

## Integration Pipeline Management

### Conditional Loading Pattern

```python
def get_asana_accessor():
    """Return AsanaAccessor if enabled, None otherwise"""
    
    # Check if Asana integration is enabled
    if not os.getenv("ENABLE_ASANA", "false").lower() == "true":
        logger.info("Asana integration is disabled")
        return None
    
    try:
        # First try to import the asana package itself
        import asana
        logger.info(f"Asana package imported successfully")
        
        # Then import our accessor
        from app.accessors.asana_accessor import AsanaAccessor
        
        logger.info("Initializing Asana accessor...")
        accessor = AsanaAccessor()
        
        # Check if access token is provided
        if not accessor.access_token:
            logger.warning("ASANA_ACCESS_TOKEN not provided - Asana integration disabled")
            return None
        
        # Check if client was initialized
        if not accessor.client:
            logger.warning("Asana client not initialized - Asana integration disabled")
            return None
        
        logger.info("Asana accessor initialized successfully")
        return accessor
        
    except ImportError as e:
        logger.error(f"Failed to import Asana dependencies: {e}")
        logger.warning("Make sure 'asana' package is installed: pip install asana")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Asana accessor: {e}")
        logger.warning("Continuing without Asana integration")
        return None
```

### Health Monitoring

```python
async def health_check(self) -> bool:
    """Check if Asana API is accessible"""
    if not self.client:
        return False
    
    try:
        # Try to get current user as a health check
        user = await self.get_current_user()
        return user is not None
    except Exception as e:
        logger.error(f"Asana health check failed: {e}")
        return False
```

## API Integration Controllers

### Status Monitoring Endpoint

```python
@router.get("/integrations/status", response_model=IntegrationStatusResponse)
async def get_integration_status():
    """Get status of all integrations"""
    
    # Check Nirdesh
    nirdesh_accessor = get_nirdesh_accessor()
    nirdesh_enabled = nirdesh_accessor is not None
    nirdesh_status = "disabled"
    
    if nirdesh_enabled:
        try:
            health = await nirdesh_accessor.health_check()
            nirdesh_status = "healthy" if health else "unhealthy"
        except Exception as e:
            logger.error(f"Nirdesh health check failed: {e}")
            nirdesh_status = "error"
    
    # Check Asana
    asana_accessor = get_asana_accessor()
    asana_enabled = asana_accessor is not None
    asana_status = "disabled"
    
    if asana_enabled:
        try:
            health = await asana_accessor.health_check()
            asana_status = "healthy" if health else "unhealthy"
        except Exception as e:
            logger.error(f"Asana health check failed: {e}")
            asana_status = "error"
    
    return IntegrationStatusResponse(
        nirdesh_enabled=nirdesh_enabled,
        asana_enabled=asana_enabled,
        nirdesh_status=nirdesh_status,
        asana_status=asana_status
    )
```

### Unified Data Access

```python
@router.post("/integrations/user-data", response_model=UserDataResponse)
async def get_user_data(request: UserDataRequest):
    """Get comprehensive user data from available integrations"""
    
    user_email = request.user_email
    source = request.source.lower()
    
    # Determine which integration to use
    nirdesh_accessor = get_nirdesh_accessor()
    asana_accessor = get_asana_accessor()
    
    if source == "auto":
        # Use first available integration
        if nirdesh_accessor:
            source = "nirdesh"
        elif asana_accessor:
            source = "asana"
        else:
            raise HTTPException(status_code=503, detail="No integrations enabled")
    
    try:
        if source == "asana":
            if not asana_accessor:
                raise HTTPException(status_code=503, detail="Asana integration not enabled")
            
            # Get data from Asana
            data = await asana_accessor.get_user_data_for_report(user_email)
            
            # Format for LLM
            from app.accessors.asana_formatter import AsanaDataFormatter
            formatted_text = AsanaDataFormatter.format_user_data_for_llm(data)
            
            return UserDataResponse(
                source="asana",
                user_email=user_email,
                total_projects=data.get("total_projects", 0),
                total_tasks=data.get("total_tasks", 0),
                data=data,
                formatted_text=formatted_text
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid source: {source}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user data from {source}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
```

### Testing and Debugging

```python
@router.get("/asana/test-full-flow")
async def test_asana_full_flow():
    """Test the complete Asana integration flow"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        results = {}
        
        # Step 1: Get current user
        user = await asana_accessor.get_current_user()
        results["step1_user"] = {
            "success": user is not None,
            "data": user,
            "message": "Got current user" if user else "Failed to get user"
        }
        
        if not user:
            return {"test_results": results, "overall_status": "failed", "failed_at": "step1"}
        
        user_gid = user["gid"]
        
        # Step 2: Get workspaces
        workspaces = await asana_accessor.get_workspaces()
        results["step2_workspaces"] = {
            "success": len(workspaces) > 0,
            "data": workspaces,
            "count": len(workspaces),
            "message": f"Found {len(workspaces)} workspaces"
        }
        
        # Continue with projects, tasks, and stories...
        
        return {
            "test_results": results,
            "overall_status": "success",
            "summary": {
                "user_name": user.get("name", "Unknown"),
                "workspaces_count": len(workspaces),
                "projects_count": len(projects),
                "tasks_count": len(tasks)
            }
        }
        
    except Exception as e:
        logger.error(f"Asana full flow test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
```

## Error Handling and Resilience

### Graceful Degradation

```python
# System continues to function even when integrations fail
try:
    asana_data = await asana_accessor.get_user_data_for_report(user_email)
    if "error" in asana_data:
        logger.warning(f"Asana integration returned error: {asana_data['error']}")
        # Fall back to manual data entry or other sources
        asana_data = None
except Exception as e:
    logger.error(f"Asana integration failed: {e}")
    asana_data = None

# Continue with summary generation using available data
if asana_data:
    formatted_data = AsanaDataFormatter.format_user_data_for_llm(asana_data)
    # Use Asana data for summary
else:
    # Use alternative data sources or prompt user for manual input
    formatted_data = get_fallback_data()
```

### Connection Management

```python
async def close(self):
    """Close HTTP client"""
    try:
        if hasattr(self, 'session'):
            self.session.close()
    except Exception as e:
        logger.error(f"Error closing client: {e}")
```

### Retry Logic

```python
async def get_with_retry(self, url: str, params: dict = None, max_retries: int = 3):
    """Make HTTP request with retry logic"""
    
    for attempt in range(max_retries):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(url, params=params)
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                await asyncio.sleep(wait_time)
                continue
            else:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Final attempt failed: {e}")
                return None
            
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)
    
    return None
```

## Configuration Management

### Environment Variables

```bash
# Asana Integration
ENABLE_ASANA=true
ASANA_ACCESS_TOKEN=2/1212000333310446/1212371107783289:00bf8b93d27be1eb951707d09509979f

# Nirdesh Integration
ENABLE_NIRDESH=true
NIRDESH_DB_SERVICE_URL=https://nirdesh-api.example.com
NIRDESH_API_KEY=your_nirdesh_api_key
```

### Configuration Validation

```python
@router.get("/asana/debug")
async def debug_asana_config():
    """Debug Asana configuration (for troubleshooting)"""
    
    import os
    
    enable_asana = os.getenv("ENABLE_ASANA", "not_set")
    has_token = bool(os.getenv("ASANA_ACCESS_TOKEN", ""))
    token_preview = ""
    
    if has_token:
        token = os.getenv("ASANA_ACCESS_TOKEN", "")
        # Show first 10 and last 4 characters for debugging
        if len(token) > 14:
            token_preview = f"{token[:10]}...{token[-4:]}"
        else:
            token_preview = "token_too_short"
    
    # Try to create accessor and capture any errors
    asana_accessor = get_asana_accessor()
    
    return {
        "environment_variables": {
            "ENABLE_ASANA": enable_asana,
            "has_ASANA_ACCESS_TOKEN": has_token,
            "token_preview": token_preview if has_token else "no_token"
        },
        "accessor_status": {
            "accessor_created": asana_accessor is not None,
            "client_initialized": asana_accessor.client is not None if asana_accessor else False,
            "access_token_set": bool(asana_accessor.access_token) if asana_accessor else False
        }
    }
```

## Usage Examples

### Basic Integration Usage

```python
# Check integration status
status_response = await client.get("/api/v1/integrations/status")
print(f"Asana enabled: {status_response['asana_enabled']}")
print(f"Asana status: {status_response['asana_status']}")

# Get user data from Asana
user_data_response = await client.post("/api/v1/integrations/user-data", json={
    "user_email": "john.doe@example.com",
    "source": "asana"
})

formatted_data = user_data_response["formatted_text"]
# Use formatted_data for AI summary generation
```

### Integration in Summary Generation

```python
# In summary builder
async def build_staging_summary_with_integration(self, request: StagingCreateRequest, action_by: UUID):
    """Build summary with external integration data"""
    
    # Try to get data from integrations
    integration_data = None
    
    # Check Asana
    asana_accessor = get_asana_accessor()
    if asana_accessor:
        try:
            asana_data = await asana_accessor.get_user_data_for_report(request.user_email)
            if asana_data and "error" not in asana_data:
                integration_data = AsanaDataFormatter.format_user_data_for_llm(asana_data)
        except Exception as e:
            logger.warning(f"Failed to get Asana data: {e}")
    
    # Combine user data with integration data
    if integration_data:
        combined_prompt = f"{request.user_prompt}\n\nAdditional Context:\n{integration_data}"
    else:
        combined_prompt = request.user_prompt
    
    # Generate summary with enhanced context
    return await self.llm_accessor.get_response(
        model=request.model or settings.DEFAULT_LLM_MODEL,
        content=format_user_data(request.user_data),
        user_prompt=combined_prompt,
        system_prompt=STAGING_SUMMARY_PROMPT
    )
```

## Best Practices

### 1. Integration Design
- Use conditional loading to avoid hard dependencies
- Implement graceful degradation when integrations fail
- Provide clear error messages and fallback options
- Design for extensibility to add new integrations

### 2. Error Handling
- Implement comprehensive retry logic with exponential backoff
- Handle rate limiting and API quotas appropriately
- Log errors with sufficient context for debugging
- Provide meaningful error messages to users

### 3. Performance
- Use connection pooling for HTTP clients
- Implement async operations for non-blocking calls
- Cache frequently accessed data when appropriate
- Monitor API usage and optimize requests

### 4. Security
- Store API tokens securely in environment variables
- Use HTTPS for all external API calls
- Implement proper authentication and authorization
- Validate and sanitize all external data

### 5. Monitoring
- Implement health checks for all integrations
- Monitor API usage and rate limits
- Track integration success/failure rates
- Set up alerts for integration failures

### 6. Testing
- Provide test endpoints for integration validation
- Mock external APIs for unit testing
- Test error scenarios and edge cases
- Validate data formatting and transformation
## Troubl
eshooting

### Common Issues

#### Missing Token Error (Fixed: January 2, 2025)
If you encounter "ASANA_ACCESS_TOKEN not provided" errors despite having the token configured:

1. **Install Asana Package:**
   ```bash
   uv add asana
   ```

2. **Verify Environment Loading:**
   Ensure your accessor files include:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

3. **Test Integration:**
   ```bash
   uv run python -c "from app.accessors.asana_nirdesh_pipeline import get_asana_accessor; print('Working:', get_asana_accessor() is not None)"
   ```

For detailed troubleshooting steps, see [Asana Integration Fixes](../troubleshooting/asana-integration-fixes.md).

#### Token Validation
Verify your Asana token is valid:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://app.asana.com/api/1.0/users/me
```

#### Integration Health Check
Use the built-in health check endpoints:
- `GET /asana/health` - Check Asana integration status
- `GET /asana/debug` - Debug configuration issues
- `GET /integrations/status` - Overall integration status

### Recent Fixes

#### January 2, 2025 - Asana Integration Fix
- **Issue**: Missing token errors despite proper configuration
- **Root Cause**: Missing `asana` package and environment variable loading
- **Solution**: Added package dependency and explicit dotenv loading
- **Status**: ✅ Resolved and tested
- **Files Modified**: 
  - `app/accessors/asana_accessor.py`
  - `app/accessors/asana_nirdesh_pipeline.py`
  - `pyproject.toml` (via `uv add asana`)

---

*Last Updated: January 2, 2025*