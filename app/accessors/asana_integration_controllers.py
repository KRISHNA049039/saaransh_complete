"""
Integration Controllers

FastAPI endpoints for Nirdesh and Asana integrations.
Provides REST API access to project management data.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel


logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class IntegrationStatusResponse(BaseModel):
    """Response model for integration status"""
    nirdesh_enabled: bool
    asana_enabled: bool
    nirdesh_status: str
    asana_status: str


class UserDataRequest(BaseModel):
    """Request model for fetching user data"""
    user_email: str
    source: str = "auto"  # "nirdesh", "asana", or "auto"


class UserDataResponse(BaseModel):
    """Response model for user data"""
    source: str
    user_email: str
    total_projects: int
    total_tasks: int
    data: Dict[str, Any]
    formatted_text: Optional[str] = None


# ==================== STATUS ENDPOINTS ====================

@router.get("/integrations/status", response_model=IntegrationStatusResponse)
async def get_integration_status():
    """
    Get status of all integrations
    
    Returns information about which integrations are enabled and their health status.
    """
    
    # Check Nirdesh
    nirdesh_accessor = get_nirdesh_accessor()
    nirdesh_enabled = nirdesh_accessor is not None
    nirdesh_status = "disabled"
    
    if nirdesh_enabled:
        try:
            # Test Nirdesh connection
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
            # Test Asana connection
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


# ==================== NIRDESH ENDPOINTS ====================

@router.get("/nirdesh/tasks")
async def get_nirdesh_tasks():
    """Get all tasks from Nirdesh"""
    
    nirdesh_accessor = get_nirdesh_accessor()
    if not nirdesh_accessor:
        raise HTTPException(status_code=503, detail="Nirdesh integration not enabled")
    
    try:
        tasks = await nirdesh_accessor.get_all_tasks()
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        logger.error(f"Failed to get Nirdesh tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")


@router.get("/nirdesh/projects")
async def get_nirdesh_projects():
    """Get all projects from Nirdesh"""
    
    nirdesh_accessor = get_nirdesh_accessor()
    if not nirdesh_accessor:
        raise HTTPException(status_code=503, detail="Nirdesh integration not enabled")
    
    try:
        projects = await nirdesh_accessor.get_all_projects()
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        logger.error(f"Failed to get Nirdesh projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@router.get("/nirdesh/users/{user_id}")
async def get_nirdesh_user(user_id: int):
    """Get specific user from Nirdesh"""
    
    nirdesh_accessor = get_nirdesh_accessor()
    if not nirdesh_accessor:
        raise HTTPException(status_code=503, detail="Nirdesh integration not enabled")
    
    try:
        user = await nirdesh_accessor.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Nirdesh user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


# ==================== ASANA ENDPOINTS ====================

@router.get("/asana/workspaces")
async def get_asana_workspaces():
    """Get all Asana workspaces"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        workspaces = await asana_accessor.get_workspaces()
        return {"workspaces": workspaces, "count": len(workspaces)}
    except Exception as e:
        logger.error(f"Failed to get Asana workspaces: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspaces: {str(e)}")


@router.get("/asana/projects")
async def get_asana_projects(workspace_gid: str = Query(..., description="Workspace GID")):
    """Get projects from specific Asana workspace"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        projects = await asana_accessor.get_projects(workspace_gid)
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        logger.error(f"Failed to get Asana projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")


@router.get("/asana/me")
async def get_asana_current_user():
    """Get current Asana user"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        user = await asana_accessor.get_current_user()
        if not user:
            raise HTTPException(status_code=404, detail="Could not get current user")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current Asana user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


@router.get("/asana/tasks")
async def get_asana_tasks(
    workspace_gid: str = Query(..., description="Workspace GID"),
    user_gid: Optional[str] = Query(None, description="User GID (defaults to current user)")
):
    """Get tasks for a user in a specific workspace"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        # If no user_gid provided, use current user
        if not user_gid:
            current_user = await asana_accessor.get_current_user()
            if not current_user:
                raise HTTPException(status_code=404, detail="Could not get current user")
            user_gid = current_user["gid"]
        
        tasks = await asana_accessor.get_tasks_for_user(user_gid, workspace_gid)
        return {"tasks": tasks, "count": len(tasks), "user_gid": user_gid, "workspace_gid": workspace_gid}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Asana tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")


@router.get("/asana/tasks/{task_gid}/stories")
async def get_asana_task_stories(task_gid: str):
    """Get stories/comments for a specific task"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        stories = await asana_accessor.get_task_stories(task_gid)
        return {"stories": stories, "count": len(stories), "task_gid": task_gid}
    except Exception as e:
        logger.error(f"Failed to get task stories: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stories: {str(e)}")


