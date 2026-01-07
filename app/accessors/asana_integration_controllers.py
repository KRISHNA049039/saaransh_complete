"""
Asana Integration Controllers

Simplified FastAPI endpoints for Asana integration.
Provides essential REST API access to Asana project management data.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.accessors.asana_nirdesh_pipeline import get_asana_accessor

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== RESPONSE MODELS ====================

class AsanaOverviewResponse(BaseModel):
    """Complete Asana overview response"""
    user: Dict[str, Any]
    workspaces: list
    projects: list
    tasks: list
    summary: Dict[str, int]


class AsanaWorkspaceResponse(BaseModel):
    """Workspace-specific data response"""
    workspace: Dict[str, Any]
    projects: list
    tasks: list
    summary: Dict[str, int]


# ==================== SIMPLIFIED ENDPOINTS ====================

@router.get("/asana/overview", response_model=AsanaOverviewResponse)
async def get_asana_overview():
    """
    Get complete Asana overview for current user
    
    Returns user info, all workspaces, projects, and tasks in one call.
    This is the main endpoint for getting all Asana data.
    """
    
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
    """
    Get all data for a specific workspace
    
    Returns projects and tasks for the specified workspace.
    """
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        # Get current user for tasks
        user = await asana_accessor.get_current_user()
        if not user:
            raise HTTPException(status_code=404, detail="Could not get current user")
        
        user_gid = user["gid"]
        
        # Get workspace info (from workspaces list)
        workspaces = await asana_accessor.get_workspaces()
        workspace = next((w for w in workspaces if w["gid"] == workspace_gid), None)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Get projects in workspace
        projects = await asana_accessor.get_projects(workspace_gid)
        
        # Get tasks for user in workspace
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
async def get_task_details(task_gid: str, include_stories: bool = Query(True, description="Include task stories/comments")):
    """
    Get detailed information for a specific task
    
    Returns task details and optionally includes stories/comments.
    """
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        # Note: We'll need to get the task from the tasks endpoint
        # For now, we'll get stories and return basic info
        stories = []
        if include_stories:
            stories = await asana_accessor.get_task_stories(task_gid)
        
        return {
            "task_gid": task_gid,
            "stories": stories,
            "stories_count": len(stories),
            "note": "Task details require workspace context. Use /asana/overview or /asana/workspace/{workspace_gid} for full task info."
        }
        
    except Exception as e:
        logger.error(f"Failed to get task details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch task details: {str(e)}")


@router.get("/asana/status")
async def get_asana_status():
    """
    Get Asana integration status and health
    
    Quick health check endpoint.
    """
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        return {
            "status": "disabled",
            "message": "Asana integration not enabled",
            "enabled": False
        }
    
    try:
        # Test connection by getting current user
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


# ==================== TEAM COLLABORATION ENDPOINTS ====================

@router.get("/asana/team/workspace/{workspace_gid}")
async def get_team_overview(workspace_gid: str):
    """
    Get comprehensive team overview for a workspace
    
    Returns all team members, their tasks, and project assignments.
    This is the main endpoint for getting colleague task data.
    """
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        team_data = await asana_accessor.get_team_tasks_overview(workspace_gid)
        
        if "error" in team_data:
            raise HTTPException(status_code=500, detail=team_data["error"])
        
        return team_data
        
    except Exception as e:
        logger.error(f"Failed to get team overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch team overview: {str(e)}")


@router.get("/asana/team/members/{workspace_gid}")
async def get_workspace_members(workspace_gid: str):
    """Get all members in a workspace"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        members = await asana_accessor.get_workspace_members(workspace_gid)
        
        return {
            "workspace_gid": workspace_gid,
            "members": members,
            "count": len(members)
        }
        
    except Exception as e:
        logger.error(f"Failed to get workspace members: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch members: {str(e)}")


@router.get("/asana/project/{project_gid}/tasks")
async def get_project_tasks(project_gid: str):
    """Get all tasks in a project (from all team members)"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        tasks = await asana_accessor.get_all_tasks_in_project(project_gid)
        
        # Group tasks by assignee for better organization
        tasks_by_assignee = {}
        unassigned_tasks = []
        
        for task in tasks:
            assignee = task.get("assignee")
            if assignee:
                assignee_name = assignee.get("name", "Unknown")
                if assignee_name not in tasks_by_assignee:
                    tasks_by_assignee[assignee_name] = []
                tasks_by_assignee[assignee_name].append(task)
            else:
                unassigned_tasks.append(task)
        
        return {
            "project_gid": project_gid,
            "all_tasks": tasks,
            "tasks_by_assignee": tasks_by_assignee,
            "unassigned_tasks": unassigned_tasks,
            "summary": {
                "total_tasks": len(tasks),
                "assigned_tasks": len(tasks) - len(unassigned_tasks),
                "unassigned_tasks": len(unassigned_tasks),
                "team_members_with_tasks": len(tasks_by_assignee)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get project tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch project tasks: {str(e)}")


@router.get("/asana/team/member/{user_gid}/tasks")
async def get_member_tasks(user_gid: str, workspace_gid: str = Query(..., description="Workspace GID")):
    """Get all tasks for a specific team member"""
    
    asana_accessor = get_asana_accessor()
    if not asana_accessor:
        raise HTTPException(status_code=503, detail="Asana integration not enabled")
    
    try:
        tasks = await asana_accessor.get_tasks_for_user(user_gid, workspace_gid)
        
        return {
            "user_gid": user_gid,
            "workspace_gid": workspace_gid,
            "tasks": tasks,
            "summary": {
                "total_tasks": len(tasks),
                "completed_tasks": len([t for t in tasks if t.get("completed", False)]),
                "pending_tasks": len([t for t in tasks if not t.get("completed", False)])
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get member tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch member tasks: {str(e)}")