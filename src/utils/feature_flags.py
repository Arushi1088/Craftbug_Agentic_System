#!/usr/bin/env python3
"""
Feature Flags System for Safe Refactoring
Controls which parts of the system use new vs legacy architecture
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class FeatureFlags:
    """
    Feature flags for controlling system behavior during refactoring.
    All flags default to False (use legacy system) for safety.
    """
    
    # Core architecture flags
    USE_NEW_ARCHITECTURE = False
    USE_NEW_API_ROUTES = False
    USE_NEW_SERVICES = False
    
    # Component-specific flags
    USE_NEW_LOGGING = False
    USE_NEW_CONFIG = False
    USE_NEW_REPORTS = False
    USE_NEW_EXECUTOR = False
    USE_NEW_INTEGRATIONS = False
    
    # Testing flags
    ENABLE_AB_TESTING = False
    ENABLE_MONITORING = False
    
    # Rollback flags
    FORCE_LEGACY_MODE = False
    
    @classmethod
    def load_from_env(cls):
        """Load feature flags from environment variables"""
        try:
            cls.USE_NEW_ARCHITECTURE = os.getenv('USE_NEW_ARCHITECTURE', 'false').lower() == 'true'
            cls.USE_NEW_API_ROUTES = os.getenv('USE_NEW_API_ROUTES', 'false').lower() == 'true'
            cls.USE_NEW_SERVICES = os.getenv('USE_NEW_SERVICES', 'false').lower() == 'true'
            cls.USE_NEW_LOGGING = os.getenv('USE_NEW_LOGGING', 'false').lower() == 'true'
            cls.USE_NEW_CONFIG = os.getenv('USE_NEW_CONFIG', 'false').lower() == 'true'
            cls.USE_NEW_REPORTS = os.getenv('USE_NEW_REPORTS', 'false').lower() == 'true'
            cls.USE_NEW_EXECUTOR = os.getenv('USE_NEW_EXECUTOR', 'false').lower() == 'true'
            cls.USE_NEW_INTEGRATIONS = os.getenv('USE_NEW_INTEGRATIONS', 'false').lower() == 'true'
            cls.ENABLE_AB_TESTING = os.getenv('ENABLE_AB_TESTING', 'false').lower() == 'true'
            cls.ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'false').lower() == 'true'
            cls.FORCE_LEGACY_MODE = os.getenv('FORCE_LEGACY_MODE', 'false').lower() == 'true'
            
            logger.info("Feature flags loaded from environment variables")
            cls.log_current_state()
            
        except Exception as e:
            logger.error(f"Failed to load feature flags from environment: {e}")
            logger.info("Using default feature flags (all legacy)")
    
    @classmethod
    def enable_new_architecture(cls):
        """Gradually enable new architecture"""
        cls.USE_NEW_ARCHITECTURE = True
        logger.info("New architecture enabled")
    
    @classmethod
    def enable_new_api_routes(cls):
        """Enable new API routes"""
        cls.USE_NEW_API_ROUTES = True
        logger.info("New API routes enabled")
    
    @classmethod
    def enable_new_services(cls):
        """Enable new services"""
        cls.USE_NEW_SERVICES = True
        logger.info("New services enabled")
    
    @classmethod
    def enable_new_logging(cls):
        """Enable new logging system"""
        cls.USE_NEW_LOGGING = True
        logger.info("New logging system enabled")
    
    @classmethod
    def enable_new_config(cls):
        """Enable new configuration system"""
        cls.USE_NEW_CONFIG = True
        logger.info("New configuration system enabled")
    
    @classmethod
    def enable_new_reports(cls):
        """Enable new report generation"""
        cls.USE_NEW_REPORTS = True
        logger.info("New report generation enabled")
    
    @classmethod
    def enable_new_executor(cls):
        """Enable new scenario executor"""
        cls.USE_NEW_EXECUTOR = True
        logger.info("New scenario executor enabled")
    
    @classmethod
    def enable_new_integrations(cls):
        """Enable new integrations"""
        cls.USE_NEW_INTEGRATIONS = True
        logger.info("New integrations enabled")
    
    @classmethod
    def enable_ab_testing(cls):
        """Enable A/B testing"""
        cls.ENABLE_AB_TESTING = True
        logger.info("A/B testing enabled")
    
    @classmethod
    def enable_monitoring(cls):
        """Enable monitoring"""
        cls.ENABLE_MONITORING = True
        logger.info("Monitoring enabled")
    
    @classmethod
    def force_legacy_mode(cls):
        """Force legacy mode (emergency rollback)"""
        cls.FORCE_LEGACY_MODE = True
        cls.USE_NEW_ARCHITECTURE = False
        cls.USE_NEW_API_ROUTES = False
        cls.USE_NEW_SERVICES = False
        cls.USE_NEW_LOGGING = False
        cls.USE_NEW_CONFIG = False
        cls.USE_NEW_REPORTS = False
        cls.USE_NEW_EXECUTOR = False
        cls.USE_NEW_INTEGRATIONS = False
        cls.ENABLE_AB_TESTING = False
        cls.ENABLE_MONITORING = False
        logger.warning("Legacy mode forced - all new features disabled")
    
    @classmethod
    def should_use_new_system(cls, component: str) -> bool:
        """Check if new system should be used for a specific component"""
        if cls.FORCE_LEGACY_MODE:
            return False
        
        component_flags = {
            'architecture': cls.USE_NEW_ARCHITECTURE,
            'api_routes': cls.USE_NEW_API_ROUTES,
            'services': cls.USE_NEW_SERVICES,
            'logging': cls.USE_NEW_LOGGING,
            'config': cls.USE_NEW_CONFIG,
            'reports': cls.USE_NEW_REPORTS,
            'executor': cls.USE_NEW_EXECUTOR,
            'integrations': cls.USE_NEW_INTEGRATIONS
        }
        
        return component_flags.get(component, False)
    
    @classmethod
    def get_current_state(cls) -> Dict[str, Any]:
        """Get current state of all feature flags"""
        return {
            'timestamp': datetime.now().isoformat(),
            'flags': {
                'USE_NEW_ARCHITECTURE': cls.USE_NEW_ARCHITECTURE,
                'USE_NEW_API_ROUTES': cls.USE_NEW_API_ROUTES,
                'USE_NEW_SERVICES': cls.USE_NEW_SERVICES,
                'USE_NEW_LOGGING': cls.USE_NEW_LOGGING,
                'USE_NEW_CONFIG': cls.USE_NEW_CONFIG,
                'USE_NEW_REPORTS': cls.USE_NEW_REPORTS,
                'USE_NEW_EXECUTOR': cls.USE_NEW_EXECUTOR,
                'USE_NEW_INTEGRATIONS': cls.USE_NEW_INTEGRATIONS,
                'ENABLE_AB_TESTING': cls.ENABLE_AB_TESTING,
                'ENABLE_MONITORING': cls.ENABLE_MONITORING,
                'FORCE_LEGACY_MODE': cls.FORCE_LEGACY_MODE
            }
        }
    
    @classmethod
    def log_current_state(cls):
        """Log current feature flag state"""
        state = cls.get_current_state()
        logger.info("Current feature flag state:")
        for flag_name, flag_value in state['flags'].items():
            status = "✅ ENABLED" if flag_value else "❌ DISABLED"
            logger.info(f"   {flag_name}: {status}")
    
    @classmethod
    def save_state_to_file(cls, filename: str = None):
        """Save current state to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feature_flags_state_{timestamp}.json"
        
        import json
        state = cls.get_current_state()
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Feature flags state saved to: {filename}")
        return filename

# Initialize feature flags
FeatureFlags.load_from_env()
