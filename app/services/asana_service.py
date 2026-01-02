"""
Asana Service Layer

Provides high-level access to Asana data without requiring HTTP authentication.
"""

from typing import Dict, List, Optional, Any
from app.accessors.asana_nirdesh_pipeline import get_asana_accessor

class AsanaService:
    """Service for accessing Asana data programmatically"""
    
    def __init__(self):
        self.accessor = get_asana_accessor()
    
    @property
    def is_available(self) -> bool:
        """Check if Asana integration is available"""
        return self.accessor is not None
    
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated Asana user"""
        if not self.is_available:
            return None
        return await self.accessor.get_current_user()
    
    async def get_workspaces(self) -> List[Dict[str, Any]]:
        """Get all available workspaces"""
        if not self.is_available:
            return []
        return await self.accessor.get_workspaces()
    
    async def get_projects(self, workspace_gid: str) -> List[Dict[str, Any]]:
        """Get projects in a workspace"""
        if not self.is_available:
            return []
        return await self.accessor.get_projects(workspace_gid)
    
    async def get_user_tasks(self, user_gid: str, workspace_gid: str) -> List[Dict[str, Any]]:
        """Get tasks for a user in a workspace"""
        if not self.is_available:
            return []
        return await self.accessor.get_tasks_for_user(user_gid, workspace_gid)
    
    async def get_comprehensive_user_data(self, user_email: str) -> Dict[str, Any]:
        """Get comprehensive user data for reports"""
        if not self.is_available:
            return {
                "user_email": user_email,
                "error": "Asana integration not available",
                "total_projects": 0,
                "total_tasks": 0
            }
        return await self.accessor.get_user_data_for_report(user_email)
    
    async def health_check(self) -> bool:
        """Check if Asana integration is healthy"""
        if not self.is_available:
            return False
        return await self.accessor.health_check()

# Singleton instance
_asana_service = None

def get_asana_service() -> AsanaService:
    """Get singleton Asana service instance"""
    global _asana_service
    if _asana_service is None:
        _asana_service = AsanaService()
    return _asana_service