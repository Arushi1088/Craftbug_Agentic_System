#!/usr/bin/env python3
"""
Scenario Resolver Utility
Bulletproof scenario resolution for all supported formats
"""

import yaml
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def resolve_scenario(scenario_path: str, scenario_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve a scenario path + (optional) scenario ID and always return a dict with steps.
    If not found, raise a clear error.
    
    Supports multiple formats:
    1) Direct {steps: [...]}
    2) {scenarios: [{id: "1.1", steps:[...]}]}
    3) Tests format: {tests: {Name: {scenarios:[{steps:[...]}]}}}
    """
    if not scenario_path or not os.path.exists(scenario_path):
        raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

    try:
        with open(scenario_path, "r") as f:
            doc = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(f"Failed to parse YAML file {scenario_path}: {e}")

    if not isinstance(doc, dict):
        raise RuntimeError(f"Scenario file must contain a dictionary, got {type(doc)}")

    # 1) Direct {steps: [...]} format
    if "steps" in doc and isinstance(doc["steps"], list):
        logger.info(f"Found direct steps format in {scenario_path}")
        return doc

    # 2) {scenarios: [{id: "1.1", steps:[...]}]} format
    if isinstance(doc.get("scenarios"), list):
        scenarios_list = doc["scenarios"]
        
        if scenario_id:
            # Look for specific scenario ID
            for scenario in scenarios_list:
                if isinstance(scenario, dict) and str(scenario.get("id")) == str(scenario_id):
                    if "steps" not in scenario or not isinstance(scenario["steps"], list):
                        raise RuntimeError(f"Scenario id {scenario_id} found but has no valid steps")
                    logger.info(f"Found scenario {scenario_id} in {scenario_path}")
                    return scenario
            raise RuntimeError(f"Scenario id {scenario_id} not found in scenarios list")
        else:
            # No ID provided → take first scenario with steps
            for scenario in scenarios_list:
                if isinstance(scenario, dict) and "steps" in scenario and isinstance(scenario["steps"], list):
                    logger.info(f"Found first valid scenario in {scenario_path}")
                    return scenario
            raise RuntimeError("No scenario with valid steps found in 'scenarios' list")

    # 3) Tests format: {tests: {Name: {scenarios:[{steps:[...]}]}}}
    if isinstance(doc.get("tests"), dict):
        tests_dict = doc["tests"]
        
        for test_name, test_group in tests_dict.items():
            if isinstance(test_group, dict) and isinstance(test_group.get("scenarios"), list):
                for scenario in test_group["scenarios"]:
                    if isinstance(scenario, dict) and "steps" in scenario and isinstance(scenario["steps"], list):
                        logger.info(f"Found scenario in tests format: {test_name} in {scenario_path}")
                        return scenario
        raise RuntimeError("No scenario with valid steps found in 'tests' format")

    raise RuntimeError(f"Unsupported scenario format or missing 'steps' in {scenario_path}. Supported formats: direct steps, scenarios list, or tests format")

def _ensure_dict(name: str, obj: Any) -> Dict[str, Any]:
    """
    Guard function to ensure object is a valid dict.
    Raises clear error if not.
    """
    if obj is None:
        raise RuntimeError(f"{name} is None (scenario not resolved correctly)")
    if not isinstance(obj, dict):
        raise RuntimeError(f"{name} is not a dict: {type(obj)}")
    return obj

def validate_scenario_steps(scenario: Dict[str, Any]) -> None:
    """
    Validate that a scenario has valid steps structure.
    """
    scenario = _ensure_dict("scenario", scenario)
    
    steps = scenario.get("steps")
    if not isinstance(steps, list):
        raise RuntimeError(f"Scenario steps must be a list, got {type(steps)}")
    
    if len(steps) == 0:
        raise RuntimeError("Scenario must have at least one step")
    
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise RuntimeError(f"Step {i+1} must be a dict, got {type(step)}")
        
        if "action" not in step:
            raise RuntimeError(f"Step {i+1} is missing required 'action' field")
    
    logger.info(f"Validated scenario with {len(steps)} steps")
