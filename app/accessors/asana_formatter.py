"""
Asana Data Formatter

Formats Asana data for LLM context.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


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
    
    @staticmethod
    def create_llm_context(asana_data: Dict[str, Any], user_prompt: str = "") -> str:
        """Create LLM context"""
        context_parts = []
        
        formatted_data = AsanaDataFormatter.format_user_data_for_llm(asana_data)
        if formatted_data:
            context_parts.append(formatted_data)
        
        if user_prompt:
            context_parts.append(f"USER INSTRUCTIONS: {user_prompt}")
        
        return "\n\n".join(context_parts)