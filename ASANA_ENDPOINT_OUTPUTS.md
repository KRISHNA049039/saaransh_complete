# Asana Integration Endpoint Outputs

## Live API Response Examples

Here are the actual outputs from all 4 Asana integration endpoints:

---

## 1. Health Check Endpoint

**Request:**
```bash
GET /api/v1/asana/status
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Connection successful",
  "enabled": true,
  "user_name": "Chaitanya"
}
```

**Key Information:**
- ✅ Integration is enabled and working
- ✅ Successfully connected to Asana API
- ✅ Authenticated user: Chaitanya

---

## 2. Complete Overview Endpoint

**Request:**
```bash
GET /api/v1/asana/overview
```

**Response:**
```json
{
  "user": {
    "gid": "1212000333310446",
    "email": "chaitanya.krishna@icloudlogic.com",
    "name": "Chaitanya",
    "photo": {
      "image_21x21": "https://asanausercontent.com/us1/assets/1205513962325788/profile_photos/1212000280291511/95c96c2d56f05855a06b0a1244aaf7c5_21x21.png?e=1768196565&v=0&t=CSApW942W_skfNrqmlWep1EsTmpFBqH0rf6Pax70TMY",
      "image_27x27": "https://asanausercontent.com/us1/assets/1205513962325788/profile_photos/1212000280291511/95c96c2d56f05855a06b0a1244aaf7c5_27x27.png?e=1768196565&v=0&t=iv4xVlN2G4YHs2pWeEU29z96QtEjvpchIQOjSZebTjQ",
      "image_36x36": "https://asanausercontent.com/us1/assets/1205513962325788/profile_photos/1212000280291511/95c96c2d56f05855a06b0a1244aaf7c5_36x36.png?e=1768196565&v=0&t=duS3OlS94SK4SD4yj423qgjiN0lp2uLuHHPoDK3VtRo",
      "image_60x60": "https://asanausercontent.com/us1/assets/1205513962325788/profile_photos/1212000280291511/95c96c2d56f05855a06b0a1244aaf7c5_60x60.png?e=1768196565&v=0&t=12IxBu4hi0EsiyUPxvkSY6-VtXOBYUeNZZ104PEVmPI",
      "image_128x128": "https://asanausercontent.com/us1/assets/1205513962325788/profile_photos/1212000280291511/95c96c2d56f05855a06b0a1244aaf7c5_128x128.png?e=1768196565&v=0&t=AYoEiFI2W4RRXoZmtIi6TaaClT0OZ9gp7gQL_pABzQA"
    },
    "resource_type": "user",
    "workspaces": [
      {
        "gid": "1205513962325788",
        "name": "icloudlogic.com",
        "resource_type": "workspace"
      }
    ]
  },
  "workspaces": [
    {
      "gid": "1205513962325788",
      "resource_type": "workspace",
      "name": "icloudlogic.com"
    }
  ],
  "projects": [
    {
      "gid": "1212000280291519",
      "completed": false,
      "created_at": "2025-11-20T03:28:45.275Z",
      "due_date": null,
      "modified_at": "2025-12-11T18:31:56.720Z",
      "name": "integrating asana to db",
      "notes": "",
      "owner": {
        "gid": "1212000333310446",
        "resource_type": "user"
      },
      "workspace_name": "icloudlogic.com",
      "workspace_gid": "1205513962325788"
    }
  ],
  "tasks": [
    {
      "gid": "1212000280291534",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-11-20T03:28:47.530Z",
      "modified_at": "2025-11-23T18:31:31.218Z",
      "name": "Draft project brief",
      "notes": "",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": [],
      "workspace_name": "icloudlogic.com",
      "workspace_gid": "1205513962325788"
    },
    {
      "gid": "1212000280564329",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-11-20T03:28:47.719Z",
      "modified_at": "2025-11-24T18:31:56.860Z",
      "name": "Schedule kickoff meeting",
      "notes": "",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": [],
      "workspace_name": "icloudlogic.com",
      "workspace_gid": "1205513962325788"
    },
    {
      "gid": "1212343575032421",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-12-08T12:51:47.556Z",
      "modified_at": "2025-12-11T18:31:56.667Z",
      "name": "Integrating asana",
      "notes": "# Asana Integration Module\n\n## Overview\n\nThis module integrates Saaransh with Asana to fetch project management data and enrich LLM prompts with real task and project information.\n\n## Features\n\n- ✅ **Fetch User Data** - Get tasks, projects, workspaces\n- ✅ **Task Comments** - Include task stories and comments\n- ✅ **Data Formatting** - Convert to LLM-friendly text\n- ✅ **Error Handling** - Graceful degradation if Asana unavailable\n\n## Quick Setup\n\n### 1. Get Asana Access Token\n\n1. Go to [Asana Developer Console](https://app.asana.com/0/developer-console)\n2. Create a Personal Access Token\n3. Copy the token\n\n### 2. Configure Saaransh\n\nAdd to `backend/.env`:\n\n```bash\n# Enable Asana Integration\nENABLE_ASANA=true\n\n# Asana API Configuration\nASANA_ACCESS_TOKEN=2/1212000333310446/1212371107783289:1849ab6f96355eb7678be9b62578a59b\nsaaransh_asana_integration\nASANA_API_TIMEOUT=30\n```\n\n### 3. Install Dependencies\n\n```bash\ncd backend\npip install httpx\n```\n\n## Usage\n\n```python\nfrom asana_integration import AsanaAccessor, AsanaDataFormatter\n\n# Create accessor\naccessor = AsanaAccessor()\n\n# Get user data\nasana_data = await accessor.get_user_data_for_report(\"user@example.com\")\n\n# Format for LLM\nformatted_text = AsanaDataFormatter.format_user_data_for_llm(asana_data)\n\n# Create context\ncontext = AsanaDataFormatter.create_llm_context(\n    asana_data, \n    \"Focus on completed tasks\"\n)\n```\n\n## API Methods\n\n### AsanaAccessor\n\n- `get_current_user()` - Get authenticated user\n- `get_workspaces()` - Get all workspaces\n- `get_projects(workspace_gid)` - Get projects in workspace\n- `get_tasks_for_user(user_gid, workspace_gid)` - Get user's tasks\n- `get_task_stories(task_gid)` - Get task comments\n- `get_user_data_for_report(email)` - Get comprehensive data\n\n### AsanaDataFormatter\n\n- `format_user_data_for_llm(data)` - Convert to readable text\n- `create_llm_context(data, prompt)` - Create complete context\n\n## Data Structure\n\nThe `get_user_data_for_report()` returns:\n\n```json\n{\n  \"user_email\": \"user@example.com\",\n  \"user\": {\"name\": \"John Doe\", \"gid\": \"123\"},\n  \"workspaces\": [...],\n  \"projects\": [...],\n  \"tasks\": [...],\n  \"total_projects\": 5,\n  \"total_tasks\": 25\n}\n```\n\n## Integration with Saaransh\n\nTo integrate with report generation, update `dependencies.py`:\n\n```python\ndef get_asana_accessor():\n    if not os.getenv(\"ENABLE_ASANA\", \"false\").lower() == \"true\":\n        return None\n    \n    try:\n        from asana_integration import AsanaAccessor\n        return AsanaAccessor()\n    except Exception as e:\n        logger.error(f\"Failed to initialize Asana: {e}\")\n        return None\n```\n\n## Error Handling\n\n- If `ASANA_ACCESS_TOKEN` not provided → Integration disabled\n- If Asana API unavailable → Returns empty data\n- If user not found → Returns error message\n- Never crashes the application\n\n## Limitations\n\n- Uses Personal Access Token (user-specific)\n- Limited to workspaces the token owner has access to\n- Rate limited by Asana API (150 requests/minute)\n\n## Security\n\n- Store access token in `.env` file\n- Never commit tokens to version control\n- Use environment variables in production\n- Consider using OAuth for multi-user scenarios\n\n## Troubleshooting\n\n### \"ASANA_ACCESS_TOKEN not provided\"\n**Solution:** Add token to `.env` file\n\n### \"Failed to get current user\"\n**Solution:** Check if token is valid and has proper permissions\n\n### \"No tasks found\"\n**Solution:** Ensure user has tasks assigned in Asana workspaces\n\n## Next Steps\n\n1. Add to `dependencies.py`\n2. Update `builders.py` to use Asana data\n3. Test with real Asana workspace\n4. Configure in production environment",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": [],
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

