"""
LLM Service

Provides dynamic model selection and management for frontend integration.
Supports both local and remote LLM models with runtime switching.
"""

import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from app.accessors.llm.llm_factory import get_llm_accessor
from app.accessors.llm.local_llama_accessor import LocalLlamaAccessor
from app.accessors.llm.litellm_accessor import LiteLLMAccessor
from app.settings import settings

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Available model types"""
    LOCAL_LLAMA = "local_llama"
    REMOTE_LLM = "litellm"


class ModelInfo(BaseModel):
    """Model information for frontend display"""
    id: str
    name: str
    type: ModelType
    size: Optional[str] = None
    description: str
    available: bool
    performance: str  # "fast", "medium", "slow"
    quality: str     # "high", "medium", "basic"
    use_cases: List[str]


class LLMService:
    """Service for managing LLM models and dynamic selection"""
    
    def __init__(self):
        self.available_models: Dict[str, ModelInfo] = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available models configuration"""
        
        # Local Llama models
        local_models = [
            ModelInfo(
                id="llama3.1:8b",
                name="Llama 3.1 8B (Local)",
                type=ModelType.LOCAL_LLAMA,
                size="4.9 GB",
                description="High-quality local model with excellent reasoning",
                available=False,  # Will be checked dynamically
                performance="slow",
                quality="high",
                use_cases=["Complex analysis", "Detailed summaries", "Creative writing"]
            ),
            ModelInfo(
                id="llama3.1:3b",
                name="Llama 3.1 3B (Local)",
                type=ModelType.LOCAL_LLAMA,
                size="2.0 GB",
                description="Fast local model optimized for quick responses",
                available=False,  # Will be checked dynamically
                performance="fast",
                quality="medium",
                use_cases=["Quick summaries", "Simple Q&A", "Task enhancement"]
            )
        ]
        
        # Remote LLM models
        remote_models = [
            ModelInfo(
                id="gemini/gemini-2.5-flash",
                name="Gemini 2.5 Flash",
                type=ModelType.REMOTE_LLM,
                description="Google's fast and efficient model",
                available=True,  # Assume available if API key is set
                performance="fast",
                quality="high",
                use_cases=["All tasks", "Real-time chat", "Analysis"]
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                type=ModelType.REMOTE_LLM,
                description="OpenAI's balanced model for general use",
                available=True,
                performance="medium",
                quality="high",
                use_cases=["General tasks", "Summaries", "Q&A"]
            ),
            ModelInfo(
                id="gpt-4",
                name="GPT-4",
                type=ModelType.REMOTE_LLM,
                description="OpenAI's most capable model",
                available=True,
                performance="slow",
                quality="high",
                use_cases=["Complex analysis", "Research", "Creative tasks"]
            )
        ]
        
        # Store all models
        for model in local_models + remote_models:
            self.available_models[model.id] = model
    
    async def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models with current status"""
        
        # Check local model availability
        if settings.LOCAL_LLM_ENABLED:
            try:
                local_accessor = LocalLlamaAccessor()
                local_models = await local_accessor.get_available_models()
                await local_accessor.close()
                
                # Update availability status
                for model_id in self.available_models:
                    if self.available_models[model_id].type == ModelType.LOCAL_LLAMA:
                        model_name = model_id
                        self.available_models[model_id].available = model_name in local_models
                        
            except Exception as e:
                logger.warning(f"Could not check local models: {e}")
                # Mark all local models as unavailable
                for model_id in self.available_models:
                    if self.available_models[model_id].type == ModelType.LOCAL_LLAMA:
                        self.available_models[model_id].available = False
        
        # Check remote model availability (basic check)
        has_gemini_key = bool(getattr(settings, 'GEMINI_API_KEY', ''))
        has_openai_key = bool(getattr(settings, 'OPENAI_API_KEY', ''))
        
        for model_id in self.available_models:
            model = self.available_models[model_id]
            if model.type == ModelType.REMOTE_LLM:
                if "gemini" in model_id.lower():
                    model.available = has_gemini_key
                elif "gpt" in model_id.lower():
                    model.available = has_openai_key
        
        return list(self.available_models.values())
    
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        
        if model_id not in self.available_models:
            return None
        
        model = self.available_models[model_id]
        
        # Check current availability
        if model.type == ModelType.LOCAL_LLAMA and settings.LOCAL_LLM_ENABLED:
            try:
                local_accessor = LocalLlamaAccessor()
                local_models = await local_accessor.get_available_models()
                model.available = model_id in local_models
                await local_accessor.close()
            except Exception:
                model.available = False
        
        return model
    
    async def create_llm_accessor(self, model_id: Optional[str] = None) -> Any:
        """Create LLM accessor for specified model"""
        
        if not model_id:
            # Use default from settings
            return get_llm_accessor()
        
        if model_id not in self.available_models:
            raise ValueError(f"Unknown model: {model_id}")
        
        model_info = self.available_models[model_id]
        
        if model_info.type == ModelType.LOCAL_LLAMA:
            if not settings.LOCAL_LLM_ENABLED:
                raise ValueError("Local LLM is disabled")
            
            # Create local accessor with specific model
            accessor = LocalLlamaAccessor()
            accessor.model = model_id  # Override model
            return accessor
        
        elif model_info.type == ModelType.REMOTE_LLM:
            # Create remote accessor
            return LiteLLMAccessor()
        
        else:
            raise ValueError(f"Unsupported model type: {model_info.type}")
    
    async def generate_response(
        self,
        model_id: str,
        content: str,
        user_prompt: str,
        system_prompt: str = "",
        **kwargs
    ) -> str:
        """Generate response using specified model"""
        
        accessor = await self.create_llm_accessor(model_id)
        
        try:
            if hasattr(accessor, 'get_response'):
                return await accessor.get_response(
                    model=model_id,
                    content=content,
                    user_prompt=user_prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
            else:
                raise ValueError(f"Accessor does not support get_response method")
        
        finally:
            if hasattr(accessor, 'close'):
                await accessor.close()
    
    async def benchmark_model(self, model_id: str) -> Dict[str, Any]:
        """Benchmark a specific model's performance"""
        
        if model_id not in self.available_models:
            raise ValueError(f"Unknown model: {model_id}")
        
        model_info = self.available_models[model_id]
        
        if not model_info.available:
            return {
                "model_id": model_id,
                "status": "unavailable",
                "error": "Model not available"
            }
        
        try:
            import time
            
            accessor = await self.create_llm_accessor(model_id)
            
            # Simple benchmark test
            start_time = time.time()
            
            response = await accessor.get_response(
                model=model_id,
                content="",
                user_prompt="Say 'Hello' in one word.",
                system_prompt="Respond with exactly one word."
            )
            
            duration = time.time() - start_time
            
            if hasattr(accessor, 'close'):
                await accessor.close()
            
            return {
                "model_id": model_id,
                "status": "success",
                "response_time": round(duration, 2),
                "response_length": len(response),
                "performance_rating": (
                    "excellent" if duration < 3 else
                    "good" if duration < 8 else
                    "acceptable" if duration < 15 else
                    "slow"
                )
            }
            
        except Exception as e:
            return {
                "model_id": model_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_recommended_model(self, use_case: str = "general") -> Optional[str]:
        """Get recommended model for specific use case"""
        
        use_case_mapping = {
            "quick_summary": ["llama3.1:3b", "gemini/gemini-2.5-flash"],
            "detailed_analysis": ["llama3.1:8b", "gpt-4"],
            "real_time_chat": ["gemini/gemini-2.5-flash", "gpt-3.5-turbo"],
            "task_enhancement": ["llama3.1:3b", "gemini/gemini-2.5-flash"],
            "general": ["gemini/gemini-2.5-flash", "llama3.1:8b", "gpt-3.5-turbo"]
        }
        
        candidates = use_case_mapping.get(use_case, use_case_mapping["general"])
        
        # Return first available model
        for model_id in candidates:
            if model_id in self.available_models and self.available_models[model_id].available:
                return model_id
        
        return None


# Global service instance
llm_service = LLMService()


async def get_llm_service() -> LLMService:
    """Dependency injection for LLM service"""
    return llm_service