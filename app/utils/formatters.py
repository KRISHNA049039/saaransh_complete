import json
import yaml
from typing import List, Dict, Any
from app.models.task_data import UserData, Task

def employee(user_data: 'UserData') -> str:
    return f"Employee: {user_data.employee.name} (Role: {user_data.employee.role})\n"

def employee_yaml(user_data: 'UserData') -> str:
    return yaml.safe_dump({
        "employee": {
            "name": user_data.employee.name,
            "role": user_data.employee.role
        }
    }, sort_keys=False)

def employee_json(user_data: 'UserData') -> str:
    return json.dumps({
        "employee": {
            "name": user_data.employee.name,
            "role": user_data.employee.role
        }
    }, indent=2)

def single_task(task: 'Task', task_number: int) -> str:
    task_info = f"{task_number}. {task.title}: {task.description}\n"
    if task.comments:
        task_info += "    Comments:\n"
        for comment in task.comments:
            task_info += f"        - {comment.text}\n"
    if task.logs:
        task_info += "    Logs:\n"
        for log in task.logs:
            task_info += f"        - {log.content}\n"
    return task_info

def tasks_yaml(tasks: List['Task']) -> str:
    return yaml.safe_dump({
        "tasks": [{
            "title": t.title,
            "description": t.description,
            "comments": [c.text for c in t.comments],
            "logs": [l.content for l in t.logs]
        } for t in tasks]
    }, sort_keys=False)

def tasks_json(tasks: List['Task']) -> str:
    return json.dumps({
        "tasks": [{
            "title": t.title,
            "description": t.description,
            "comments": [c.text for c in t.comments],
            "logs": [l.content for l in t.logs]
        } for t in tasks]
    }, indent=2)

def all_tasks(tasks: List['Task']) -> str:
    """Return a single formatted string for all tasks."""
    return "".join(single_task(task, i) for i, task in enumerate(tasks, 1))