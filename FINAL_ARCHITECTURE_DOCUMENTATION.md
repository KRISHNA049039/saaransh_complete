# Saaransh Backend - Final Architecture Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Software Architecture](#software-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow Architecture](#data-flow-architecture)
5. [API Architecture](#api-architecture)
6. [Production Architecture](#production-architecture)
7. [Extension Guidelines](#extension-guidelines)
8. [Production Deployment Steps](#production-deployment-steps)

## Project Overview

Saaransh is an AI-powered task management and productivity platform that integrates with Asana and provides intelligent insights through dual AI models (LLM + Embeddings). The system processes task data, generates summaries, and provides contextual assistance to users.

### Core Features
- **Asana Integration**: Complete task, project, and workspace management
- **Dual AI Models**: Local LLM (Llama 3.1 8B) + OpenAI Embeddings
- **Intelligent Summarization**: Task and project insights
- **Team Collaboration**: Multi-user workspace support
- **Real-time Processing**: Async task processing with background jobs

## Software Architecture

### Architecture Pattern: Layered + Microservices Hybrid

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Routers  │  WebSocket  │  Static Files  │  CORS    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     BUSINESS LAYER                          │
├─────────────────────────────────────────────────────────────┤
│   Handlers   │   Services   │   Validators   │   Middleware │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     DATA ACCESS LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  Accessors   │  Repositories │  Cache Layer  │  Queue Mgmt  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                         │
├─────────────────────────────────────────────────────────────┤
│   Asana API   │   Local LLM   │   OpenAI API  │   Database  │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles
1. **Separation of Concerns**: Clear layer boundaries
2. **Dependency Injection**: Factory patterns for service creation
3. **Interface Segregation**: Abstract base classes for extensibility
4. **Single Responsibility**: Each component has one clear purpose
5. **Open/Closed Principle**: Easy to extend without modification

## Component Architecture

### 1. Core Components

#### FastAPI Application (`main.py`)
```python
# Central application orchestrator
- Router registration
- Middleware configuration
- Lifecycle management
- Error handling
- CORS and security
```

#### Settings Management (`settings.py`)
```python
# Configuration hub
- Environment variables
- Service configurations
- Feature flags
- Security settings
```

### 2. Handler Layer

#### Comments Handler (`handlers/comments_handler.py`)
```python
# Business logic orchestrator
- Request validation
- Service coordination
- Response formatting
- Error handling
```

#### Task Handler (`handlers/task_handler.py`)
```python
# Task-specific operations
- Task CRUD operations
- Batch processing
- Status management
```

### 3. Accessor Layer

#### Asana Accessor (`accessors/asana_accessor.py`)
```python
# Asana API integration
- Authentication management
- Rate limiting
- Data transformation
- Error recovery
```

#### LLM Factory (`accessors/llm/llm_factory.py`)
```python
# AI service orchestrator
- Model selection
- Configuration management
- Fallback handling
```

#### Local LLM Accessor (`accessors/llm/local_llama_accessor.py`)
```python
# Local AI model integration
- Ollama communication
- Prompt engineering
- Response processing
```

### 4. Data Models

#### Pydantic Models
```python
# Type-safe data structures
- Request/Response models
- Validation rules
- Serialization logic
```

## Data Flow Architecture

### 1. Request Processing Flow

```
Client Request
      │
      ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Router    │───▶│   Handler    │───▶│  Accessor   │
│ (FastAPI)   │    │ (Business)   │    │ (Data)      │
└─────────────┘    └──────────────┘    └─────────────┘
      │                     │                   │
      ▼                     ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Response   │◀───│  Processing  │◀───│ External    │
│ Formatting  │    │   Logic      │    │ Services    │
└─────────────┘    └──────────────┘    └─────────────┘
```

### 2. AI Processing Flow

```
User Input
    │
    ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Handler   │───▶│ LLM Factory  │───▶│Local/Remote │
│             │    │              │    │    LLM      │
└─────────────┘    └──────────────┘    └─────────────┘
    │                       │                   │
    ▼                       ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Response   │◀───│  Processing  │◀───│   AI Model  │
│ Generation  │    │   Pipeline   │    │  Response   │
└─────────────┘    └──────────────┘    └─────────────┘
```

### 3. Asana Integration Flow

```
API Request
    │
    ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Handler   │───▶│Asana Accessor│───▶│ Asana API   │
│             │    │              │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
    │                       │                   │
    ▼                       ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Formatted   │◀───│ Data Trans-  │◀───│ Raw Asana   │
│ Response    │    │ formation    │    │ Response    │
└─────────────┘    └──────────────┘    └─────────────┘
```

## API Architecture

### Core Endpoints Structure

```
/api/v1/
├── asana/
│   ├── workspaces/           # Workspace management
│   ├── projects/{gid}        # Project operations
│   ├── tasks/{gid}          # Task CRUD operations
│   └── stories/{gid}        # Task comments/stories
├── llm/
│   ├── chat/                # LLM interactions
│   ├── summarize/           # Content summarization
│   └── debug/               # Development endpoints
└── health/                  # System health checks
```

### Authentication Flow

```
Client Request
      │
      ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Middleware│───▶│ Token Valid. │───▶│   Asana     │
│   (Auth)    │    │              │    │ Validation  │
└─────────────┘    └──────────────┘    └─────────────┘
      │                     │                   │
      ▼                     ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Proceed    │◀───│   Success    │◀───│   Valid     │
│ to Handler  │    │              │    │   Token     │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Production Architecture

### 1. Infrastructure Components

```
┌─────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER                          │
│                    (AWS ALB/CloudFlare)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION TIER                         │
├─────────────────────────────────────────────────────────────┤
│  EC2 Instance 1   │  EC2 Instance 2   │  EC2 Instance N    │
│  (FastAPI App)    │  (FastAPI App)    │  (FastAPI App)     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      AI SERVICES                            │
├─────────────────────────────────────────────────────────────┤
│   Ollama Server   │   OpenAI API      │   Embedding Svc    │
│   (Local LLM)     │   (Remote)        │   (Vector Store)   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
├─────────────────────────────────────────────────────────────┤
│   Asana API       │   Redis Cache     │   CloudWatch       │
│   (Third-party)   │   (Session)       │   (Monitoring)     │
└─────────────────────────────────────────────────────────────┘
```

### 2. Deployment Architecture

#### Single Instance (Development/Small Scale)
```
EC2 Instance (t3.large)
├── FastAPI Application (Port 8000)
├── Ollama Server (Port 11434)
├── Redis Cache (Port 6379)
└── Nginx Reverse Proxy (Port 80/443)
```

#### Multi-Instance (Production Scale)
```
Application Load Balancer
├── EC2 Instance 1 (FastAPI)
├── EC2 Instance 2 (FastAPI)
└── EC2 Instance 3 (FastAPI)

Dedicated AI Server
├── EC2 Instance (g4dn.xlarge)
└── Ollama + Multiple Models

Shared Services
├── ElastiCache Redis Cluster
├── RDS Database (if needed)
└── S3 Storage (logs, assets)
```

### 3. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                        │
├─────────────────────────────────────────────────────────────┤
│  WAF/CloudFlare  │  SSL/TLS Cert   │  Rate Limiting       │
├─────────────────────────────────────────────────────────────┤
│  VPC Security    │  Security Groups │  IAM Roles          │
├─────────────────────────────────────────────────────────────┤
│  API Key Mgmt    │  Token Validation│  Environment Vars   │
├─────────────────────────────────────────────────────────────┤
│  Input Validation│  CORS Policy     │  Audit Logging      │
└─────────────────────────────────────────────────────────────┘
```

## Extension Guidelines

### 1. Adding New AI Models

#### Step 1: Create New Accessor
```python
# app/accessors/llm/new_model_accessor.py
from app.accessors.llm.llm_accessor import LLMAccessor

class NewModelAccessor(LLMAccessor):
    def __init__(self, config: dict):
        self.config = config
        # Initialize your model client
    
    async def generate_response(self, prompt: str) -> str:
        # Implement model-specific logic
        pass
```

#### Step 2: Update LLM Factory
```python
# app/accessors/llm/llm_factory.py
def create_llm_accessor(sdk_option: str) -> LLMAccessor:
    if sdk_option == "new_model":
        return NewModelAccessor(settings.NEW_MODEL_CONFIG)
    # ... existing options
```

#### Step 3: Add Configuration
```python
# app/settings.py
class Settings(BaseSettings):
    NEW_MODEL_CONFIG: dict = {
        "api_key": "",
        "model_name": "",
        "base_url": ""
    }
```

### 2. Adding New External Integrations

#### Step 1: Create Accessor Interface
```python
# app/accessors/new_service_accessor.py
from abc import ABC, abstractmethod

class NewServiceAccessor(ABC):
    @abstractmethod
    async def fetch_data(self, params: dict) -> dict:
        pass
    
    @abstractmethod
    async def create_item(self, data: dict) -> dict:
        pass
```

#### Step 2: Implement Concrete Accessor
```python
class ConcreteNewServiceAccessor(NewServiceAccessor):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def fetch_data(self, params: dict) -> dict:
        # Implementation
        pass
```

#### Step 3: Create Handler
```python
# app/handlers/new_service_handler.py
class NewServiceHandler:
    def __init__(self):
        self.accessor = ConcreteNewServiceAccessor(
            settings.NEW_SERVICE_API_KEY,
            settings.NEW_SERVICE_BASE_URL
        )
    
    async def handle_request(self, request_data: dict) -> dict:
        # Business logic
        pass
```

#### Step 4: Add Router
```python
# app/routers/new_service_router.py
from fastapi import APIRouter
from app.handlers.new_service_handler import NewServiceHandler

router = APIRouter(prefix="/api/v1/new-service")
handler = NewServiceHandler()

@router.get("/data")
async def get_data():
    return await handler.handle_request({})
```

### 3. Scaling Components

#### Horizontal Scaling
```python
# Add load balancing configuration
# docker-compose.yml or Kubernetes deployment
services:
  app1:
    image: saaransh-backend
    ports: ["8001:8000"]
  app2:
    image: saaransh-backend
    ports: ["8002:8000"]
  nginx:
    image: nginx
    volumes: ["./nginx.conf:/etc/nginx/nginx.conf"]
```

#### Vertical Scaling
```python
# Optimize resource usage
# app/settings.py
class Settings(BaseSettings):
    MAX_WORKERS: int = 4
    WORKER_CONNECTIONS: int = 1000
    KEEPALIVE_TIMEOUT: int = 65
```

### 4. Adding Caching Layer

#### Step 1: Create Cache Interface
```python
# app/cache/cache_interface.py
from abc import ABC, abstractmethod

class CacheInterface(ABC):
    @abstractmethod
    async def get(self, key: str) -> str:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        pass
```

#### Step 2: Implement Redis Cache
```python
# app/cache/redis_cache.py
import redis.asyncio as redis

class RedisCache(CacheInterface):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> str:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        return await self.redis.setex(key, ttl, value)
```

#### Step 3: Add Cache Decorator
```python
# app/decorators/cache_decorator.py
from functools import wraps
from app.cache.redis_cache import RedisCache

def cache_result(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache(settings.REDIS_URL)
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            cached_result = await cache.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            result = await func(*args, **kwargs)
            await cache.set(cache_key, json.dumps(result), ttl)
            return result
        return wrapper
    return decorator
```

## Production Deployment Steps

### Phase 1: Infrastructure Setup

#### 1. AWS Account Preparation
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### 2. VPC and Security Setup
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create security groups
aws ec2 create-security-group \
  --group-name saaransh-web \
  --description "Saaransh web traffic"

# Configure security group rules
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

#### 3. EC2 Instance Launch
```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0abcdef1234567890 \
  --count 1 \
  --instance-type t3.large \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-id subnet-xxxxxxxxx
```

### Phase 2: Application Deployment

#### 1. Server Preparation
```bash
# Connect to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/your-org/saaransh-backend.git
cd saaransh-backend

# Copy production environment file
cp .env.production .env

# Build and start services
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Ollama Setup
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Llama model
ollama pull llama3.1:8b

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Phase 3: Load Balancer Configuration

#### 1. Application Load Balancer
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name saaransh-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-xxxxxxxxx

# Create target group
aws elbv2 create-target-group \
  --name saaransh-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxxxxxx
```

#### 2. SSL Certificate
```bash
# Request SSL certificate
aws acm request-certificate \
  --domain-name yourdomain.com \
  --validation-method DNS

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:...
```

### Phase 4: Monitoring and Logging

#### 1. CloudWatch Setup
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

#### 2. Application Monitoring
```python
# Add to main.py
import logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### Phase 5: Backup and Recovery

#### 1. Automated Backups
```bash
# Create backup script
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf $BACKUP_DIR/saaransh_backup_$DATE.tar.gz /home/ubuntu/saaransh-backend

# Upload to S3
aws s3 cp $BACKUP_DIR/saaransh_backup_$DATE.tar.gz s3://your-backup-bucket/

# Clean old local backups (keep last 7 days)
find $BACKUP_DIR -name "saaransh_backup_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup.sh

# Add to crontab
echo "0 2 * * * /home/ubuntu/backup.sh" | crontab -
```

### Phase 6: Performance Optimization

#### 1. Application Tuning
```python
# app/settings.py - Production optimizations
class Settings(BaseSettings):
    # Uvicorn settings
    WORKERS: int = 4
    MAX_REQUESTS: int = 1000
    MAX_REQUESTS_JITTER: int = 100
    
    # Connection pooling
    HTTP_POOL_CONNECTIONS: int = 20
    HTTP_POOL_MAXSIZE: int = 20
    
    # Caching
    CACHE_TTL: int = 3600
    ENABLE_RESPONSE_CACHE: bool = True
```

#### 2. Database Optimization (if using)
```python
# Connection pooling for databases
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

### Phase 7: Security Hardening

#### 1. System Security
```bash
# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

#### 2. Application Security
```python
# app/middleware/security.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add to main.py
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

### Phase 8: Scaling Preparation

#### 1. Auto Scaling Group
```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name saaransh-template \
  --launch-template-data file://launch-template.json

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name saaransh-asg \
  --launch-template LaunchTemplateName=saaransh-template \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2
```

#### 2. Health Checks
```python
# app/routers/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "services": {
            "ollama": await check_ollama_health(),
            "asana": await check_asana_health()
        }
    }
```

This comprehensive architecture documentation provides the complete blueprint for understanding, extending, and deploying the Saaransh backend system in production environments.