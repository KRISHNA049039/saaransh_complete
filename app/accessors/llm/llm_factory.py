from typing import Optional
from app.accessors.llm.llm_accessor import LLMAccessor
from app.accessors.llm.litellm_accessor import LiteLLMAccessor
from app.accessors.llm.local_llama_accessor import LocalLlamaAccessor
from app.settings import settings
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory class for creating LLM accessor instances"""
    
    @staticmethod
    def get_llm_accessor(llm_sdk: Optional[str] = None) -> LLMAccessor:
        """
        Factory method to get appropriate LLM accessor based on configuration
        
        Args:
            llm_sdk: Override for LLM SDK (optional, uses settings if not provided)
            
        Returns:
            Configured LLM accessor instance
        """
        
        llm_sdk = llm_sdk or settings.LLM_SDK.strip().lower() or "litellm"
        
        logger.info(f"Creating LLM accessor for SDK: {llm_sdk}")

        if llm_sdk == "litellm":
            logger.info("Using LiteLLM accessor (remote)")
            return LiteLLMAccessor()
        
        elif llm_sdk == "local_llama":
            logger.info("Using Local Llama accessor")
            return LocalLlamaAccessor()
        
        else:
            logger.error(f"Unknown LLM SDK: {llm_sdk}")
            raise ValueError(f"Unknown LLM sdk: {llm_sdk}")


def get_llm_accessor(llm_sdk: Optional[str] = None) -> LLMAccessor:
    """
    Factory function to get appropriate LLM accessor based on configuration
    
    Args:
        llm_sdk: Override for LLM SDK (optional, uses settings if not provided)
        
    Returns:
        Configured LLM accessor instance
    """
    
    llm_sdk = llm_sdk or settings.LLM_SDK.strip().lower() or "litellm"
    
    logger.info(f"Creating LLM accessor for SDK: {llm_sdk}")

    if llm_sdk == "litellm":
        logger.info("Using LiteLLM accessor (remote)")
        return LiteLLMAccessor()
    
    elif llm_sdk == "local_llama":
        logger.info("Using Local Llama accessor")
        return LocalLlamaAccessor()
    
    else:
        logger.error(f"Unknown LLM SDK: {llm_sdk}")
        raise ValueError(f"Unknown LLM sdk: {llm_sdk}")


async def test_llm_factory():
    """Test function to verify LLM factory works with different providers"""
    
    print("🧪 Testing LLM Factory...")
    
    # Test LiteLLM (existing)
    try:
        litellm_accessor = get_llm_accessor("litellm")
        print(f"✅ LiteLLM accessor created: {type(litellm_accessor).__name__}")
    except Exception as e:
        print(f"❌ LiteLLM accessor failed: {e}")
    
    # Test Local Llama (new)
    try:
        local_accessor = get_llm_accessor("local_llama")
        print(f"✅ Local Llama accessor created: {type(local_accessor).__name__}")
        
        # Test health check
        if hasattr(local_accessor, 'health_check'):
            healthy = await local_accessor.health_check()
            print(f"🏥 Local Llama health: {'HEALTHY' if healthy else 'UNHEALTHY'}")
            
        await local_accessor.close()
        
    except Exception as e:
        print(f"❌ Local Llama accessor failed: {e}")
    
    # Test invalid SDK
    try:
        invalid_accessor = get_llm_accessor("invalid_sdk")
        print(f"❌ Should have failed for invalid SDK")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid SDK: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_llm_factory())
