# Production Deployment Checklist & Troubleshooting Guide

## Pre-Deployment Checklist

### ✅ Code Preparation
- [ ] All environment variables configured in `.env.production`
- [ ] Debug mode disabled (`DEBUG=False`)
- [ ] Proper logging configuration
- [ ] Error handling implemented
- [ ] Input validation in place
- [ ] Rate limiting configured
- [ ] CORS policies set correctly
- [ ] Security headers configured

### ✅ Dependencies & Configuration
- [ ] `pyproject.toml` dependencies locked
- [ ] `uv.lock` file committed
- [ ] Docker images built and tested
- [ ] Environment-specific configurations
- [ ] SSL certificates obtained
- [ ] Domain DNS configured

### ✅ Infrastructure Preparation
- [ ] AWS account and IAM roles configured
- [ ] VPC and subnets created
- [ ] Security groups configured
- [ ] Load balancer set up
- [ ] Auto-scaling groups configured
- [ ] Monitoring and alerting set up

### ✅ AI Services Preparation
- [ ] Ollama server configured and tested
- [ ] Llama 3.1 8B model downloaded
- [ ] OpenAI API keys configured
- [ ] Model performance benchmarked
- [ ] Fallback mechanisms tested

### ✅ External Integrations
- [ ] Asana API credentials configured
- [ ] API rate limits understood
- [ ] Error handling for external services
- [ ] Timeout configurations set
- [ ] Retry mechanisms implemented

## Deployment Steps Checklist

### Phase 1: Infrastructure
- [ ] Launch EC2 instances
- [ ] Configure security groups
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Set up monitoring

### Phase 2: Application
- [ ] Deploy application code
- [ ] Configure environment variables
- [ ] Start application services
- [ ] Verify health endpoints
- [ ] Test API endpoints

### Phase 3: AI Services
- [ ] Install and configure Ollama
- [ ] Download required models
- [ ] Test model responses
- [ ] Configure model parameters
- [ ] Set up model monitoring

### Phase 4: Monitoring
- [ ] Configure CloudWatch
- [ ] Set up log aggregation
- [ ] Create dashboards
- [ ] Set up alerts
- [ ] Test notification systems

### Phase 5: Security
- [ ] Configure WAF rules
- [ ] Set up SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up backup systems
- [ ] Test disaster recovery

## Post-Deployment Verification

### ✅ Functional Testing
- [ ] Health check endpoints responding
- [ ] Asana integration working
- [ ] LLM responses generating correctly
- [ ] Authentication flow working
- [ ] Error handling functioning
- [ ] Rate limiting active

### ✅ Performance Testing
- [ ] Response times within SLA
- [ ] Memory usage stable
- [ ] CPU usage acceptable
- [ ] Database connections stable
- [ ] Cache hit rates optimal

### ✅ Security Testing
- [ ] SSL certificate valid
- [ ] Security headers present
- [ ] Input validation working
- [ ] Authentication required
- [ ] Authorization working
- [ ] Audit logging active

## Troubleshooting Guide

### Common Issues & Solutions

#### 1. Application Won't Start

**Symptoms:**
- Container exits immediately
- Health check fails
- Port binding errors

**Diagnosis:**
```bash
# Check container logs
docker logs saaransh-backend

# Check port usage
netstat -tulpn | grep :8000

# Check environment variables
docker exec saaransh-backend env
```

**Solutions:**
```bash
# Fix port conflicts
sudo lsof -i :8000
sudo kill -9 <PID>

# Fix environment variables
docker-compose down
docker-compose up -d

# Check file permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/saaransh-backend
```

#### 2. Ollama Connection Issues

**Symptoms:**
- LLM requests timeout
- "Connection refused" errors
- Model not found errors

**Diagnosis:**
```bash
# Check Ollama service
sudo systemctl status ollama

# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello"
}'

# Check available models
ollama list
```

**Solutions:**
```bash
# Restart Ollama service
sudo systemctl restart ollama

# Pull missing model
ollama pull llama3.1:8b

# Check Ollama logs
journalctl -u ollama -f

# Fix permissions
sudo chown -R ollama:ollama /usr/share/ollama
```

#### 3. Asana API Issues

**Symptoms:**
- 401 Unauthorized errors
- Rate limit exceeded
- Invalid token errors

**Diagnosis:**
```bash
# Test Asana token
curl -H "Authorization: Bearer $ASANA_TOKEN" \
  https://app.asana.com/api/1.0/users/me

# Check rate limits
curl -I -H "Authorization: Bearer $ASANA_TOKEN" \
  https://app.asana.com/api/1.0/workspaces
```

