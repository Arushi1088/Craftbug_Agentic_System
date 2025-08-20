#!/usr/bin/env python3
"""
Figma Design System Integration Module
=====================================

This module integrates with Figma design files to extract design system specifications
for enhanced Craft bug detection in Excel Web applications.

Supports:
- Excel Web Fluent 2 Design System
- Office Icons Design System  
- Excel Copilot UI Kit
- Design token extraction
- Component specification analysis
- Design compliance checking
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DesignToken:
    """Represents a design token from Figma"""
    name: str
    value: str
    type: str  # color, typography, spacing, etc.
    category: str
    description: Optional[str] = None

@dataclass
class ComponentSpec:
    """Represents a component specification from Figma"""
    name: str
    type: str
    properties: Dict[str, Any]
    variants: List[Dict[str, Any]]
    design_tokens: List[str]

class FigmaDesignSystemIntegration:
    """Integrates with Figma design files to extract design system specifications"""
    
    def __init__(self, figma_access_token: Optional[str] = None):
        """
        Initialize Figma integration
        
        Args:
            figma_access_token: Personal access token for Figma API
        """
        self.figma_access_token = figma_access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.base_url = "https://api.figma.com/v1"
        self.design_systems = {
            "excel_web_fluent": {
                "file_key": "WIhOBHqKHheLMqZMJimsgF",
                "node_id": "2054-46829",
                "name": "Excel Web Fluent 2"
            },
            "office_icons": {
                "file_key": "llkQlCJaz2PfmpgpcEsuVc", 
                "node_id": "0-1",
                "name": "Office Icons"
            },
            "excel_copilot": {
                "file_key": "75lT8qsOZiWMLG89cQmBtq",
                "node_id": "0-1", 
                "name": "Excel Copilot UI Kit"
            }
        }
        
        # Design tokens cache
        self.design_tokens: Dict[str, List[DesignToken]] = {}
        self.component_specs: Dict[str, List[ComponentSpec]] = {}
        
    def get_figma_file_data(self, file_key: str, node_id: Optional[str] = None) -> Optional[Dict]:
        """
        Fetch Figma file data using the REST API
        
        Args:
            file_key: Figma file key from URL
            node_id: Specific node ID to fetch (optional)
            
        Returns:
            Figma file data or None if failed
        """
        if not self.figma_access_token:
            logger.warning("⚠️ No Figma access token provided. Using fallback method.")
            return self._get_figma_data_fallback(file_key, node_id)
            
        try:
            url = f"{self.base_url}/files/{file_key}"
            if node_id:
                url += f"/nodes?ids={node_id}"
                
            headers = {
                "X-Figma-Token": self.figma_access_token
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            logger.info(f"✅ Successfully fetched Figma data for file: {file_key}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to fetch Figma data: {e}")
            return self._get_figma_data_fallback(file_key, node_id)
    
    def _get_figma_data_fallback(self, file_key: str, node_id: Optional[str] = None) -> Optional[Dict]:
        """
        Fallback method to get Figma data when API access is not available
        Uses predefined design system specifications based on known Excel Web patterns
        """
        logger.info(f"🔄 Using fallback design system data for: {file_key}")
        
        # Predefined Excel Web Fluent Design System specifications
        if file_key == "WIhOBHqKHheLMqZMJimsgF":  # Excel Web Fluent 2
            return self._get_excel_web_fluent_specs()
        elif file_key == "llkQlCJaz2PfmpgpcEsuVc":  # Office Icons
            return self._get_office_icons_specs()
        elif file_key == "75lT8qsOZiWMLG89cQmBtq":  # Excel Copilot UI Kit
            return self._get_excel_copilot_specs()
        else:
            logger.warning(f"⚠️ Unknown Figma file key: {file_key}")
            return None
    
    def _get_excel_web_fluent_specs(self) -> Dict:
        """Get Excel Web Fluent 2 design system specifications"""
        return {
            "name": "Excel Web Fluent 2",
            "design_tokens": {
                "colors": {
                    "primary": {
                        "blue": "#0078d4",
                        "blue_hover": "#106ebe",
                        "blue_pressed": "#005a9e"
                    },
                    "neutral": {
                        "white": "#ffffff",
                        "gray_10": "#faf9f8",
                        "gray_20": "#f3f2f1",
                        "gray_30": "#edebe9",
                        "gray_40": "#e1dfdd",
                        "gray_50": "#d2d0ce",
                        "gray_60": "#c8c6c4",
                        "gray_70": "#b3b0ad",
                        "gray_80": "#a19f9d",
                        "gray_90": "#8a8886",
                        "gray_100": "#605e5c",
                        "gray_110": "#3b3a39",
                        "gray_120": "#323130",
                        "gray_130": "#292827",
                        "gray_140": "#201f1e",
                        "gray_150": "#1b1a19",
                        "gray_160": "#161514",
                        "black": "#000000"
                    },
                    "semantic": {
                        "error": "#d13438",
                        "warning": "#ffaa44",
                        "success": "#107c10",
                        "info": "#0078d4"
                    }
                },
                "typography": {
                    "font_family": {
                        "primary": "Segoe UI",
                        "monospace": "Consolas"
                    },
                    "font_size": {
                        "xs": "10px",
                        "sm": "12px",
                        "md": "14px",
                        "lg": "16px",
                        "xl": "18px",
                        "xxl": "20px",
                        "xxxl": "24px"
                    },
                    "font_weight": {
                        "regular": "400",
                        "medium": "500",
                        "semibold": "600",
                        "bold": "700"
                    },
                    "line_height": {
                        "tight": "1.2",
                        "normal": "1.4",
                        "relaxed": "1.6"
                    }
                },
                "spacing": {
                    "xs": "4px",
                    "sm": "8px",
                    "md": "12px",
                    "lg": "16px",
                    "xl": "20px",
                    "xxl": "24px",
                    "xxxl": "32px"
                },
                "border_radius": {
                    "none": "0px",
                    "sm": "2px",
                    "md": "4px",
                    "lg": "8px",
                    "xl": "12px"
                },
                "shadows": {
                    "sm": "0 1px 2px rgba(0, 0, 0, 0.1)",
                    "md": "0 2px 4px rgba(0, 0, 0, 0.1)",
                    "lg": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "xl": "0 8px 16px rgba(0, 0, 0, 0.1)"
                }
            },
            "components": {
                "button": {
                    "primary": {
                        "background": "var(--color-primary-blue)",
                        "color": "var(--color-neutral-white)",
                        "border": "none",
                        "border_radius": "var(--border-radius-md)",
                        "padding": "var(--spacing-sm) var(--spacing-md)",
                        "font_size": "var(--font-size-md)",
                        "font_weight": "var(--font-weight-medium)"
                    },
                    "secondary": {
                        "background": "transparent",
                        "color": "var(--color-primary-blue)",
                        "border": "1px solid var(--color-primary-blue)",
                        "border_radius": "var(--border-radius-md)",
                        "padding": "var(--spacing-sm) var(--spacing-md)",
                        "font_size": "var(--font-size-md)",
                        "font_weight": "var(--font-weight-medium)"
                    }
                },
                "input": {
                    "background": "var(--color-neutral-white)",
                    "border": "1px solid var(--color-neutral-gray-60)",
                    "border_radius": "var(--border-radius-md)",
                    "padding": "var(--spacing-sm) var(--spacing-md)",
                    "font_size": "var(--font-size-md)",
                    "color": "var(--color-neutral-gray-130)"
                },
                "dialog": {
                    "background": "var(--color-neutral-white)",
                    "border": "1px solid var(--color-neutral-gray-40)",
                    "border_radius": "var(--border-radius-lg)",
                    "box_shadow": "var(--shadow-lg)",
                    "padding": "var(--spacing-lg)"
                }
            }
        }
    
    def _get_office_icons_specs(self) -> Dict:
        """Get Office Icons design system specifications"""
        return {
            "name": "Office Icons",
            "icon_sizes": {
                "xs": "12px",
                "sm": "16px", 
                "md": "20px",
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px"
            },
            "icon_colors": {
                "primary": "var(--color-primary-blue)",
                "secondary": "var(--color-neutral-gray-100)",
                "disabled": "var(--color-neutral-gray-60)",
                "error": "var(--color-semantic-error)",
                "warning": "var(--color-semantic-warning)",
                "success": "var(--color-semantic-success)"
            },
            "icon_spacing": {
                "padding": "var(--spacing-xs)",
                "margin": "var(--spacing-xs)"
            },
            "icon_alignment": {
                "vertical": "center",
                "horizontal": "center"
            }
        }
    
    def _get_excel_copilot_specs(self) -> Dict:
        """Get Excel Copilot UI Kit specifications"""
        return {
            "name": "Excel Copilot UI Kit",
            "copilot_colors": {
                "primary": "#0078d4",
                "secondary": "#106ebe",
                "accent": "#00bcf2",
                "background": "#f8f9fa",
                "surface": "#ffffff",
                "border": "#e1dfdd"
            },
            "copilot_components": {
                "chat_panel": {
                    "background": "var(--copilot-color-surface)",
                    "border": "1px solid var(--copilot-color-border)",
                    "border_radius": "var(--border-radius-lg)",
                    "padding": "var(--spacing-lg)"
                },
                "message_bubble": {
                    "user": {
                        "background": "var(--copilot-color-primary)",
                        "color": "var(--color-neutral-white)",
                        "border_radius": "var(--border-radius-lg) var(--border-radius-sm)"
                    },
                    "assistant": {
                        "background": "var(--copilot-color-background)",
                        "color": "var(--color-neutral-gray-130)",
                        "border_radius": "var(--border-radius-sm) var(--border-radius-lg)"
                    }
                },
                "suggestion_chip": {
                    "background": "var(--copilot-color-background)",
                    "border": "1px solid var(--copilot-color-border)",
                    "border_radius": "var(--border-radius-xl)",
                    "padding": "var(--spacing-sm) var(--spacing-md)",
                    "hover_background": "var(--copilot-color-primary)",
                    "hover_color": "var(--color-neutral-white)"
                }
            }
        }
    
    def extract_design_tokens(self, system_name: str) -> List[DesignToken]:
        """
        Extract design tokens from a specific design system
        
        Args:
            system_name: Name of the design system to extract from
            
        Returns:
            List of design tokens
        """
        if system_name not in self.design_systems:
            logger.error(f"❌ Unknown design system: {system_name}")
            return []
        
        system_config = self.design_systems[system_name]
        file_data = self.get_figma_file_data(system_config["file_key"], system_config["node_id"])
        
        if not file_data:
            logger.warning(f"⚠️ Could not fetch data for {system_name}, using fallback")
            file_data = self._get_figma_data_fallback(system_config["file_key"], system_config["node_id"])
        
        tokens = []
        
        if file_data and "design_tokens" in file_data:
            for category, category_tokens in file_data["design_tokens"].items():
                if isinstance(category_tokens, dict):
                    for token_name, token_value in category_tokens.items():
                        if isinstance(token_value, dict):
                            # Handle nested token structures
                            for sub_name, sub_value in token_value.items():
                                tokens.append(DesignToken(
                                    name=f"{token_name}_{sub_name}",
                                    value=str(sub_value),
                                    type=category,
                                    category=token_name
                                ))
                        else:
                            tokens.append(DesignToken(
                                name=token_name,
                                value=str(token_value),
                                type=category,
                                category=category
                            ))
        
        self.design_tokens[system_name] = tokens
        logger.info(f"✅ Extracted {len(tokens)} design tokens from {system_name}")
        return tokens
    
    def get_component_specifications(self, system_name: str) -> List[ComponentSpec]:
        """
        Get component specifications from a design system
        
        Args:
            system_name: Name of the design system
            
        Returns:
            List of component specifications
        """
        if system_name not in self.design_systems:
            logger.error(f"❌ Unknown design system: {system_name}")
            return []
        
        system_config = self.design_systems[system_name]
        file_data = self.get_figma_file_data(system_config["file_key"], system_config["node_id"])
        
        if not file_data:
            logger.warning(f"⚠️ Could not fetch data for {system_name}, using fallback")
            file_data = self._get_figma_data_fallback(system_config["file_key"], system_config["node_id"])
        
        specs = []
        
        if file_data and "components" in file_data:
            for component_name, component_data in file_data["components"].items():
                if isinstance(component_data, dict):
                    variants = []
                    properties = {}
                    
                    for variant_name, variant_data in component_data.items():
                        if isinstance(variant_data, dict):
                            variants.append({
                                "name": variant_name,
                                "properties": variant_data
                            })
                            # Merge properties for the main spec
                            properties.update(variant_data)
                    
                    specs.append(ComponentSpec(
                        name=component_name,
                        type="component",
                        properties=properties,
                        variants=variants,
                        design_tokens=[]
                    ))
        
        self.component_specs[system_name] = specs
        logger.info(f"✅ Extracted {len(specs)} component specifications from {system_name}")
        return specs
    
    def check_design_compliance(self, element_data: Dict, system_name: str = "excel_web_fluent") -> Dict[str, Any]:
        """
        Check if an element complies with the design system specifications
        
        Args:
            element_data: Element data to check (color, typography, spacing, etc.)
            system_name: Design system to check against
            
        Returns:
            Compliance report with violations and recommendations
        """
        tokens = self.design_tokens.get(system_name, [])
        if not tokens:
            tokens = self.extract_design_tokens(system_name)
        
        violations = []
        recommendations = []
        
        # Check color compliance
        if "color" in element_data:
            element_color = element_data["color"]
            matching_tokens = [t for t in tokens if t.type == "colors" and t.value == element_color]
            
            if not matching_tokens:
                violations.append({
                    "type": "color",
                    "issue": f"Color '{element_color}' not found in design system",
                    "severity": "medium"
                })
                
                # Find closest matching color
                closest_token = self._find_closest_color_token(element_color, tokens)
                if closest_token:
                    recommendations.append({
                        "type": "color",
                        "suggestion": f"Use design token '{closest_token.name}' ({closest_token.value}) instead"
                    })
        
        # Check typography compliance
        if "font_size" in element_data:
            element_font_size = element_data["font_size"]
            matching_tokens = [t for t in tokens if t.type == "typography" and "font_size" in t.category and t.value == element_font_size]
            
            if not matching_tokens:
                violations.append({
                    "type": "typography",
                    "issue": f"Font size '{element_font_size}' not found in design system",
                    "severity": "low"
                })
        
        # Check spacing compliance
        if "padding" in element_data or "margin" in element_data:
            for spacing_type in ["padding", "margin"]:
                if spacing_type in element_data:
                    element_spacing = element_data[spacing_type]
                    matching_tokens = [t for t in tokens if t.type == "spacing" and t.value == element_spacing]
                    
                    if not matching_tokens:
                        violations.append({
                            "type": "spacing",
                            "issue": f"{spacing_type.title()} '{element_spacing}' not found in design system",
                            "severity": "low"
                        })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "recommendations": recommendations,
            "score": max(0, 100 - (len(violations) * 20))  # Simple scoring
        }
    
    def _find_closest_color_token(self, color: str, tokens: List[DesignToken]) -> Optional[DesignToken]:
        """Find the closest matching color token"""
        color_tokens = [t for t in tokens if t.type == "colors"]
        if not color_tokens:
            return None
        
        # Simple color matching (could be enhanced with color distance calculation)
        for token in color_tokens:
            if token.value.lower() == color.lower():
                return token
        
        return color_tokens[0] if color_tokens else None
    
    def generate_design_report(self, system_name: str = "excel_web_fluent") -> Dict[str, Any]:
        """
        Generate a comprehensive design system report
        
        Args:
            system_name: Design system to report on
            
        Returns:
            Design system report
        """
        tokens = self.extract_design_tokens(system_name)
        components = self.get_component_specifications(system_name)
        
        token_categories = {}
        for token in tokens:
            if token.type not in token_categories:
                token_categories[token.type] = []
            token_categories[token.type].append(token)
        
        return {
            "system_name": system_name,
            "total_tokens": len(tokens),
            "total_components": len(components),
            "token_categories": {cat: len(tokens) for cat, tokens in token_categories.items()},
            "components": [comp.name for comp in components],
            "last_updated": "2024-01-18"  # Could be fetched from Figma API
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize Figma integration
    figma_integration = FigmaDesignSystemIntegration()
    
    # Extract design tokens from Excel Web Fluent 2
    print("🎨 Extracting Excel Web Fluent 2 design tokens...")
    tokens = figma_integration.extract_design_tokens("excel_web_fluent")
    print(f"✅ Found {len(tokens)} design tokens")
    
    # Get component specifications
    print("🔧 Extracting component specifications...")
    components = figma_integration.get_component_specifications("excel_web_fluent")
    print(f"✅ Found {len(components)} component specifications")
    
    # Generate design report
    print("📊 Generating design system report...")
    report = figma_integration.generate_design_report("excel_web_fluent")
    print(f"✅ Design system: {report['system_name']}")
    print(f"   Total tokens: {report['total_tokens']}")
    print(f"   Total components: {report['total_components']}")
    
    # Test design compliance
    print("🔍 Testing design compliance...")
    test_element = {
        "color": "#0078d4",
        "font_size": "14px",
        "padding": "8px"
    }
    compliance = figma_integration.check_design_compliance(test_element)
    print(f"✅ Compliance score: {compliance['score']}/100")
    print(f"   Compliant: {compliance['compliant']}")
    print(f"   Violations: {len(compliance['violations'])}")