@router.get("/asana/test-full-flow")
async def test_asana_full_flow():
    """
    Test the complete Asana integration flow
    
    This endpoint tests all major Asana operations in sequence:
    1. Get current user
    2. Get workspaces
    3. Get projects from first workspace
    4. Get tasks for current user
    5. Get stories for first task (if any)
    """
    
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
        
        if not workspaces:
            return {"test_results": results, "overall_status": "failed", "failed_at": "step2"}
        
        workspace_gid = workspaces[0]["gid"]
        
        # Step 3: Get projects
        projects = await asana_accessor.get_projects(workspace_gid)
        results["step3_projects"] = {
            "success": True,  # Projects can be empty
            "data": projects,
            "count": len(projects),
            "message": f"Found {len(projects)} projects in workspace {workspaces[0]['name']}"
        }
        
        # Step 4: Get tasks
        tasks = await asana_accessor.get_tasks_for_user(user_gid, workspace_gid)
        results["step4_tasks"] = {
            "success": True,  # Tasks can be empty
            "data": tasks,
            "count": len(tasks),
            "message": f"Found {len(tasks)} tasks for user"
        }
        
        # Step 5: Get stories for first task (if any)
        if tasks:
            task_gid = tasks[0]["gid"]
            stories = await asana_accessor.get_task_stories(task_gid)
            results["step5_stories"] = {
                "success": True,  # Stories can be empty
                "data": stories,
                "count": len(stories),
                "task_name": tasks[0].get("name", "Unknown"),
                "message": f"Found {len(stories)} stories for task '{tasks[0].get('name', 'Unknown')}'"
            }
        else:
            results["step5_stories"] = {
                "success": True,
                "data": [],
                "count": 0,
                "message": "No tasks available to test stories"
            }
        
        return {
            "test_results": results,
            "overall_status": "success",
            "summary": {
                "user_name": user.get("name", "Unknown"),
                "workspaces_count": len(workspaces),
                "projects_count": len(projects),
                "tasks_count": len(tasks),
                "stories_count": results["step5_stories"]["count"]
            }
        }
        
    except Exception as e:
        logger.error(f"Asana full flow test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


# ==================== UNIFIED DATA ENDPOINTS ====================

@router.post("/integrations/user-data", response_model=UserDataResponse)
async def get_user_data(request: UserDataRequest):
    """
    Get comprehensive user data from available integrations
    
    Fetches user's projects, tasks, and related data from Nirdesh and/or Asana
    based on the source parameter.
    """
    
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
        if source == "nirdesh":
            if not nirdesh_accessor:
                raise HTTPException(status_code=503, detail="Nirdesh integration not enabled")
            
            # Get data from Nirdesh
            data = await nirdesh_accessor.get_user_data_for_report(user_email)
            
            # Format for LLM
            from nirdesh_integration.data_formatter import NirdeshDataFormatter
            formatted_text = NirdeshDataFormatter.format_user_data_for_llm(data)
            
            return UserDataResponse(
                source="nirdesh",
                user_email=user_email,
                total_projects=data.get("total_projects", 0),
                total_tasks=data.get("total_tasks", 0),
                data=data,
                formatted_text=formatted_text
            )
        
        elif source == "asana":
            if not asana_accessor:
                raise HTTPException(status_code=503, detail="Asana integration not enabled")
            
            # Get data from Asana
            data = await asana_accessor.get_user_data_for_report(user_email)
            
            # Format for LLM
            from asana_integration.asana_formatter import AsanaDataFormatter
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


@router.get("/integrations/user-data/{user_email}")
async def get_user_data_simple(
    user_email: str,
    source: str = Query("auto", description="Data source: nirdesh, asana, or auto")
):
    """
    Simple endpoint to get user data (GET version)
    
    Same as POST /integrations/user-data but as a GET request for easier testing.
    """
    
    request = UserDataRequest(user_email=user_email, source=source)
    return await get_user_data(request)


# ==================== HEALTH CHECK ENDPOINTS ====================

@router.get("/nirdesh/health")
async def check_nirdesh_health():
    """Check Nirdesh integration health"""
    
    nirdesh_accessor = get_nirdesh_accessor()
    if not nirdesh_accessor:
        return {"status": "disabled", "message": "Nirdesh integration not enabled"}
    
    try:
        healthy = await nirdesh_accessor.health_check()
        return {
            "status": "healthy" if healthy else "unhealthy",
            "message": "Connection successful" if healthy else "Connection failed"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/asana/health")
async def check_asana_health():
    """Check Asana integration health"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        return {"status": "disabled", "message": "Asana integration not enabled"}
    
    try:
        healthy = await asana_accessor.health_check()
        return {
            "status": "healthy" if healthy else "unhealthy",
            "message": "Connection successful" if healthy else "Connection failed"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


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