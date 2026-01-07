# Asana Integration Implementation Steps

## Complete Step-by-Step Implementation Guide

This document provides detailed, actionable steps to implement the Asana integration from scratch.

## Prerequisites

- Python 3.12+
- FastAPI application setup
- Asana account with admin access
- Basic understanding of REST APIs

## Phase 1: Environment Setup

### Step 1.1: Get Asana Access Token

1. **Login to Asana**
   - Go to [https://app.asana.com](https://app.asana.com)
   - Login with your account

2. **Access Developer Console**
   - Navigate to [https://app.asana.com/0/developer-console](https://app.asana.com/0/developer-console)
   - Click on "Personal Access Tokens"

3. **Create New Token**
   - Click "Create New Token"
   - Enter description: "Saaransh Backend Integration"
   - Click "Create Token"
   - **IMPORTANT**: Copy the token immediately (it won't be shown again)

4. **Verify Token**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        https://app.asana.com/api/1.0/users/me
   ```

### Step 1.2: Configure Environment

1. **Update .env file**
   ```bash
   # Add to saaransh_backend/.env
   ENABLE_ASANA=true
   ASANA_ACCESS_TOKEN=2/1212000333310446/1212371107783289:your_actual_token_here
   ```

2. **Verify Environment Loading**
   ```python
   # Test script: test_env.py
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   print(f"ENABLE_ASANA: {os.getenv('ENABLE_ASANA')}")
   print(f"Has Token: {bool(os.getenv('ASANA_ACCESS_TOKEN'))}")
   ```

### Step 1.3: Install Dependencies

1. **Update pyproject.toml**
   ```toml
   dependencies = [
       # ... existing dependencies
       "asana>=5.2.2",
       "requests>=2.31.0",
   ]
   ```

2. **Install Dependencies**
   ```bash
   cd saaransh_backend
   uv sync
   ```

3. **Verify Installation**
   ```python
   # Test script: test_imports.py
   try:
       import asana
       import requests
       print("✅ All dependencies installed successfully")
   except ImportError as e:
       print(f"❌ Import error: {e}")
   ```

## Phase 2: Core Implementation

### Step 2.1: Create Pipeline Layer

**File**: `app/accessors/asana_nirdesh_pipeline.py`

```python
import logging as logger
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_asana_accessor():
    """Return AsanaAccessor if enabled, None otherwise"""
    
    # Check if Asana integration is enabled
    if not os.getenv("ENABLE_ASANA", "false").lower() == "true":
        logger.info("Asana integration is disabled")
        return None
    
    try:
        # Import here to avoid import errors if asana package not installed
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
        logger.warning("Make sure 'asana' package is installed: uv add asana")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Asana accessor: {e}")
        logger.warning("Continuing without Asana integration")
        print(traceback.format_exc())
        return None
```

### Step 2.2: Create Service Layer

**File**: `app/accessors/asana_accessor.py`

```python
"""
Asana API Accessor

Accesses Asana project management data using REST API calls.
"""

import os
import logging
import requests
from typing import List, Optional, Dict, Any
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

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
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        if not self.client:
            return None
        
        try:
            # Make API request
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

### Step 2.3: Create Controller Layer

**File**: `app/accessors/asana_integration_controllers.py`

```python
"""
Asana Integration Controllers

Simplified FastAPI endpoints for Asana integration.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.accessors.asana_nirdesh_pipeline import get_asana_accessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Response Models
class AsanaOverviewResponse(BaseModel):
    user: Dict[str, Any]
    workspaces: list
    projects: list
    tasks: list
    summary: Dict[str, int]

class AsanaWorkspaceResponse(BaseModel):
    workspace: Dict[str, Any]
    projects: list
    tasks: list
    summary: Dict[str, int]

# Endpoints
@router.get("/asana/status")
async def get_asana_status():
    """Get Asana integration status and health"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        return {
            "status": "disabled",
            "message": "Asana integration not enabled",
            "enabled": False
        }
    
    try:
        user = await asana_accessor.get_current_user()
        healthy = user is not None
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "message": "Connection successful" if healthy else "Connection failed",
            "enabled": True,
            "user_name": user.get("name", "Unknown") if user else None
        }
    except Exception as e:
        logger.error(f"Asana health check failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "enabled": True
        }

@router.get("/asana/overview", response_model=AsanaOverviewResponse)
async def get_asana_overview():
    """Get complete Asana overview for current user"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        # Get current user
        user = await asana_accessor.get_current_user()
        if not user:
            raise HTTPException(status_code=404, detail="Could not get current user")
        
        user_gid = user["gid"]
        
        # Get all workspaces
        workspaces = await asana_accessor.get_workspaces()
        
        all_projects = []
        all_tasks = []
        
        # Get projects and tasks from all workspaces
        for workspace in workspaces:
            workspace_gid = workspace["gid"]
            
            # Get projects in this workspace
            projects = await asana_accessor.get_projects(workspace_gid)
            for project in projects:
                project["workspace_name"] = workspace["name"]
                project["workspace_gid"] = workspace_gid
            all_projects.extend(projects)
            
            # Get tasks for user in this workspace
            tasks = await asana_accessor.get_tasks_for_user(user_gid, workspace_gid)
            for task in tasks:
                task["workspace_name"] = workspace["name"]
                task["workspace_gid"] = workspace_gid
            all_tasks.extend(tasks)
        
        return AsanaOverviewResponse(
            user=user,
            workspaces=workspaces,
            projects=all_projects,
            tasks=all_tasks,
            summary={
                "total_workspaces": len(workspaces),
                "total_projects": len(all_projects),
                "total_tasks": len(all_tasks),
                "completed_tasks": len([t for t in all_tasks if t.get("completed", False)])
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get Asana overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch overview: {str(e)}")

@router.get("/asana/workspace/{workspace_gid}", response_model=AsanaWorkspaceResponse)
async def get_workspace_data(workspace_gid: str):
    """Get all data for a specific workspace"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        # Get current user for tasks
        user = await asana_accessor.get_current_user()
        if not user:
            raise HTTPException(status_code=404, detail="Could not get current user")
        
        user_gid = user["gid"]
        
        # Get workspace info
        workspaces = await asana_accessor.get_workspaces()
        workspace = next((w for w in workspaces if w["gid"] == workspace_gid), None)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Get projects and tasks
        projects = await asana_accessor.get_projects(workspace_gid)
        tasks = await asana_accessor.get_tasks_for_user(user_gid, workspace_gid)
        
        return AsanaWorkspaceResponse(
            workspace=workspace,
            projects=projects,
            tasks=tasks,
            summary={
                "total_projects": len(projects),
                "total_tasks": len(tasks),
                "completed_tasks": len([t for t in tasks if t.get("completed", False)]),
                "overdue_tasks": len([t for t in tasks if t.get("due_date") and not t.get("completed", False)])
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get workspace data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspace data: {str(e)}")

@router.get("/asana/task/{task_gid}")
async def get_task_details(task_gid: str, include_stories: bool = Query(True)):
    """Get detailed information for a specific task"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        stories = []
        if include_stories:
            stories = await asana_accessor.get_task_stories(task_gid)
        
        return {
            "task_gid": task_gid,
            "stories": stories,
            "stories_count": len(stories)
        }
        
    except Exception as e:
        logger.error(f"Failed to get task details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch task details: {str(e)}")
```

### Step 2.4: Register Controllers

**File**: `app/main.py` (add to existing imports and router registration)

```python
# Add to imports
from app.accessors.asana_integration_controllers import router as integration_router

# Add to router registration (in existing protected_router section)
protected_router.include_router(integration_router)
```

## Phase 3: Testing and Validation

### Step 3.1: Unit Testing

**File**: `tests/test_asana_integration.py`

```python
import pytest
import os
from unittest.mock import patch, MagicMock
from app.accessors.asana_nirdesh_pipeline import get_asana_accessor

class TestAsanaIntegration:
    
    @patch.dict(os.environ, {"ENABLE_ASANA": "false"})
    def test_asana_disabled(self):
        """Test that accessor returns None when disabled"""
        accessor = get_asana_accessor()
        assert accessor is None
    
    @patch.dict(os.environ, {"ENABLE_ASANA": "true", "ASANA_ACCESS_TOKEN": "test_token"})
    @patch('app.accessors.asana_accessor.AsanaAccessor')
    def test_asana_enabled(self, mock_accessor_class):
        """Test that accessor is created when enabled"""
        mock_instance = MagicMock()
        mock_instance.access_token = "test_token"
        mock_instance.client = MagicMock()
        mock_accessor_class.return_value = mock_instance
        
        accessor = get_asana_accessor()
        assert accessor is not None
        mock_accessor_class.assert_called_once()

    @patch.dict(os.environ, {"ENABLE_ASANA": "true", "ASANA_ACCESS_TOKEN": ""})
    def test_asana_no_token(self):
        """Test graceful handling when no token provided"""
        accessor = get_asana_accessor()
        assert accessor is None
```

### Step 3.2: Integration Testing

**File**: `tests/test_asana_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAsanaAPI:
    
    def test_status_endpoint(self):
        """Test the status endpoint"""
        response = client.get("/api/v1/asana/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "enabled" in data
    
    def test_overview_endpoint_when_disabled(self):
        """Test overview endpoint when Asana is disabled"""
        # This test assumes Asana is disabled in test environment
        response = client.get("/api/v1/asana/overview")
        # Should return 503 if disabled
        assert response.status_code in [200, 503]
    
    def test_workspace_endpoint_invalid_gid(self):
        """Test workspace endpoint with invalid GID"""
        response = client.get("/api/v1/asana/workspace/invalid_gid")
        # Should return error for invalid GID
        assert response.status_code in [404, 500, 503]
```

### Step 3.3: Manual Testing

1. **Start the Server**
   ```bash
   cd saaransh_backend
   uv run python serve.py
   ```

2. **Test Health Check**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/asana/status" \
        -H "accept: application/json"
   ```

3. **Test Overview Endpoint**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/asana/overview" \
        -H "accept: application/json"
   ```

4. **Test Workspace Endpoint**
   ```bash
   # Replace with actual workspace GID from overview response
   curl -X GET "http://localhost:8000/api/v1/asana/workspace/1205513962325788" \
        -H "accept: application/json"
   ```

5. **Test Task Endpoint**
   ```bash
   # Replace with actual task GID from workspace response
   curl -X GET "http://localhost:8000/api/v1/asana/task/1212000280291534" \
        -H "accept: application/json"
   ```

## Phase 4: Production Deployment

### Step 4.1: Environment Configuration

1. **Production .env**
   ```bash
   # Production environment variables
   ENABLE_ASANA=true
   ASANA_ACCESS_TOKEN=${ASANA_TOKEN_FROM_SECRET_MANAGER}
   LOG_LEVEL=INFO
   ```

2. **Docker Configuration** (if using Docker)
   ```dockerfile
   # Add to Dockerfile
   ENV ENABLE_ASANA=true
   # Token should be injected at runtime via secrets
   ```

3. **Kubernetes Configuration** (if using K8s)
   ```yaml
   # asana-secret.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: asana-credentials
   type: Opaque
   data:
     token: <base64-encoded-token>
   ```

### Step 4.2: Monitoring and Logging

1. **Add Health Check Monitoring**
   ```python
   # Add to monitoring system
   def check_asana_health():
       response = requests.get("http://localhost:8000/api/v1/asana/status")
       return response.json().get("status") == "healthy"
   ```

2. **Configure Log Aggregation**
   ```python
   # Ensure proper logging configuration
   import logging
   
   logging.getLogger("app.accessors.asana_accessor").setLevel(logging.INFO)
   ```

### Step 4.3: Performance Optimization

1. **Add Caching** (optional)
   ```python
   # Add Redis caching for frequently accessed data
   from functools import lru_cache
   
   @lru_cache(maxsize=100, ttl=300)  # 5-minute cache
   async def cached_get_workspaces():
       # Implementation
       pass
   ```

2. **Connection Pooling**
   ```python
   # Already implemented in AsanaAccessor with requests.Session
   # Ensure session reuse for better performance
   ```

## Phase 5: Maintenance and Monitoring

### Step 5.1: Regular Maintenance Tasks

1. **Token Rotation**
   - Set up quarterly token rotation
   - Update environment variables
   - Test integration after rotation

2. **Dependency Updates**
   ```bash
   # Regular dependency updates
   uv update
   uv sync
   ```

3. **Performance Monitoring**
   - Monitor API response times
   - Track rate limit usage
   - Monitor error rates

### Step 5.2: Troubleshooting Guide

1. **Common Issues and Solutions**

   | Issue | Cause | Solution |
   |-------|-------|----------|
   | "Integration not enabled" | ENABLE_ASANA=false | Set to true and restart |
   | "Failed to get user" | Invalid token | Generate new token |
   | "No workspaces" | User has no access | Check Asana permissions |
   | Rate limit errors | Too many requests | Implement backoff strategy |

2. **Debug Commands**
   ```bash
   # Check environment
   python -c "import os; print(os.getenv('ENABLE_ASANA'))"
   
   # Test token manually
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://app.asana.com/api/1.0/users/me
   
   # Check logs
   tail -f logs/asana_integration.log
   ```

## Completion Checklist

- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Pipeline layer implemented
- [ ] Service layer implemented
- [ ] Controller layer implemented
- [ ] Controllers registered in main.py
- [ ] Unit tests written and passing
- [ ] Integration tests written and passing
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] Production deployment configured
- [ ] Monitoring and logging set up
- [ ] Performance optimization implemented
- [ ] Maintenance procedures documented

## Success Criteria

✅ **Integration Working**: All 4 endpoints return successful responses
✅ **Error Handling**: Graceful degradation when Asana is unavailable
✅ **Performance**: Response times under 5 seconds for overview endpoint
✅ **Security**: No tokens exposed in logs or error messages
✅ **Monitoring**: Health checks and logging in place
✅ **Documentation**: Complete documentation and troubleshooting guides

---

*This implementation guide provides a complete roadmap for implementing the Asana integration. Follow each phase sequentially for best results.*