"""
LLM Handler

Provides endpoints for testing and interacting with LLM services including local Ollama models.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.accessors.llm.llm_factory import LLMFactory
from app.accessors.llm.local_llama_accessor import LocalLlamaAccessor
from app.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to send to the LLM")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")
    model: Optional[str] = Field(None, description="Specific model to use (optional)")


class ChatResponse(BaseModel):
    response: str = Field(..., description="LLM generated response")
    model_used: str = Field(..., description="Model that generated the response")
    token_count: Optional[int] = Field(None, description="Estimated token count")


class SummarizeRequest(BaseModel):
    content: str = Field(..., description="Content to summarize")
    max_length: Optional[int] = Field(None, description="Maximum length of summary")


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
    original_length: int = Field(..., description="Original content length")
    summary_length: int = Field(..., description="Summary length")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    model: str = Field(..., description="Current model")
    available: bool = Field(..., description="Whether the service is available")
    models: list = Field(..., description="List of available models")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """
    Chat with the configured LLM (local Ollama or remote)
    
    This endpoint allows you to send a message to the LLM and get a response.
    Perfect for testing if your local Ollama model is working correctly.
    """
    try:
        # Use local Llama accessor directly for testing
        if settings.LLM_SDK == "local_llama" and settings.LOCAL_LLM_ENABLED:
            accessor = LocalLlamaAccessor()
            
            # Generate response
            response = await accessor.get_response(
                model=request.model or settings.LOCAL_LLM_MODEL,
                content="",  # No additional context
                user_prompt=request.message,
                system_prompt=request.system_prompt or "You are a helpful AI assistant."
            )
            
            # Get token count
            token_count = await accessor.get_token_count(request.message + response)
            
            await accessor.close()
            
            return ChatResponse(
                response=response,
                model_used=settings.LOCAL_LLM_MODEL,
                token_count=token_count
            )
        else:
            # Use LLM factory for other models
            factory = LLMFactory()
            accessor = factory.get_llm_accessor()
            
            response = await accessor.get_response(
                model=request.model or settings.DEFAULT_LLM_MODEL,
                content="",
                user_prompt=request.message,
                system_prompt=request.system_prompt or "You are a helpful AI assistant."
            )
            
            return ChatResponse(
                response=response,
                model_used=request.model or settings.DEFAULT_LLM_MODEL,
                token_count=None
            )
            
    except Exception as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM request failed: {str(e)}")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_content(request: SummarizeRequest):
    """
    Summarize the provided content using the configured LLM
    
    This endpoint takes longer text content and generates a concise summary.
    Great for testing how well your local model handles summarization tasks.
    """
    try:
        # Build summarization prompt
        system_prompt = "You are an expert at creating concise, informative summaries. Summarize the following content in a clear and helpful way."
        
        if request.max_length:
            system_prompt += f" Keep the summary under {request.max_length} words."
        
        user_prompt = f"Please summarize this content:\n\n{request.content}"
        
        # Use local Llama accessor for local models
        if settings.LLM_SDK == "local_llama" and settings.LOCAL_LLM_ENABLED:
            accessor = LocalLlamaAccessor()
            
            summary = await accessor.get_response(
                model=settings.LOCAL_LLM_MODEL,
                content=request.content,
                user_prompt="Please provide a concise summary of the above content.",
                system_prompt=system_prompt
            )
            
            await accessor.close()
        else:
            # Use LLM factory for other models
            factory = LLMFactory()
            accessor = factory.get_llm_accessor()
            
            summary = await accessor.get_response(
                model=settings.DEFAULT_LLM_MODEL,
                content=request.content,
                user_prompt="Please provide a concise summary of the above content.",
                system_prompt=system_prompt
            )
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(request.content),
            summary_length=len(summary)
        )
        
    except Exception as e:
        logger.error(f"Summarization request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def check_llm_health():
    """
    Check the health and availability of the LLM service
    
    This endpoint tests if your local Ollama service is running and accessible,
    and returns information about available models.
    """
    try:
        if settings.LLM_SDK == "local_llama" and settings.LOCAL_LLM_ENABLED:
            accessor = LocalLlamaAccessor()
            
            # Check health
            is_healthy = await accessor.health_check()
            
            # Get available models
            available_models = await accessor.get_available_models()
            
            await accessor.close()
            
            return HealthResponse(
                status="healthy" if is_healthy else "unhealthy",
                model=settings.LOCAL_LLM_MODEL,
                available=is_healthy,
                models=available_models
            )
        else:
            return HealthResponse(
                status="configured",
                model=settings.DEFAULT_LLM_MODEL,
                available=True,
                models=[settings.DEFAULT_LLM_MODEL]
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="error",
            model=settings.LOCAL_LLM_MODEL if settings.LOCAL_LLM_ENABLED else settings.DEFAULT_LLM_MODEL,
            available=False,
            models=[]
        )


@router.get("/models")
async def list_available_models():
    """
    List all available models
    
    Returns a list of models available in your local Ollama installation.
    """
    try:
        if settings.LLM_SDK == "local_llama" and settings.LOCAL_LLM_ENABLED:
            accessor = LocalLlamaAccessor()
            models = await accessor.get_available_models()
            await accessor.close()
            
            return {
                "status": "success",
                "service": "local_ollama",
                "models": models,
                "current_model": settings.LOCAL_LLM_MODEL
            }
        else:
            return {
                "status": "success",
                "service": "remote_llm",
                "models": [settings.DEFAULT_LLM_MODEL],
                "current_model": settings.DEFAULT_LLM_MODEL
            }
            
    except Exception as e:
        logger.error(f"Failed to list models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.post("/test-simple")
async def test_simple_request():
    """
    Simple test endpoint to verify LLM connectivity
    
    Sends a basic "Hello" message to test if the LLM is responding correctly.
    Perfect for a quick connectivity test.
    """
    try:
        test_message = "Hello! Please respond with a simple greeting to confirm you're working correctly."
        
        if settings.LLM_SDK == "local_llm" and settings.LOCAL_LLM_ENABLED:
            accessor = LocalLlamaAccessor()
            
            response = await accessor.get_response(
                model=settings.LOCAL_LLM_MODEL,
                content="",
                user_prompt=test_message,
                system_prompt="You are a helpful AI assistant. Respond briefly and clearly."
            )
            
            await accessor.close()
            
            return {
                "status": "success",
                "test_message": test_message,
                "response": response,
                "model": settings.LOCAL_LLM_MODEL,
                "service": "local_ollama"
            }
        else:
            return {
                "status": "success",
                "message": "LLM service configured but not using local Ollama",
                "current_sdk": settings.LLM_SDK,
                "local_enabled": settings.LOCAL_LLM_ENABLED
            }
            
    except Exception as e:
        logger.error(f"Simple test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")
@router.p
ost("/benchmark")
async def benchmark_llm_performance():
    """
    Benchmark LLM performance with different request types
    
    Tests various scenarios to measure response times and identify bottlenecks.
    """
    import time
    
    results = {
        "timestamp": time.time(),
        "tests": [],
        "system_info": {
            "model": settings.LOCAL_LLM_MODEL,
            "sdk": settings.LLM_SDK,
            "local_enabled": settings.LOCAL_LLM_ENABLED
        }
    }
    
    if not (settings.LLM_SDK == "local_llama" and settings.LOCAL_LLM_ENABLED):
        return {
            "error": "Benchmarking only available for local LLM",
            "current_config": results["system_info"]
        }
    
    accessor = LocalLlamaAccessor()
    
    try:
        # Test 1: Simple short response
        start_time = time.time()
        response1 = await accessor.get_response(
            model=settings.LOCAL_LLM_MODEL,
            content="",
            user_prompt="Say 'Hello' in one word.",
            system_prompt="Respond with exactly one word."
        )
        test1_time = time.time() - start_time
        
        results["tests"].append({
            "test": "Short Response (1 word)",
            "time_seconds": round(test1_time, 2),
            "response_length": len(response1),
            "tokens_per_second": round(len(response1.split()) / test1_time, 2)
        })
        
        # Test 2: Medium response
        start_time = time.time()
        response2 = await accessor.get_response(
            model=settings.LOCAL_LLM_MODEL,
            content="",
            user_prompt="Explain what AI is in 2-3 sentences.",
            system_prompt="Be concise and clear."
        )
        test2_time = time.time() - start_time
        
        results["tests"].append({
            "test": "Medium Response (2-3 sentences)",
            "time_seconds": round(test2_time, 2),
            "response_length": len(response2),
            "tokens_per_second": round(len(response2.split()) / test2_time, 2)
        })
        
        # Test 3: Health check speed
        start_time = time.time()
        health_status = await accessor.health_check()
        health_time = time.time() - start_time
        
        results["tests"].append({
            "test": "Health Check",
            "time_seconds": round(health_time, 2),
            "status": "healthy" if health_status else "unhealthy"
        })
        
        # Performance analysis
        avg_response_time = sum(test["time_seconds"] for test in results["tests"][:2]) / 2
        
        results["analysis"] = {
            "average_response_time": round(avg_response_time, 2),
            "performance_rating": (
                "Excellent" if avg_response_time < 3 else
                "Good" if avg_response_time < 8 else
                "Acceptable" if avg_response_time < 15 else
                "Slow"
            ),
            "recommendations": []
        }
        
        # Add recommendations based on performance
        if avg_response_time > 10:
            results["analysis"]["recommendations"].extend([
                "Consider using a smaller model (e.g., llama3.1:3b)",
                "Ensure Ollama has sufficient RAM allocated",
                "Check if other applications are using CPU/RAM"
            ])
        
        if avg_response_time > 5:
            results["analysis"]["recommendations"].extend([
                "Reduce max_tokens for faster responses",
                "Use GPU acceleration if available",
                "Keep model warm with periodic health checks"
            ])
        
        return results
        
    except Exception as e:
        return {
            "error": f"Benchmark failed: {str(e)}",
            "partial_results": results
        }
    finally:
        await accessor.close()


@router.get("/performance-tips")
async def get_performance_optimization_tips():
    """
    Get performance optimization tips for local LLM setup
    """
    return {
        "current_config": {
            "model": getattr(settings, 'LOCAL_LLM_MODEL', 'llama3.1:8b'),
            "timeout": getattr(settings, 'LOCAL_LLM_TIMEOUT', 60),
            "temperature": getattr(settings, 'LOCAL_LLM_TEMPERATURE', 0.7),
            "max_tokens": getattr(settings, 'LOCAL_LLM_MAX_TOKENS', 4096),
            "context_length": getattr(settings, 'LOCAL_LLM_CONTEXT_LENGTH', 8192)
        },
        "optimization_tips": {
            "hardware": [
                "Use SSD storage for faster model loading",
                "Ensure 16GB+ RAM for optimal performance",
                "Use GPU acceleration if available (CUDA/Metal)",
                "Close unnecessary applications to free RAM"
            ],
            "model_settings": [
                "Reduce max_tokens (256-512) for faster responses",
                "Lower temperature (0.3-0.5) for more focused responses",
                "Use smaller context window (2048-4096) if possible",
                "Consider smaller models (3B instead of 8B) for speed"
            ],
            "application_level": [
                "Implement response caching for repeated queries",
                "Use streaming responses for long outputs",
                "Keep model warm with periodic health checks",
                "Batch multiple requests when possible"
            ],
            "ollama_specific": [
                "Set OLLAMA_NUM_PARALLEL=1 for single requests",
                "Configure OLLAMA_MAX_LOADED_MODELS=1",
                "Use OLLAMA_FLASH_ATTENTION=1 if supported",
                "Set appropriate OLLAMA_HOST and OLLAMA_ORIGINS"
            ]
        },
        "expected_performance": {
            "first_request": "10-30 seconds (cold start)",
            "subsequent_requests": "2-10 seconds",
            "short_responses": "1-5 seconds",
            "long_responses": "5-15 seconds",
            "factors": [
                "Model size (8B parameters = slower)",
                "Response length (more tokens = more time)",
                "Hardware specs (CPU speed, RAM amount)",
                "System load (other running applications)"
            ]
        }
    }