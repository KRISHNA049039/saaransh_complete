"""
Local Llama Accessor

Integrates local Llama models via Ollama with the existing Saaransh LLM architecture.
Implements the LLMAccessor interface for seamless integration.
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any, Optional
from app.accessors.llm.llm_accessor import LLMAccessor
from app.settings import settings

logger = logging.getLogger(__name__)


class LocalLlamaAccessor(LLMAccessor):
    """Local Llama model accessor using Ollama runtime"""
    
    def __init__(self):
        """Initialize Local Llama accessor"""
        self.host = getattr(settings, 'LOCAL_LLM_HOST', 'localhost')
        self.port = getattr(settings, 'LOCAL_LLM_PORT', 11434)
        self.model = getattr(settings, 'LOCAL_LLM_MODEL', 'llama3.1:8b')
        self.base_url = f"http://{self.host}:{self.port}"
        self.timeout = getattr(settings, 'LOCAL_LLM_TIMEOUT', 60)
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
        logger.info(f"Initialized LocalLlamaAccessor: {self.base_url}, model: {self.model}")
    
    async def get_response(
        self,
        model: str,
        content: str,
        user_prompt: Optional[str] = None,
        system_prompt: str = "",
        use_tools: bool = False,
        tool_schemas=None,
        tool_registry=None,
    ) -> str:
        """
        Get response from local Llama model
        
        Args:
            model: Model name (will use configured local model)
            content: Main content/context for the LLM
            user_prompt: User's specific prompt/question
            system_prompt: System instructions
            use_tools: Whether to use tools (not supported in local mode)
            tool_schemas: Tool schemas (not supported in local mode)
            tool_registry: Tool registry (not supported in local mode)
            
        Returns:
            Generated response from the local Llama model
        """
        try:
            # Build the complete prompt
            full_prompt = self._build_prompt(content, user_prompt, system_prompt)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": getattr(settings, 'LOCAL_LLM_TEMPERATURE', 0.7),
                    "num_ctx": getattr(settings, 'LOCAL_LLM_CONTEXT_LENGTH', 8192),
                    "num_predict": getattr(settings, 'LOCAL_LLM_MAX_TOKENS', 4096),
                }
            }
            
            logger.info(f"Sending request to local Llama model: {self.model}")
            logger.debug(f"Prompt length: {len(full_prompt)} characters")
            
            # Make API call to Ollama
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                
                logger.info(f"Local Llama response received: {len(generated_text)} characters")
                return generated_text
            else:
                error_msg = f"Local Llama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except httpx.TimeoutException:
            error_msg = f"Local Llama request timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Local Llama request failed: {str(e)}")
            raise
    
    async def get_token_count(self, text: str) -> int:
        """
        Calculate token count for given text
        
        Note: This is an approximation since we don't have direct access
        to the tokenizer. Uses a rough estimate of ~4 characters per token.
        """
        # Rough approximation: ~4 characters per token for most models
        estimated_tokens = len(text) // 4
        
        logger.debug(f"Estimated token count for text ({len(text)} chars): {estimated_tokens}")
        return estimated_tokens
    
    def _build_prompt(self, content: str, user_prompt: Optional[str], system_prompt: str) -> str:
        """
        Build complete prompt from components
        
        Args:
            content: Main content/context
            user_prompt: User's specific question/request
            system_prompt: System instructions
            
        Returns:
            Complete formatted prompt
        """
        prompt_parts = []
        
        # Add system prompt if provided
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        # Add main content
        if content:
            prompt_parts.append(f"Context: {content}")
        
        # Add user prompt if provided
        if user_prompt:
            prompt_parts.append(f"User: {user_prompt}")
        else:
            # Default instruction if no specific user prompt
            prompt_parts.append("User: Please analyze the above content and provide a helpful summary.")
        
        # Add assistant prompt to encourage response
        prompt_parts.append("Assistant:")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        logger.debug(f"Built prompt with {len(prompt_parts)} parts, total length: {len(full_prompt)}")
        return full_prompt
    
    async def health_check(self) -> bool:
        """
        Check if local Llama service is available and responsive
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Check if Ollama is running
            response = await self.client.get(f"{self.base_url}/api/tags")
            
            if response.status_code == 200:
                tags_data = response.json()
                models = tags_data.get("models", [])
                
                # Check if our configured model is available
                model_available = any(
                    model.get("name") == self.model 
                    for model in models
                )
                
                if model_available:
                    logger.info(f"Local Llama health check passed: model {self.model} available")
                    return True
                else:
                    logger.warning(f"Local Llama model {self.model} not found in available models")
                    return False
            else:
                logger.warning(f"Local Llama health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Local Llama health check failed: {str(e)}")
            return False
    
    async def get_available_models(self) -> list:
        """
        Get list of available models from Ollama
        
        Returns:
            List of available model names
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            
            if response.status_code == 200:
                tags_data = response.json()
                models = [model.get("name", "") for model in tags_data.get("models", [])]
                logger.info(f"Available local models: {models}")
                return models
            else:
                logger.error(f"Failed to get available models: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get available models: {str(e)}")
            return []
    
    async def close(self):
        """Close HTTP client"""
        try:
            await self.client.aclose()
            logger.info("Local Llama accessor closed")
        except Exception as e:
            logger.error(f"Error closing Local Llama accessor: {str(e)}")
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            # Note: This won't work in async context, but provides cleanup hint
            if hasattr(self, 'client') and self.client:
                logger.debug("Local Llama accessor being garbage collected")
        except Exception:
            pass


# Utility functions for easy testing and debugging

async def test_local_llama():
    """Test function for local Llama integration"""
    accessor = LocalLlamaAccessor()
    
    try:
        # Health check
        print("🔍 Checking Local Llama health...")
        healthy = await accessor.health_check()
        print(f"✅ Health check: {'PASSED' if healthy else 'FAILED'}")
        
        if healthy:
            # Get available models
            models = await accessor.get_available_models()
            print(f"📋 Available models: {models}")
            
            # Test simple response
            print("🧪 Testing simple response...")
            response = await accessor.get_response(
                model="test",
                content="This is a test of the local Llama integration.",
                user_prompt="Please confirm that you received this message and are working correctly."
            )
            print(f"🤖 Response: {response[:200]}...")
            
            # Test token counting
            token_count = await accessor.get_token_count("This is a test message for token counting.")
            print(f"🔢 Token count test: {token_count} tokens")
            
        return healthy
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    finally:
        await accessor.close()


if __name__ == "__main__":
    # Run test if executed directly
    import asyncio
    asyncio.run(test_local_llama())