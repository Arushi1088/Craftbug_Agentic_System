#!/usr/bin/env python3
"""
AI-Powered Dynamic UX Issue Generator
Generates realistic UX issues using AI analysis of step context and screen state
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not installed. Run: pip install openai")

# Load environment variables with validation
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
    load_dotenv("production.env")  # Also try production.env
    print("✅ Environment variables loaded from .env files")
except ImportError:
    print("⚠️ python-dotenv not available, using manual .env loading")
    
    def load_env_file(env_path: str = ".env"):
        """Load environment variables from .env file"""
        if not os.path.exists(env_path):
            return
        
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if not os.getenv(key):  # Don't override existing env vars
                            os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

    # Load .env file if it exists
    load_env_file()
    load_env_file("production.env")  # Also try production.env

# Validate OpenAI API Key with explicit logging
api_key = os.getenv("OPENAI_API_KEY")

if not api_key or api_key == "your-openai-api-key-here":
    print("❌ OPENAI_API_KEY not found or still using placeholder.")
    print("🔧 Please update your .env file with a valid OpenAI API key.")
    print("💡 Get your key from: https://platform.openai.com/api-keys")
    OPENAI_KEY_AVAILABLE = False
elif api_key.startswith("sk-"):
    print(f"✅ OpenAI Key Loaded: {api_key[:8]}... (truncated)")
    OPENAI_KEY_AVAILABLE = True
else:
    print("❌ Invalid OpenAI API key format. Should start with 'sk-'")
    OPENAI_KEY_AVAILABLE = False

logger = logging.getLogger(__name__)

class DynamicUXAnalyzer:
    """AI-powered dynamic UX issue generator based on step context"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        self.fallback_mode = True
        
        if OPENAI_AVAILABLE:
            # Get API key from parameter or environment
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key == "your-openai-api-key-here":
                print("❌ OPENAI_API_KEY not found or still using placeholder.")
                print("🔧 Please update your .env file with a valid OpenAI API key.")
                print("💡 Get your key from: https://platform.openai.com/api-keys")
                # Don't raise an error, but make it very clear
                logger.warning("⚠️ OpenAI API key not configured. Using fallback mode.")
                self.fallback_mode = True
            elif not api_key.startswith("sk-"):
                print("❌ Invalid OpenAI API key format. Should start with 'sk-'")
                logger.warning("⚠️ Invalid OpenAI API key format. Using fallback mode.")
                self.fallback_mode = True
            else:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.fallback_mode = False
                    print(f"✅ OpenAI client initialized: {api_key[:8]}... (truncated)")
                    logger.info("✅ OpenAI client initialized successfully")
                except Exception as e:
                    print(f"❌ OpenAI initialization failed: {e}")
                    logger.warning(f"⚠️ OpenAI initialization failed: {e}")
                    self.fallback_mode = True
        else:
            print("⚠️ OpenAI package not available. Using fallback mode.")
            logger.warning("⚠️ OpenAI package not available. Using fallback mode.")
        
        # Initialize enhanced static patterns for fallback
        self.ux_patterns = self._initialize_ux_patterns()
        
    def _initialize_ux_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize comprehensive UX issue patterns for fallback mode"""
        return {
            "navigation": [
                {
                    "title": "Navigation hierarchy unclear",
                    "severity": "medium",
                    "user_impact": "Users may struggle to understand site structure",
                    "recommended_fix": "Implement breadcrumbs and clear navigation labels",
                    "triggers": ["multiple nav elements", "deep nesting", "unclear labels"]
                },
                {
                    "title": "Inconsistent navigation patterns", 
                    "severity": "high",
                    "user_impact": "Users become confused by changing navigation styles",
                    "recommended_fix": "Standardize navigation component across all pages",
                    "triggers": ["style inconsistency", "different nav types"]
                }
            ],
            "interaction": [
                {
                    "title": "Button labels lack clarity",
                    "severity": "high", 
                    "user_impact": "Users uncertain about button actions",
                    "recommended_fix": "Use action-oriented, descriptive button text",
                    "triggers": ["generic labels", "short labels", "unclear actions"]
                },
                {
                    "title": "Missing interactive feedback",
                    "severity": "medium",
                    "user_impact": "Users unsure if actions registered",
                    "recommended_fix": "Add hover states, loading indicators, and confirmation messages",
                    "triggers": ["no hover effects", "no loading states", "no confirmations"]
                }
            ],
            "accessibility": [
                {
                    "title": "Form inputs missing labels",
                    "severity": "high",
                    "user_impact": "Screen reader users cannot identify input purposes",
                    "recommended_fix": "Add proper labels, aria-label, or aria-labelledby attributes",
                    "triggers": ["unlabeled inputs", "missing aria attributes"]
                },
                {
                    "title": "Poor keyboard navigation support",
                    "severity": "high",
                    "user_impact": "Keyboard-only users cannot navigate effectively",
                    "recommended_fix": "Ensure logical tab order and visible focus indicators",
                    "triggers": ["no focus indicators", "poor tab order", "keyboard traps"]
                }
            ],
            "cognitive_load": [
                {
                    "title": "Information overload on interface",
                    "severity": "medium",
                    "user_impact": "Users feel overwhelmed and may abandon tasks",
                    "recommended_fix": "Progressive disclosure and content prioritization",
                    "triggers": ["too many elements", "cluttered layout", "competing CTAs"]
                },
                {
                    "title": "Complex workflow with too many steps",
                    "severity": "high",
                    "user_impact": "Users abandon complex processes midway",
                    "recommended_fix": "Simplify workflow and provide clear progress indicators",
                    "triggers": ["multi-step complexity", "unclear progress", "too many forms"]
                }
            ],
            "performance": [
                {
                    "title": "Slow response times affect user experience",
                    "severity": "high",
                    "user_impact": "Users become frustrated and may leave",
                    "recommended_fix": "Optimize performance and add loading feedback",
                    "triggers": ["slow loading", "no progress indicators", "timeouts"]
                }
            ]
        }
    
    async def generate_dynamic_issues(
        self, 
        step_description: str, 
        screen_html: str, 
        task_goal: str,
        step_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Generate UX issues dynamically based on step context"""
        
        if not self.fallback_mode and self.client:
            try:
                return await self._generate_ai_issues(step_description, screen_html, task_goal, step_context)
            except Exception as e:
                logger.warning(f"AI generation failed, falling back to pattern-based: {e}")
                
        # Fallback to enhanced pattern-based generation
        return self._generate_pattern_based_issues(step_description, screen_html, task_goal, step_context)
    
    async def _generate_ai_issues(
        self,
        step_description: str,
        screen_html: str, 
        task_goal: str,
        step_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Generate issues using OpenAI API"""
        
        # Truncate HTML to avoid token limits
        truncated_html = screen_html[:3000] if screen_html else "No HTML available"
        
        step_info = step_context or {}
        duration = step_info.get('duration_ms', 0)
        action = step_info.get('action', 'unknown')
        status = step_info.get('status', 'unknown')
        
        prompt = f"""
        You are a senior UX expert analyzing a user interface step. Generate realistic UX issues based on the context.

        CONTEXT:
        - Step: {step_description}
        - Action: {action}
        - Goal: {task_goal}
        - Duration: {duration}ms
        - Status: {status}
        
        HTML SAMPLE: {truncated_html}

        Analyze this step and identify 1-3 realistic UX issues. You must respond with ONLY a valid JSON array in this exact format:

        [
          {{
            "title": "Specific issue title",
            "severity": "low",
            "user_impact": "Clear description of impact on users",
            "recommended_fix": "Actionable fix recommendation",
            "affected_component": "Specific UI component",
            "category": "interaction"
          }}
        ]

        Rules:
        - Severity must be: "low", "medium", or "high"
        - Category must be: "navigation", "interaction", "accessibility", "cognitive_load", "performance", or "visual_design"
        - Focus on real usability problems specific to this step
        - Return only the JSON array, no markdown, no explanations
        """

        try:
            response = self.client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o'),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.3')),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '800'))
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"AI response received: {content[:100]}...")
            
            # Try to extract JSON from the response
            if content.startswith('['):
                issues = json.loads(content)
            elif content.startswith('{'):
                # If wrapped in object, extract array
                parsed = json.loads(content)
                issues = parsed.get('issues', [parsed])  # Handle single issue object
            else:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    issues = json.loads(json_match.group())
                else:
                    logger.warning("No valid JSON found in AI response")
                    issues = []
                
            # Validate and enhance issues
            validated_issues = []
            for issue in issues[:3]:  # Limit to 3 issues
                if self._validate_issue_structure(issue):
                    # Add metadata
                    issue['generated_by'] = 'ai'
                    issue['step'] = step_context.get('action', 'unknown') if step_context else 'unknown'
                    issue['timestamp'] = datetime.now().isoformat()
                    validated_issues.append(issue)
            
            return validated_issues
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"AI API call failed: {e}")
            raise
    
    def _generate_pattern_based_issues(
        self,
        step_description: str,
        screen_html: str,
        task_goal: str, 
        step_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Generate issues using enhanced pattern matching"""
        
        issues = []
        step_info = step_context or {}
        action = step_info.get('action', 'unknown')
        duration = step_info.get('duration_ms', 0)
        
        # Analyze HTML content for patterns
        html_lower = screen_html.lower() if screen_html else ""
        
        # Performance-based issues
        if duration > 2000:
            issues.append({
                "title": "Slow response time impacting user experience",
                "severity": "high" if duration > 5000 else "medium",
                "user_impact": f"Users wait {duration}ms for response, may abandon task",
                "recommended_fix": "Optimize performance and add loading indicators",
                "affected_component": f"Step: {action}",
                "category": "performance",
                "generated_by": "pattern",
                "step": action,
                "timestamp": datetime.now().isoformat()
            })
        
        # Navigation issues
        nav_count = html_lower.count('<nav') + html_lower.count('class="nav')
        if nav_count > 2:
            pattern = self.ux_patterns["navigation"][0]
            issues.append({
                **pattern,
                "affected_component": f"{nav_count} navigation elements",
                "category": "navigation",
                "generated_by": "pattern",
                "step": action,
                "timestamp": datetime.now().isoformat()
            })
        
        # Button/interaction issues
        button_count = html_lower.count('<button')
        if button_count > 10:
            pattern = self.ux_patterns["cognitive_load"][0]
            issues.append({
                **pattern,
                "affected_component": f"{button_count} interactive buttons",
                "category": "cognitive_load", 
                "generated_by": "pattern",
                "step": action,
                "timestamp": datetime.now().isoformat()
            })
        
        # Accessibility issues
        if 'input' in html_lower and 'label' not in html_lower:
            pattern = self.ux_patterns["accessibility"][0]
            issues.append({
                **pattern,
                "affected_component": "Form inputs",
                "category": "accessibility",
                "generated_by": "pattern", 
                "step": action,
                "timestamp": datetime.now().isoformat()
            })
        
        # Context-specific issues based on step
        if action == "click" and "resolve" in step_description.lower():
            issues.append({
                "title": "Comment resolution feedback unclear",
                "severity": "medium",
                "user_impact": "Users uncertain if comment was actually resolved",
                "recommended_fix": "Add clear visual confirmation and state change animation",
                "affected_component": "Comment resolution UI",
                "category": "interaction",
                "generated_by": "pattern",
                "step": action,
                "timestamp": datetime.now().isoformat()
            })
        
        return issues[:3]  # Limit to 3 issues
    
    def _validate_issue_structure(self, issue: Dict) -> bool:
        """Validate that an issue has the required structure"""
        required_fields = ["title", "severity", "user_impact", "recommended_fix"]
        return all(field in issue and issue[field] for field in required_fields)
    
    def get_analysis_summary(self, all_issues: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for all detected issues"""
        if not all_issues:
            return {
                "total_issues": 0,
                "severity_breakdown": {},
                "category_breakdown": {},
                "generation_method": {}
            }
        
        severity_count = {}
        category_count = {}
        generation_count = {}
        
        for issue in all_issues:
            # Count by severity
            severity = issue.get('severity', 'unknown')
            severity_count[severity] = severity_count.get(severity, 0) + 1
            
            # Count by category
            category = issue.get('category', 'unknown')
            category_count[category] = category_count.get(category, 0) + 1
            
            # Count by generation method
            method = issue.get('generated_by', 'unknown')
            generation_count[method] = generation_count.get(method, 0) + 1
        
        return {
            "total_issues": len(all_issues),
            "severity_breakdown": severity_count,
            "category_breakdown": category_count,
            "generation_method": generation_count,
            "ai_enabled": not self.fallback_mode
        }
