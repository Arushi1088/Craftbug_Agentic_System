"""
Validation Service for Craftbug Agentic System.
This module handles data validation, JSON parsing, and bug data normalization.
"""

import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import asdict

from config.constants import BUG_TYPES, SEVERITY_LEVELS, CONFIDENCE_LEVELS, DEFAULT_UI_PATH
from src.core.exceptions import ValidationError, ParsingError
from src.core.types import BugData


class ValidationService:
    """Service for handling data validation and parsing."""
    
    def __init__(self):
        """Initialize the validation service."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Performance tracking
        self.stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "total_parses": 0,
            "successful_parses": 0,
            "failed_parses": 0
        }
    
    def validate_bug_data(self, bug_data: Dict[str, Any]) -> bool:
        """Validate that bug data contains required fields."""
        self.stats["total_validations"] += 1
        
        try:
            # Check required fields
            required_fields = ["title", "type", "severity", "confidence"]
            missing_fields = [field for field in required_fields if not bug_data.get(field)]
            
            if missing_fields:
                self.logger.warning(f"Missing required fields: {missing_fields}")
                self.stats["failed_validations"] += 1
                return False
            
            # Validate field values
            if bug_data.get("type") not in BUG_TYPES:
                self.logger.warning(f"Invalid bug type: {bug_data.get('type')}")
                self.stats["failed_validations"] += 1
                return False
            
            if bug_data.get("severity") not in SEVERITY_LEVELS:
                self.logger.warning(f"Invalid severity: {bug_data.get('severity')}")
                self.stats["failed_validations"] += 1
                return False
            
            if bug_data.get("confidence") not in CONFIDENCE_LEVELS:
                self.logger.warning(f"Invalid confidence: {bug_data.get('confidence')}")
                self.stats["failed_validations"] += 1
                return False
            
            self.stats["successful_validations"] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            self.stats["failed_validations"] += 1
            return False
    
    def parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response with multiple fallback strategies."""
        self.stats["total_parses"] += 1
        
        try:
            # Try direct JSON parsing
            data = json.loads(text)
            if isinstance(data, dict):
                self.stats["successful_parses"] += 1
                return data
        except Exception:
            pass
        
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                if end > start:
                    json_text = text[start:end].strip()
                    data = json.loads(json_text)
                    if isinstance(data, dict):
                        self.stats["successful_parses"] += 1
                        return data
        except Exception:
            pass
        
        try:
            # Try to find JSON object in the text
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
                        self.stats["successful_parses"] += 1
                        return data
        except Exception:
            pass
        
        self.stats["failed_parses"] += 1
        return None
    
    def normalize_bug_data(self, bug_data: Dict[str, Any], bug_category: str = "unknown") -> BugData:
        """Normalize bug data to standard format."""
        try:
            return BugData(
                title=bug_data.get("title", "Untitled"),
                type=bug_data.get("type", "Visual"),
                severity=bug_data.get("severity", "Yellow"),
                confidence=bug_data.get("confidence", "Medium"),
                description=bug_data.get("description", ""),
                expected=bug_data.get("expected", ""),
                actual=bug_data.get("actual", ""),
                ui_path=bug_data.get("ui_path", DEFAULT_UI_PATH),
                screen_position=bug_data.get("screen_position", "Center"),
                visual_analysis=bug_data.get("visual_analysis", {}),
                developer_action=bug_data.get("developer_action", {}),
                design_system_compliance=bug_data.get("design_system_compliance", {}),
                persona_impact=bug_data.get("persona_impact", {}),
                screenshot_paths=bug_data.get("screenshot_paths", []),
                affected_steps=bug_data.get("affected_steps", []),
                bug_category=bug_category
            )
        except Exception as e:
            raise ValidationError(f"Failed to normalize bug data: {e}")
    
    def fill_missing_fields(self, bug_data: Dict[str, Any], category: str = "minor") -> Dict[str, Any]:
        """Fill missing fields with appropriate defaults based on category."""
        filled_data = bug_data.copy()
        
        if category == "minor":
            # For minor bugs, be more lenient with defaults
            if not filled_data.get("title"):
                filled_data["title"] = f"Minor {filled_data.get('type', 'Visual')} Issue"
            if not filled_data.get("type"):
                filled_data["type"] = "Visual"
            if not filled_data.get("severity"):
                filled_data["severity"] = "Yellow"
            if not filled_data.get("confidence"):
                filled_data["confidence"] = "Low"
            if not filled_data.get("ui_path"):
                filled_data["ui_path"] = DEFAULT_UI_PATH
        
        return filled_data
    
    def validate_screenshot_paths(self, paths: List[str]) -> List[str]:
        """Validate and filter screenshot paths."""
        valid_paths = []
        
        for path in paths:
            if path and isinstance(path, str):
                valid_paths.append(path)
        
        return valid_paths
    
    def create_deduplication_key(self, bug: BugData) -> str:
        """Create a unique key for deduplication."""
        # Use a composite key for better deduplication
        element_identifier = bug.ui_path if bug.ui_path != DEFAULT_UI_PATH else "unknown"
        primary_step = bug.affected_steps[0].get("name", "unknown") if bug.affected_steps else "unknown"
        rounded_position = bug.screen_position.lower() if bug.screen_position else "center"
        
        return f"{bug.type.lower()}|{element_identifier.lower()}|{primary_step.lower()}|{rounded_position}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        stats = self.stats.copy()
        if stats["total_validations"] > 0:
            stats["validation_success_rate"] = stats["successful_validations"] / stats["total_validations"]
        if stats["total_parses"] > 0:
            stats["parse_success_rate"] = stats["successful_parses"] / stats["total_parses"]
        return stats
    
    def reset_stats(self):
        """Reset service statistics."""
        self.stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "total_parses": 0,
            "successful_parses": 0,
            "failed_parses": 0
        }