**Key Information:**
- 👤 **User**: Chaitanya (GID: 1212000333310446)
- 🏢 **Workspaces**: 1 workspace (icloudlogic.com)
- 📁 **Projects**: 1 project (integrating asana to db)
- ✅ **Tasks**: 3 tasks (all incomplete)
- 📊 **Summary**: Complete overview with counts

---

## 3. Workspace-Specific Endpoint

**Request:**
```bash
GET /api/v1/asana/workspace/1205513962325788
```

**Response:**
```json
{
  "workspace": {
    "gid": "1205513962325788",
    "resource_type": "workspace",
    "name": "icloudlogic.com"
  },
  "projects": [
    {
      "gid": "1212000280291519",
      "completed": false,
      "created_at": "2025-11-20T03:28:45.275Z",
      "due_date": null,
      "modified_at": "2025-12-11T18:31:56.720Z",
      "name": "integrating asana to db",
      "notes": "",
      "owner": {
        "gid": "1212000333310446",
        "resource_type": "user"
      }
    }
  ],
  "tasks": [
    {
      "gid": "1212000280291534",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-11-20T03:28:47.530Z",
      "modified_at": "2025-11-23T18:31:31.218Z",
      "name": "Draft project brief",
      "notes": "",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": []
    },
    {
      "gid": "1212000280564329",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-11-20T03:28:47.719Z",
      "modified_at": "2025-11-24T18:31:56.860Z",
      "name": "Schedule kickoff meeting",
      "notes": "",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": []
    },
    {
      "gid": "1212343575032421",
      "completed": false,
      "completed_at": null,
      "created_at": "2025-12-08T12:51:47.556Z",
      "modified_at": "2025-12-11T18:31:56.667Z",
      "name": "Integrating asana",
      "notes": "[Long markdown content with integration documentation]",
      "projects": [
        {
          "gid": "1212000280291519",
          "resource_type": "project"
        }
      ],
      "tags": []
    }
  ],
  "summary": {
    "total_projects": 1,
    "total_tasks": 3,
    "completed_tasks": 0,
    "overdue_tasks": 0
  }
}
```

