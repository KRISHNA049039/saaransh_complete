from contextlib import asynccontextmanager
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.components.embeddings_model import EmbeddingModelSingleton
from app.config.logging import setup_logging
from app.config.security.resource_server import require_auth
from app.handlers.comments_handler import router as comments_router
from app.handlers.summaries_handler import router as summaries_router
from app.handlers.summaries_users_handler import router as share_router
from app.handlers.user_prompts_handler import router as user_prompts_router
from app.handlers.auth_test_handler import router as auth_test_router
from app.handlers.kc_test_handler import router as kc_test_router
from app.handlers.users_handler import router as users_router
from app.handlers.llm_handler import router as llm_router
from app.settings import settings
from app.accessors.asana_integration_controllers import router as integration_router


setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    EmbeddingModelSingleton.get_model()
    print("Embedding model loaded at startup")

    yield
    print("Shutting down Saaransh backend")


app = FastAPI(
    title="saaransh_backend",
    description="Backend service for Saaransh application",
    version="1.0.0",
    lifespan=lifespan,
)

origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TEMP: Disabled authentication for testing
protected_router = APIRouter(prefix="/api/v1")  # Removed: dependencies=[Depends(require_auth)]

protected_router.include_router(comments_router)
protected_router.include_router(summaries_router)
protected_router.include_router(users_router)
protected_router.include_router(user_prompts_router)
protected_router.include_router(share_router)
protected_router.include_router(integration_router)
protected_router.include_router(llm_router)

test_router = APIRouter(prefix="/api/v1/test")  # Removed: dependencies=[Depends(require_auth)]

test_router.include_router(auth_test_router)
test_router.include_router(kc_test_router)

app.include_router(protected_router)
app.include_router(test_router)

# Add unprotected debug router for integration testing
debug_router = APIRouter(prefix="/debug")

@debug_router.get("/asana/test")
async def debug_asana_test():
    """Unprotected endpoint to test Asana integration"""
    try:
        from app.accessors.asana_nirdesh_pipeline import get_asana_accessor
        accessor = get_asana_accessor()
        
        if not accessor:
            return {"status": "error", "message": "Asana accessor not available"}
        
        # Test basic API call
        user = await accessor.get_current_user()
        workspaces = await accessor.get_workspaces()
        
        return {
            "status": "success",
            "asana_user": user.get("name") if user else "Failed to get user",
            "workspaces_count": len(workspaces),
            "workspaces": [{"gid": w["gid"], "name": w["name"]} for w in workspaces]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@debug_router.get("/asana/health")
async def debug_asana_health():
    """Unprotected endpoint to check Asana health"""
    try:
        from app.accessors.asana_nirdesh_pipeline import get_asana_accessor
        accessor = get_asana_accessor()
        
        if not accessor:
            return {"status": "disabled", "message": "Asana accessor not available"}
        
        # Test health
        health = await accessor.health_check()
        
        return {
            "status": "healthy" if health else "unhealthy",
            "message": "Connection successful" if health else "Connection failed",
            "has_token": bool(accessor.access_token),
            "token_preview": accessor.access_token[:10] + "..." + accessor.access_token[-4:] if accessor.access_token else "no_token"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@debug_router.get("/integrations/status")
async def debug_integration_status():
    """Unprotected endpoint to check all integrations"""
    try:
        from app.accessors.asana_nirdesh_pipeline import get_asana_accessor
        
        # Check Asana
        asana_accessor = get_asana_accessor()
        asana_enabled = asana_accessor is not None
        asana_status = "disabled"
        
        if asana_enabled:
            try:
                health = await asana_accessor.health_check()
                asana_status = "healthy" if health else "unhealthy"
            except Exception as e:
                asana_status = f"error: {str(e)}"
        
        # Check Nirdesh (simplified)
        nirdesh_enabled = False
        nirdesh_status = "not_tested"
        
        return {
            "asana": {
                "enabled": asana_enabled,
                "status": asana_status
            },
            "nirdesh": {
                "enabled": nirdesh_enabled,
                "status": nirdesh_status
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@debug_router.get("/asana/service-test")
async def debug_asana_service():
    """Test the Asana service layer"""
    try:
        from app.services.asana_service import get_asana_service
        
        service = get_asana_service()
        
        if not service.is_available:
            return {"status": "error", "message": "Asana service not available"}
        
        # Test service methods
        user = await service.get_current_user()
        workspaces = await service.get_workspaces()
        
        if user:
            comprehensive_data = await service.get_comprehensive_user_data(user['email'])
            
            return {
                "status": "success",
                "service_available": True,
                "user": user['name'],
                "workspaces_count": len(workspaces),
                "total_projects": comprehensive_data.get('total_projects', 0),
                "total_tasks": comprehensive_data.get('total_tasks', 0)
            }
        else:
            return {"status": "error", "message": "Failed to get user data"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.include_router(debug_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
