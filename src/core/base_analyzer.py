"""
Base analyzer class for Craftbug Agentic System.
This module provides the foundation for all analyzer implementations.
"""

import os
import json
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pathlib import Path

from openai import AsyncOpenAI

from config.settings import get_settings
from config.constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from .exceptions import ConfigurationError, LLMError, AnalysisError
from .types import BugData, StepData, AnalysisResult, LLMResponse


class BaseAnalyzer(ABC):
    """Abstract base class for all analyzers in the system."""
    
    def __init__(self, settings=None):
        """Initialize the base analyzer with configuration."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate configuration
        if not self.settings.validate():
            print("⚠️ Configuration validation failed - continuing with warnings")
        
        # Initialize LLM client
        self.llm_client = self._setup_llm_client()
        
        # Initialize counters for debugging
        self.debug_counters = {
            "api_calls": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "bugs_detected": 0,
            "errors": 0
        }
    
    def _setup_llm_client(self) -> AsyncOpenAI:
        """Setup the OpenAI client with configuration."""
        try:
            return AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        except Exception as e:
            raise ConfigurationError(f"Failed to setup LLM client: {e}")
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> AnalysisResult:
        """Abstract method that must be implemented by subclasses."""
        pass
    
    async def _make_llm_call(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Make a call to the LLM with proper error handling."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            self.debug_counters["api_calls"] += 1
            
            response = await self.llm_client.chat.completions.create(
                model=self.settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=self.settings.OPENAI_MAX_TOKENS,
                temperature=self.settings.OPENAI_TEMPERATURE,
                **kwargs
            )
            
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            self.logger.info(f"LLM call successful: {len(content)} chars, {tokens_used} tokens")
            
            return LLMResponse(
                content=content,
                model=self.settings.OPENAI_MODEL,
                tokens_used=tokens_used,
                response_time=response_time,
                success=True
            )
            
        except Exception as e:
            self.debug_counters["errors"] += 1
            self.logger.error(f"LLM call failed: {e}")
            
            return LLMResponse(
                content="",
                model=self.settings.OPENAI_MODEL,
                tokens_used=0,
                response_time=asyncio.get_event_loop().time() - start_time,
                success=False,
                error=str(e)
            )
    
    def _validate_bug_data(self, bug_data: Dict[str, Any]) -> bool:
        """Validate bug data structure."""
        required_fields = ["title", "type", "severity", "confidence"]
        return all(field in bug_data for field in required_fields)
    
    def _normalize_bug_data(self, bug_data: Dict[str, Any]) -> BugData:
        """Normalize bug data to standard format."""
        return BugData(
            title=bug_data.get("title", "Untitled"),
            type=bug_data.get("type", "Visual"),
            severity=bug_data.get("severity", "Yellow"),
            confidence=bug_data.get("confidence", "Medium"),
            description=bug_data.get("description", ""),
            expected=bug_data.get("expected", ""),
            actual=bug_data.get("actual", ""),
            ui_path=bug_data.get("ui_path", "Not Observable"),
            screen_position=bug_data.get("screen_position", "Center"),
            visual_analysis=bug_data.get("visual_analysis", {}),
            developer_action=bug_data.get("developer_action", {}),
            design_system_compliance=bug_data.get("design_system_compliance", {}),
            persona_impact=bug_data.get("persona_impact", {}),
            screenshot_paths=bug_data.get("screenshot_paths", []),
            affected_steps=bug_data.get("affected_steps", []),
            bug_category=bug_data.get("bug_category")
        )
    
    def _try_parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Try to parse JSON from text with multiple fallback strategies."""
        # Try direct JSON parsing
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        
        # Try to extract JSON from markdown code blocks
        try:
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end > start:
                    json_text = text[start:end].strip()
                    data = json.loads(json_text)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        
        # Try to find JSON object in the text
        try:
            if '{"bugs_strong"' in text:
                start = text.find('{"bugs_strong"')
                brace_count = 0
                end = start
                for i, char in enumerate(text[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                if end > start:
                    json_text = text[start:end]
                    data = json.loads(json_text)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        
        return None
    
    def get_debug_counters(self) -> Dict[str, int]:
        """Get current debug counters."""
        return self.debug_counters.copy()
    
    def reset_debug_counters(self):
        """Reset debug counters."""
        self.debug_counters = {
            "api_calls": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "bugs_detected": 0,
            "errors": 0
        }