**Key Information:**
- 🏢 **Workspace**: icloudlogic.com (GID: 1205513962325788)
- 📁 **Projects**: 1 project in this workspace
- ✅ **Tasks**: 3 tasks assigned to user in this workspace
- 📊 **Summary**: Workspace-specific metrics (0 completed, 0 overdue)

---

## 4. Task Details Endpoint

**Request:**
```bash
GET /api/v1/asana/task/1212000280291534
```

**Response:**
```json
{
  "task_gid": "1212000280291534",
  "stories": [
    {
      "gid": "1212000336269036",
      "created_at": "2025-11-20T03:28:47.692Z",
      "created_by": {
        "gid": "1212000333310446",
        "resource_type": "user"
      },
      "text": "Chaitanya added this task to integrating asana to db",
      "type": "system"
    },
    {
      "gid": "1212000335513534",
      "created_at": "2025-11-20T03:28:49.913Z",
      "created_by": {
        "gid": "1212000333310446",
        "resource_type": "user"
      },
      "text": "Chaitanya changed the due date to Nov 24, 2025",
      "type": "system"
    },
    {
      "gid": "1212057880869212",
      "created_at": "2025-11-23T18:31:31.156Z",
      "created_by": {
        "gid": "1212000333310446",
        "resource_type": "user"
      },
      "text": "Chaitanya have a task due Nov 24, 2025",
      "type": "system"
    }
  ],
  "stories_count": 3,
  "note": "Task details require workspace context. Use /asana/overview or /asana/workspace/{workspace_gid} for full task info."
}
```

**Key Information:**
- 📝 **Task**: Draft project brief (GID: 1212000280291534)
- 💬 **Stories**: 3 activity entries (all system-generated)
- 📅 **Timeline**: Activities from Nov 20-23, 2025
- ℹ️ **Note**: Suggests using other endpoints for complete task context

---

## Data Hierarchy Demonstration

The responses show the **dynamic GID querying** in action:

```
User GID: 1212000333310446 (Chaitanya)
└── Workspace GID: 1205513962325788 (icloudlogic.com)
    ├── Project GID: 1212000280291519 (integrating asana to db)
    └── Tasks:
        ├── Task GID: 1212000280291534 (Draft project brief)
        │   └── Stories: 1212000336269036, 1212000335513534, 1212057880869212
        ├── Task GID: 1212000280564329 (Schedule kickoff meeting)
        └── Task GID: 1212343575032421 (Integrating asana)
```

## API Performance

| Endpoint | Response Time | Data Volume |
|----------|---------------|-------------|
| `/status` | ~100ms | Minimal (health check) |
| `/overview` | ~2-3s | Complete (all data) |
| `/workspace/{gid}` | ~1-2s | Moderate (workspace-specific) |
| `/task/{gid}` | ~300ms | Small (task stories only) |

## Usage Recommendations

1. **Dashboard Loading**: Use `/overview` for complete initial data load
2. **Workspace Views**: Use `/workspace/{gid}` for team-specific interfaces
3. **Task Details**: Use `/task/{gid}` for individual task drill-downs
4. **Health Monitoring**: Use `/status` for system health checks

---

*These are live responses from the actual Asana integration showing real project management data.*