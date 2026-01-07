# Saaransh Backend - Complete Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Environment Setup](#development-environment-setup)
3. [Local Development Setup](#local-development-setup)
4. [Configuration Guide](#configuration-guide)
5. [Running the Application](#running-the-application)
6. [Testing Setup](#testing-setup)
7. [Docker Setup](#docker-setup)
8. [Production Setup](#production-setup)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 8GB RAM (16GB recommended for local LLM)
- **Storage**: 20GB free space (50GB+ for local LLM models)
- **Network**: Stable internet connection for API integrations

### Required Software

#### 1. Python and Package Manager
```bash
# Install Python 3.11+ from python.org or using package manager

# Install uv (fast Python package manager)
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
python --version
```

#### 2. Git
```bash
# Windows: Download from git-scm.com
# macOS: Install Xcode Command Line Tools
xcode-select --install

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install git

# Verify installation
git --version
```

#### 3. Docker (Optional but Recommended)
```bash
# Windows: Download Docker Desktop from docker.com
# macOS: Download Docker Desktop from docker.com
# Linux: Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version
docker-compose --version
```

## Development Environment Setup

### 1. Clone the Repository
```bash
# Clone the repository
git clone https://github.com/your-org/saaransh-backend.git
cd saaransh-backend

# Verify project structure
ls -la
```

### 2. Python Environment Setup
```bash
# Create virtual environment using uv
uv venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Verify virtual environment
which python
python --version
```

### 3. Install Dependencies
```bash
# Install all dependencies using uv
uv pip install -e .

# Or install from requirements if available
uv pip install -r requirements.txt

# Verify installation
uv pip list
```

### 4. IDE Setup (VS Code Recommended)

#### Install VS Code Extensions
```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.pylint",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "ms-vscode.vscode-json"
    ]
}
```

#### VS Code Settings
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Local Development Setup

### 1. Environment Configuration

#### Create Environment File
```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
# Windows
notepad .env

# macOS/Linux
nano .env
```

#### Basic Environment Variables
```bash
# .env file content
# Application Settings
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000

# Asana Integration
ASANA_ACCESS_TOKEN=your_asana_personal_access_token_here
ASANA_CLIENT_ID=your_asana_client_id_here
ASANA_CLIENT_SECRET=your_asana_client_secret_here

# LLM Configuration
LLM_SDK_OPTION=local_llama  # or "openai"
OPENAI_API_KEY=your_openai_api_key_here

# Local LLM Settings
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL_NAME=llama3.1:8b
LOCAL_LLM_TIMEOUT=60

# Cache Settings (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

### 2. Asana API Setup

#### Get Asana Personal Access Token
1. Go to [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Click "Create New Token"
3. Give it a name (e.g., "Saaransh Development")
4. Copy the token and add to `.env` file

#### Test Asana Connection
```bash
# Test Asana API connection
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://app.asana.com/api/1.0/users/me
```

### 3. Local LLM Setup (Ollama)

#### Install Ollama
```bash
# Windows: Download from ollama.ai
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
```

#### Download and Setup Llama Model
```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama3.1:8b

# Test the model
ollama run llama3.1:8b "Hello, how are you?"

# List available models
ollama list
```

#### Configure Ollama for API Access
```bash
# Create Ollama configuration (Linux/macOS)
mkdir -p ~/.ollama
echo 'OLLAMA_HOST=0.0.0.0:11434' >> ~/.ollama/config

# Windows: Set environment variable
setx OLLAMA_HOST "0.0.0.0:11434"

# Restart Ollama service
# Linux/macOS
sudo systemctl restart ollama

# Windows: Restart Ollama application
```

### 4. Optional: Redis Setup (for Caching)

#### Install Redis
```bash
# Windows: Download from redis.io or use WSL
# macOS
brew install redis

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# Start Redis
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

## Configuration Guide

### 1. Application Settings

#### settings.py Configuration
```python
# app/settings.py
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Asana Configuration
    ASANA_ACCESS_TOKEN: str
    ASANA_CLIENT_ID: Optional[str] = None
    ASANA_CLIENT_SECRET: Optional[str] = None
    ASANA_BASE_URL: str = "https://app.asana.com/api/1.0"
    ASANA_TIMEOUT: int = 30
    
    # LLM Configuration
    LLM_SDK_OPTION: str = "local_llama"  # "openai" or "local_llama"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.7
    
    # Local LLM Configuration
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL_NAME: str = "llama3.1:8b"
    LOCAL_LLM_TIMEOUT: int = 60
    LOCAL_LLM_MAX_TOKENS: int = 500
    LOCAL_LLM_TEMPERATURE: float = 0.7
    
    # Cache Configuration
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600
    ENABLE_CACHE: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. Logging Configuration

#### Create logging.conf
```ini
# logging.conf
[loggers]
keys=root,saaransh

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_saaransh]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=saaransh
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/saaransh.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s
```

## Running the Application

### 1. Development Mode

#### Start the Application
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
python -m app.main

# Or using uv
uv run uvicorn app.main:app --reload
```

#### Verify Application is Running
```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
# Open browser: http://localhost:8000/docs
```

### 2. Production Mode

#### Start Production Server
```bash
# Install production server
uv pip install gunicorn

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Or with specific configuration
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --keepalive 2 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### 3. Environment-Specific Startup

#### Development Startup Script
```bash
#!/bin/bash
# scripts/start-dev.sh

# Activate virtual environment
source .venv/bin/activate

# Set development environment
export ENVIRONMENT=development
export DEBUG=True
export LOG_LEVEL=DEBUG

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Start Redis if not running (optional)
if command -v redis-server &> /dev/null; then
    if ! pgrep -x "redis-server" > /dev/null; then
        echo "Starting Redis..."
        redis-server --daemonize yes
    fi
fi

# Start the application
echo "Starting Saaransh Backend..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Startup Script
```bash
#!/bin/bash
# scripts/start-prod.sh

# Set production environment
export ENVIRONMENT=production
export DEBUG=False
export LOG_LEVEL=INFO

# Create logs directory
mkdir -p logs

# Start the application with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --keepalive 2 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  --daemon
```

## Testing Setup

### 1. Install Testing Dependencies
```bash
# Install testing packages
uv pip install pytest pytest-asyncio pytest-cov httpx

# Install development dependencies
uv pip install black isort pylint mypy
```

### 2. Create Test Configuration

#### pytest.ini
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
asyncio_mode = auto
```

#### Test Environment
```bash
# .env.test
DEBUG=True
ENVIRONMENT=test
LOG_LEVEL=DEBUG

# Test Asana token (use a test workspace)
ASANA_ACCESS_TOKEN=test_token_here

# Use local LLM for testing
LLM_SDK_OPTION=local_llama
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL_NAME=llama3.1:8b

# Disable cache for testing
ENABLE_CACHE=False
```

### 3. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_handlers.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

## Docker Setup

### 1. Create Dockerfile

#### Application Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv pip install --system -e .

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Setup

#### docker-compose.yml (Development)
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - ENVIRONMENT=development
      - ASANA_ACCESS_TOKEN=${ASANA_ACCESS_TOKEN}
      - LLM_SDK_OPTION=local_llama
      - LOCAL_LLM_BASE_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - /app/.venv
    depends_on:
      - ollama
      - redis
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  ollama_data:
  redis_data:
```

#### docker-compose.prod.yml (Production)
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - ENVIRONMENT=production
      - ASANA_ACCESS_TOKEN=${ASANA_ACCESS_TOKEN}
      - LLM_SDK_OPTION=${LLM_SDK_OPTION}
      - LOCAL_LLM_BASE_URL=http://ollama:11434
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - ollama
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  ollama_data:
  redis_data:
```

### 3. Run with Docker
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d
```

## Production Setup

### 1. Server Preparation

#### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    curl \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    htop \
    ufw
```

#### Security Setup
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Create application user
sudo useradd -m -s /bin/bash saaransh
sudo usermod -aG sudo saaransh

# Setup SSH key authentication
sudo mkdir -p /home/saaransh/.ssh
sudo cp ~/.ssh/authorized_keys /home/saaransh/.ssh/
sudo chown -R saaransh:saaransh /home/saaransh/.ssh
sudo chmod 700 /home/saaransh/.ssh
sudo chmod 600 /home/saaransh/.ssh/authorized_keys
```

### 2. Application Deployment

#### Clone and Setup
```bash
# Switch to application user
sudo su - saaransh

# Clone repository
git clone https://github.com/your-org/saaransh-backend.git
cd saaransh-backend

# Setup Python environment
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv venv
source .venv/bin/activate
uv pip install -e .

# Copy and configure environment
cp .env.production .env
nano .env  # Edit with production values
```

#### Systemd Service
```ini
# /etc/systemd/system/saaransh.service
[Unit]
Description=Saaransh Backend API
After=network.target

[Service]
Type=exec
User=saaransh
Group=saaransh
WorkingDirectory=/home/saaransh/saaransh-backend
Environment=PATH=/home/saaransh/saaransh-backend/.venv/bin
ExecStart=/home/saaransh/saaransh-backend/.venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable saaransh
sudo systemctl start saaransh

# Check status
sudo systemctl status saaransh

# View logs
sudo journalctl -u saaransh -f
```

### 3. Nginx Configuration

#### Nginx Site Configuration
```nginx
# /etc/nginx/sites-available/saaransh
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Proxy to FastAPI application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/saaransh/saaransh-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

#### Enable Site and SSL
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/saaransh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test SSL renewal
sudo certbot renew --dry-run
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Application Won't Start
```bash
# Check Python version
python --version

# Check virtual environment
which python
pip list

# Check environment variables
env | grep -E "(ASANA|LLM|DEBUG)"

# Check logs
tail -f logs/saaransh.log
sudo journalctl -u saaransh -f
```

#### 2. Ollama Connection Issues
```bash
# Check Ollama service
sudo systemctl status ollama
ollama list

# Test Ollama API
curl http://localhost:11434/api/tags

# Restart Ollama
sudo systemctl restart ollama

# Check Ollama logs
sudo journalctl -u ollama -f
```

#### 3. Asana API Issues
```bash
# Test Asana token
curl -H "Authorization: Bearer $ASANA_ACCESS_TOKEN" \
  https://app.asana.com/api/1.0/users/me

# Check rate limits
curl -I -H "Authorization: Bearer $ASANA_ACCESS_TOKEN" \
  https://app.asana.com/api/1.0/workspaces
```

#### 4. Port Conflicts
```bash
# Check what's using port 8000
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill process using port
sudo kill -9 <PID>
```

#### 5. Permission Issues
```bash
# Fix file permissions
sudo chown -R saaransh:saaransh /home/saaransh/saaransh-backend
chmod +x scripts/*.sh

# Fix log directory permissions
sudo mkdir -p /var/log/saaransh
sudo chown saaransh:saaransh /var/log/saaransh
```

### Performance Monitoring
```bash
# Monitor system resources
htop
free -h
df -h

# Monitor application
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# Monitor logs
tail -f /var/log/nginx/access.log
sudo journalctl -u saaransh -f
```

This comprehensive setup guide covers everything needed to get the Saaransh backend running in both development and production environments.