**Solutions:**
```python
# Refresh Asana token
# Update .env file with new token
ASANA_ACCESS_TOKEN=new_token_here

# Implement rate limiting
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=150, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        # Remove old requests
        self.requests = [req for req in self.requests 
                        if now - req < timedelta(seconds=self.time_window)]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0]).seconds
            await asyncio.sleep(sleep_time)
        
        self.requests.append(now)
```

#### 4. High Memory Usage

**Symptoms:**
- OOM killer activated
- Slow response times
- Container restarts

**Diagnosis:**
```bash
# Check memory usage
free -h
docker stats

# Check process memory
ps aux --sort=-%mem | head

# Check application metrics
curl http://localhost:8000/metrics
```

**Solutions:**
```python
# Optimize memory usage in settings.py
class Settings(BaseSettings):
    # Reduce worker count
    WORKERS: int = 2
    
    # Limit request size
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Configure garbage collection
    GC_THRESHOLD: tuple = (700, 10, 10)

# Add memory monitoring
import gc
import psutil

@app.middleware("http")
async def memory_monitor(request, call_next):
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    response = await call_next(request)
    
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    if memory_after - memory_before > 50:  # 50MB increase
        gc.collect()
    
    return response
```

#### 5. SSL Certificate Issues

**Symptoms:**
- Certificate expired warnings
- HTTPS not working
- Mixed content errors

**Diagnosis:**
```bash
# Check certificate expiry
openssl x509 -in /path/to/cert.pem -text -noout | grep "Not After"

# Test SSL configuration
curl -I https://yourdomain.com

# Check certificate chain
openssl s_client -connect yourdomain.com:443 -showcerts
```

**Solutions:**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Update ALB certificate
aws acm list-certificates
aws elbv2 modify-listener --listener-arn <arn> --certificates CertificateArn=<new-cert-arn>

# Force HTTPS redirect
# Add to nginx.conf
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 6. Database Connection Issues (if applicable)

**Symptoms:**
- Connection pool exhausted
- Timeout errors
- Deadlock errors

**Diagnosis:**
```bash
# Check database connections
SELECT * FROM pg_stat_activity WHERE state = 'active';

# Check connection pool
docker exec saaransh-backend python -c "
from app.database import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
"
```

**Solutions:**
```python
# Optimize connection pool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)

# Add connection retry logic
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10)
)
async def execute_query(query):
    # Database operation
    pass
```

## Performance Optimization

### 1. Response Time Optimization

```python
# Add response time middleware
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 2.0:  # 2 seconds
        logger.warning(f"Slow request: {request.url} took {process_time:.2f}s")
    
    return response
```

### 2. Caching Implementation

```python
# Redis caching for expensive operations
import redis.asyncio as redis
import json
from functools import wraps

redis_client = redis.from_url(settings.REDIS_URL)

def cache_response(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_response(ttl=1800)  # 30 minutes
async def get_asana_projects(workspace_gid: str):
    # Expensive Asana API call
    pass
```

### 3. Background Task Processing

```python
# Implement background tasks for heavy operations
from fastapi import BackgroundTasks
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_heavy_task(data: dict):
    """Process heavy AI operations in background"""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, heavy_ai_processing, data)
    return result

@app.post("/api/v1/process-async")
async def process_async(data: dict, background_tasks: BackgroundTasks):
    # Start background task
    background_tasks.add_task(process_heavy_task, data)
    return {"status": "processing", "message": "Task started"}
```

## Monitoring & Alerting Setup

### 1. Application Metrics

```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 2. Health Check Enhancement

```python
# Comprehensive health checks
@app.get("/health/detailed")
async def detailed_health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
            health_status["services"]["ollama"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
    except Exception as e:
        health_status["services"]["ollama"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Asana API
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {settings.ASANA_ACCESS_TOKEN}"}
            response = await client.get("https://app.asana.com/api/1.0/users/me", 
                                      headers=headers, timeout=5.0)
            health_status["services"]["asana"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
    except Exception as e:
        health_status["services"]["asana"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(service.get("status") == "healthy" 
                     for service in health_status["services"].values())
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    return health_status
```

### 3. Log Aggregation

```python
# Structured logging configuration
import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    logHandler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    # Add request ID for tracing
    import uuid
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

This comprehensive checklist and troubleshooting guide provides everything needed for a successful production deployment and ongoing maintenance of the Saaransh backend system.