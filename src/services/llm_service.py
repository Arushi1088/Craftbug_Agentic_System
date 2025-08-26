"""
LLM Service for Craftbug Agentic System.
This module handles all interactions with the OpenAI API.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI

from config.settings import get_settings
from src.core.exceptions import LLMError
from src.core.types import LLMResponse


class LLMService:
    """Service for handling LLM interactions."""
    
    def __init__(self, settings=None):
        """Initialize the LLM service."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize OpenAI client
        self.client = self._setup_client()
        
        # Performance tracking
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_response_time": 0.0
        }
    
    def _setup_client(self) -> AsyncOpenAI:
        """Setup the OpenAI client."""
        try:
            return AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        except Exception as e:
            raise LLMError(f"Failed to setup OpenAI client: {e}")
    
    async def generate_completion(
        self, 
        messages: List[Dict], 
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a completion using the LLM."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.stats["total_calls"] += 1
            
            # Use provided parameters or defaults
            model = model or self.settings.OPENAI_MODEL
            max_tokens = max_tokens or self.settings.OPENAI_MAX_TOKENS
            temperature = temperature or self.settings.OPENAI_TEMPERATURE
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            # Update stats
            self.stats["successful_calls"] += 1
            self.stats["total_tokens"] += tokens_used
            self.stats["total_response_time"] += response_time
            
            self.logger.info(f"LLM call successful: {len(content)} chars, {tokens_used} tokens, {response_time:.2f}s")
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            self.stats["failed_calls"] += 1
            self.logger.error(f"LLM call failed: {e}")
            
            return LLMResponse(
                content="",
                model=model or self.settings.OPENAI_MODEL,
                tokens_used=0,
                response_time=asyncio.get_event_loop().time() - start_time,
                success=False,
                error=str(e)
            )
    
    async def analyze_with_images(
        self, 
        prompt: str, 
        images: List[Dict], 
        **kwargs
    ) -> LLMResponse:
        """Analyze images with a prompt using multimodal LLM."""
        try:
            # Build messages with interleaved images
            messages = self._build_multimodal_messages(prompt, images)
            
            return await self.generate_completion(messages, **kwargs)
            
        except Exception as e:
            raise LLMError(f"Image analysis failed: {e}")
    
    def _build_multimodal_messages(self, prompt: str, images: List[Dict]) -> List[Dict]:
        """Build messages for multimodal analysis."""
        messages = [{"role": "user", "content": prompt}]
        
        for image_data in images:
            # Add caption if provided
            if "caption" in image_data:
                messages.append({"role": "user", "content": image_data["caption"]})
            
            # Add image
            image_url = f"data:image/jpeg;base64,{image_data['base64']}"
            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            })
        
        return messages
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        stats = self.stats.copy()
        if stats["total_calls"] > 0:
            stats["success_rate"] = stats["successful_calls"] / stats["total_calls"]
            stats["avg_response_time"] = stats["total_response_time"] / stats["successful_calls"]
        return stats
    
    def reset_stats(self):
        """Reset service statistics."""
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_response_time": 0.0
        }
