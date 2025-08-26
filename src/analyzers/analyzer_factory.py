"""
Analyzer Factory for Craftbug Agentic System.
This module provides a unified interface for creating and managing different analyzer types.
"""

import logging
from typing import Dict, Type, Optional, Any
from enum import Enum

from config.settings import get_settings
from src.core.base_analyzer import BaseAnalyzer
from src.core.exceptions import ConfigurationError
from .craft_bug_analyzer import CraftBugAnalyzer
from .enhanced_craft_bug_analyzer import EnhancedCraftBugAnalyzer


class AnalyzerType(Enum):
    """Enumeration of available analyzer types."""
    CRAFT_BUG = "craft_bug"
    ENHANCED_CRAFT_BUG = "enhanced_craft_bug"
    LEGACY = "legacy"


class AnalyzerFactory:
    """Factory for creating and managing analyzers."""
    
    def __init__(self, settings=None):
        """Initialize the analyzer factory."""
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Register available analyzers
        self._analyzers: Dict[AnalyzerType, Type[BaseAnalyzer]] = {
            AnalyzerType.CRAFT_BUG: CraftBugAnalyzer,
            AnalyzerType.ENHANCED_CRAFT_BUG: EnhancedCraftBugAnalyzer,
        }
        
        # Cache for analyzer instances
        self._analyzer_cache: Dict[AnalyzerType, BaseAnalyzer] = {}
    
    def get_analyzer(self, analyzer_type: AnalyzerType) -> BaseAnalyzer:
        """Get an analyzer instance of the specified type."""
        try:
            # Check cache first
            if analyzer_type in self._analyzer_cache:
                return self._analyzer_cache[analyzer_type]
            
            # Create new instance if not cached
            if analyzer_type not in self._analyzers:
                raise ConfigurationError(f"Unknown analyzer type: {analyzer_type}")
            
            analyzer_class = self._analyzers[analyzer_type]
            analyzer = analyzer_class(self.settings)
            
            # Cache the instance
            self._analyzer_cache[analyzer_type] = analyzer
            
            self.logger.info(f"Created analyzer: {analyzer_type.value}")
            return analyzer
            
        except Exception as e:
            self.logger.error(f"Failed to create analyzer {analyzer_type.value}: {e}")
            raise ConfigurationError(f"Failed to create analyzer: {e}")
    
    def get_available_analyzers(self) -> Dict[str, str]:
        """Get a list of available analyzers with descriptions."""
        return {
            analyzer_type.value: self._get_analyzer_description(analyzer_type)
            for analyzer_type in self._analyzers.keys()
        }
    
    def _get_analyzer_description(self, analyzer_type: AnalyzerType) -> str:
        """Get description for an analyzer type."""
        descriptions = {
            AnalyzerType.CRAFT_BUG: "Basic craft bug analyzer with JSON-first approach",
            AnalyzerType.ENHANCED_CRAFT_BUG: "Enhanced craft bug analyzer with service layer architecture",
        }
        return descriptions.get(analyzer_type, "No description available")
    
    def clear_cache(self):
        """Clear the analyzer cache."""
        self._analyzer_cache.clear()
        self.logger.info("Analyzer cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_analyzers": len(self._analyzer_cache),
            "available_analyzers": len(self._analyzers),
            "cache_keys": list(self._analyzer_cache.keys())
        }
    
    def register_analyzer(self, analyzer_type: AnalyzerType, analyzer_class: Type[BaseAnalyzer]):
        """Register a new analyzer type."""
        if not issubclass(analyzer_class, BaseAnalyzer):
            raise ConfigurationError("Analyzer class must inherit from BaseAnalyzer")
        
        self._analyzers[analyzer_type] = analyzer_class
        self.logger.info(f"Registered new analyzer: {analyzer_type.value}")
    
    def unregister_analyzer(self, analyzer_type: AnalyzerType):
        """Unregister an analyzer type."""
        if analyzer_type in self._analyzers:
            del self._analyzers[analyzer_type]
            if analyzer_type in self._analyzer_cache:
                del self._analyzer_cache[analyzer_type]
            self.logger.info(f"Unregistered analyzer: {analyzer_type.value}")


# Global factory instance
_analyzer_factory: Optional[AnalyzerFactory] = None


def get_analyzer_factory(settings=None) -> AnalyzerFactory:
    """Get the global analyzer factory instance."""
    global _analyzer_factory
    if _analyzer_factory is None:
        _analyzer_factory = AnalyzerFactory(settings)
    return _analyzer_factory


def create_analyzer(analyzer_type: str, settings=None) -> BaseAnalyzer:
    """Create an analyzer of the specified type."""
    factory = get_analyzer_factory(settings)
    
    try:
        analyzer_enum = AnalyzerType(analyzer_type)
        return factory.get_analyzer(analyzer_enum)
    except ValueError:
        raise ConfigurationError(f"Invalid analyzer type: {analyzer_type}")


def get_available_analyzers(settings=None) -> Dict[str, str]:
    """Get available analyzers."""
    factory = get_analyzer_factory(settings)
    return factory.get_available_analyzers()
