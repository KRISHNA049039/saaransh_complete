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
    
    async def close(self):
        """Close HTTP client"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
        except Exception as e:
            logger.error(f"Error closing client: {e}")