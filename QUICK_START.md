# Saaransh Backend - Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites Check
- ✅ Python 3.11+ installed
- ✅ Git installed
- ✅ Internet connection

### 1. Clone and Setup (2 minutes)
```bash
# Clone repository
git clone https://github.com/your-org/saaransh-backend.git
cd saaransh-backend

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or for Windows PowerShell:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

uv pip install -e .
```

### 2. Configure Environment (1 minute)
```bash
# Copy environment template
cp .env.example .env

# Edit with your Asana token (get from: https://app.asana.com/0/developer-console)
# Minimum required:
echo "ASANA_ACCESS_TOKEN=your_token_here" >> .env
echo "LLM_SDK_OPTION=local_llama" >> .env
echo "DEBUG=True" >> .env
```

### 3. Setup Local LLM (2 minutes)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh  # Linux/macOS
# or download from https://ollama.ai for Windows

# Start Ollama and download model
ollama serve &
ollama pull llama3.1:8b

# Test it works
ollama run llama3.1:8b "Hello!"
```

### 4. Start Application (30 seconds)
```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ✅ Application running at: http://localhost:8000
# ✅ API docs available at: http://localhost:8000/docs
```

### 5. Test Everything Works
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test Asana integration
curl -X GET "http://localhost:8000/api/v1/asana/workspaces" \
  -H "Authorization: Bearer your_asana_token"

# Test LLM integration
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

## 🐳 Docker Quick Start (Alternative)

### If you prefer Docker:
```bash
# Clone repository
git clone https://github.com/your-org/saaransh-backend.git
cd saaransh-backend

# Create environment file
echo "ASANA_ACCESS_TOKEN=your_token_here" > .env

# Start everything with Docker Compose
docker-compose up -d

# ✅ Application running at: http://localhost:8000
```

## 📝 Essential API Endpoints

### Core Asana Endpoints
```bash
# Get workspaces
GET /api/v1/asana/workspaces

# Get projects in workspace
GET /api/v1/asana/workspaces/{workspace_gid}/projects

# Get tasks in project
GET /api/v1/asana/projects/{project_gid}/tasks

# Create comment on task
POST /api/v1/asana/tasks/{task_gid}/stories
```

### LLM Endpoints
```bash
# Chat with AI
POST /api/v1/llm/chat
Body: {"message": "Your question here"}

# Summarize content
POST /api/v1/llm/summarize
Body: {"content": "Text to summarize"}

# Debug LLM status
GET /api/v1/llm/debug/status
```

## 🔧 Common Issues & Quick Fixes

### Issue: "Module not found"
```bash
# Solution: Reinstall dependencies
uv pip install -e .
```

### Issue: "Ollama connection refused"
```bash
# Solution: Start Ollama service
ollama serve
```

### Issue: "Asana 401 Unauthorized"
```bash
# Solution: Check your token
curl -H "Authorization: Bearer YOUR_TOKEN" https://app.asana.com/api/1.0/users/me
```

### Issue: "Port 8000 already in use"
```bash
# Solution: Use different port
uvicorn app.main:app --reload --port 8001
```

## 📚 Next Steps

1. **Explore API Documentation**: Visit http://localhost:8000/docs
2. **Read Full Setup Guide**: See `SETUP_GUIDE.md` for detailed configuration
3. **Check Architecture**: Review `FINAL_ARCHITECTURE_DOCUMENTATION.md`
4. **Production Deployment**: Follow `PRODUCTION_DEPLOYMENT_CHECKLIST.md`

## 🆘 Need Help?

- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Logs**: Check terminal output or `logs/` directory
- **Issues**: Check `SETUP_GUIDE.md` troubleshooting section

---

**🎉 You're ready to start building with Saaransh Backend!**