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

# Add Local LLM debug endpoints
@debug_router.get("/llm/status")
async def debug_llm_status():
    """Debug endpoint to check LLM configuration and status"""
    try:
        from app.accessors.llm.llm_factory import get_llm_accessor
        
        current_sdk = settings.LLM_SDK
        
        # Get current LLM accessor
        llm_accessor = get_llm_accessor()
        accessor_type = type(llm_accessor).__name__
        
        # Test health if it's local Llama
        health_status = "unknown"
        available_models = []
        
        if hasattr(llm_accessor, 'health_check'):
            try:
                health_status = "healthy" if await llm_accessor.health_check() else "unhealthy"
            except Exception as e:
                health_status = f"error: {str(e)}"
        
        if hasattr(llm_accessor, 'get_available_models'):
            try:
                available_models = await llm_accessor.get_available_models()
            except Exception as e:
                available_models = [f"error: {str(e)}"]
        
        # Clean up
        if hasattr(llm_accessor, 'close'):
            await llm_accessor.close()
        
        return {
            "current_sdk": current_sdk,
            "accessor_type": accessor_type,
            "health_status": health_status,
            "available_models": available_models,
            "local_llm_config": {
                "enabled": settings.LOCAL_LLM_ENABLED,
                "host": settings.LOCAL_LLM_HOST,
                "port": settings.LOCAL_LLM_PORT,
                "model": settings.LOCAL_LLM_MODEL,
                "timeout": settings.LOCAL_LLM_TIMEOUT
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@debug_router.get("/llm/test")
async def debug_llm_test():
    """Debug endpoint to test LLM response"""
    try:
        from app.accessors.llm.llm_factory import get_llm_accessor
        
        test_prompt = "Hello, please respond to confirm you are working correctly."
        
        llm_accessor = get_llm_accessor()
        
        # Test LLM response
        response = await llm_accessor.get_response(
            model="test",
            content="This is a test of the LLM integration.",
            user_prompt=test_prompt,
            system_prompt="You are a helpful assistant. Respond concisely and clearly."
        )
        
        # Test token counting
        token_count = await llm_accessor.get_token_count(test_prompt)
        
        # Clean up
        if hasattr(llm_accessor, 'close'):
            await llm_accessor.close()
        
        return {
            "status": "success",
            "accessor_type": type(llm_accessor).__name__,
            "test_prompt": test_prompt,
            "response": response,
            "token_count": token_count,
            "response_length": len(response)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@debug_router.post("/llm/saaransh-simple")
async def debug_simple_saaransh_test():
    """Test LLM integration with simple Saaransh-style prompt"""
    try:
        from app.accessors.llm.llm_factory import get_llm_accessor
        
        # Simple task content
        task_content = "Project Alpha: 3 tasks completed, 2 pending. Team delivered authentication module. API integration delayed."
        
        user_prompt = "Summarize this project status"
        system_prompt = "You are a project assistant. Be concise."
        
        llm_accessor = get_llm_accessor()
        
        # Test with simple content
        response = await llm_accessor.get_response(
            model="saaransh-simple",
            content=task_content,
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # Clean up
        if hasattr(llm_accessor, 'close'):
            await llm_accessor.close()
        
        return {
            "status": "success",
            "test_type": "simple_saaransh_integration",
            "accessor_type": type(llm_accessor).__name__,
            "input": task_content,
            "prompt": user_prompt,
            "summary": response,
            "length": len(response),
            "note": "This confirms local Llama works with Saaransh-style prompts"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@debug_router.post("/llm/saaransh-test")
async def debug_saaransh_llm_integration():
    """Test LLM integration with Saaransh-style prompts"""
    try:
        from app.accessors.llm.llm_factory import get_llm_accessor
        
        # Simulate Saaransh task data
        task_content = """
        Project Status Report:
        - User Authentication Module: COMPLETED
        - Database Schema Updates: COMPLETED  
        - API Integration: IN PROGRESS (60% complete, facing third-party delays)
        - Frontend Components: IN PROGRESS (3 new components completed)
        
        Overall Progress: 67% complete
        Team: 4 developers working on remaining tasks
        Timeline: 4 tasks remaining, targeting completion next week
        """
        
        user_prompt = "Create a concise executive summary of this project status"
        system_prompt = "You are a project management assistant. Create clear, professional summaries for executives."
        
        llm_accessor = get_llm_accessor()
        
        # Test with Saaransh-style content
        response = await llm_accessor.get_response(
            model="saaransh-test",
            content=task_content,
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # Clean up
        if hasattr(llm_accessor, 'close'):
            await llm_accessor.close()
        
        return {
            "status": "success",
            "integration_test": "saaransh_pipeline",
            "accessor_type": type(llm_accessor).__name__,
            "input_content": task_content,
            "user_prompt": user_prompt,
            "generated_summary": response,
            "response_length": len(response),
            "note": "This simulates how Saaransh uses the LLM for project summaries"
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

app.include_router(debug_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}
