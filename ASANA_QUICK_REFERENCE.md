# Asana Integration Quick Reference

## 🚀 Quick Start

### 1. Setup (30 seconds)

```bash
# 1. Add to .env
echo "ENABLE_ASANA=true" >> .env
echo "ASANA_ACCESS_TOKEN=your_token_here" >> .env

# 2. Install dependencies
uv sync

# 3. Start server
uv run python serve.py
```

### 2. Test Integration

```bash
# Health check
curl http://localhost:8000/api/v1/asana/status

# Get all data
curl http://localhost:8000/api/v1/asana/overview
```

## 📋 API Endpoints Summary

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/asana/status` | GET | Health check | ~100ms |
| `/asana/overview` | GET | All user data | ~2-5s |
| `/asana/workspace/{gid}` | GET | Workspace data | ~1-3s |
| `/asana/task/{gid}` | GET | Task details | ~200-500ms |

## 🏗️ Architecture at a Glance

```
Controllers → Pipeline → Accessor → Asana API
     ↓           ↓          ↓
   REST      Factory    Business
 Endpoints   Pattern     Logic
```

## 🔧 Key Files

| File | Purpose |
|------|---------|
| `asana_integration_controllers.py` | REST API endpoints |
| `asana_accessor.py` | Core business logic |
| `asana_nirdesh_pipeline.py` | Factory & configuration |
| `.env` | Configuration |

## 📊 Data Hierarchy

```
User (1212000333310446)
└── Workspace (1205513962325788)
    ├── Projects (1212000280291519)
    └── Tasks (1212000280291534)
        └── Stories (1212000336269036)
```

## ⚡ Common Usage Patterns

### Get Everything
```python
response = requests.get("/api/v1/asana/overview")
data = response.json()
```

### Get Workspace Data
```python
workspace_gid = "1205513962325788"
response = requests.get(f"/api/v1/asana/workspace/{workspace_gid}")
```

### Get Task Comments
```python
task_gid = "1212000280291534"
response = requests.get(f"/api/v1/asana/task/{task_gid}")
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Integration not enabled" | Set `ENABLE_ASANA=true` |
| "Failed to get user" | Check `ASANA_ACCESS_TOKEN` |
| "No workspaces" | Verify Asana account access |
| Rate limits | Implement caching/delays |

## 🔑 Environment Variables

```bash
ENABLE_ASANA=true                    # Required: Enable integration
ASANA_ACCESS_TOKEN=2/1212.../1212... # Required: Your personal token
LOG_LEVEL=INFO                       # Optional: Logging level
```

## 📈 Performance Tips

1. **Use `/overview` for dashboards** - Gets everything in one call
2. **Cache responses** - Asana data doesn't change frequently  
3. **Handle rate limits** - 150 requests/minute limit
4. **Use workspace endpoints** - For team-specific views

## 🔒 Security Notes

- Never commit tokens to git
- Use environment variables
- Tokens inherit user permissions
- Consider OAuth for production

## 📝 Response Examples

### Status Response
```json
{
  "status": "healthy",
  "enabled": true,
  "user_name": "Chaitanya"
}
```

### Overview Response
```json
{
  "user": {"gid": "...", "name": "..."},
  "workspaces": [...],
  "projects": [...],
  "tasks": [...],
  "summary": {
    "total_workspaces": 1,
    "total_projects": 1,
    "total_tasks": 3,
    "completed_tasks": 0
  }
}
```

---

*For detailed documentation, see `ASANA_INTEGRATION_ARCHITECTURE.md`*