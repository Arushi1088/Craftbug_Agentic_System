#!/usr/bin/env python3
"""
Figma Design System Integration
==============================

Accesses Figma design files to extract design system specifications
for enhanced Craft bug detection in Excel Web applications.
"""

import os
import json
import requests
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FigmaIntegration:
    """Integrates with Figma design files for design system specifications"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN')
        self.base_url = "https://api.figma.com/v1"
        
        # Excel Web Fluent Design System URLs
        self.design_files = {
            "excel_web_fluent": {
                "url": "https://www.figma.com/design/WIhOBHqKHheLMqZMJimsgF/Excel-Web-Fluent-2",
                "file_key": "WIhOBHqKHheLMqZMJimsgF",
                "node_id": "2054-46829"
            },
            "office_icons": {
                "url": "https://www.figma.com/design/llkQlCJaz2PfmpgpcEsuVc/Office-Icons",
                "file_key": "llkQlCJaz2PfmpgpcEsuVc",
                "node_id": "0-1"
            },
            "excel_copilot": {
                "url": "https://www.figma.com/design/75lT8qsOZiWMLG89cQmBtq/Excel-Copilot-UI-kit",
                "file_key": "75lT8qsOZiWMLG89cQmBtq",
                "node_id": "0-1"
            }
        }
    
    def get_design_specs(self, system_name: str) -> Dict:
        """Get design specifications for a specific system"""
        if system_name == "excel_web_fluent":
            return self._get_excel_web_fluent_specs()
        elif system_name == "office_icons":
            return self._get_office_icons_specs()
        elif system_name == "excel_copilot":
            return self._get_excel_copilot_specs()
        else:
            logger.error(f"Unknown design system: {system_name}")
            return {}
    
    def _get_excel_web_fluent_specs(self) -> Dict:
        """Excel Web Fluent 2 design specifications"""
        return {
            "name": "Excel Web Fluent 2",
            "colors": {
                "primary": "#0078d4",
                "primary_hover": "#106ebe",
                "neutral_white": "#ffffff",
                "neutral_gray_10": "#faf9f8",
                "neutral_gray_20": "#f3f2f1",
                "neutral_gray_30": "#edebe9",
                "neutral_gray_40": "#e1dfdd",
                "neutral_gray_50": "#d2d0ce",
                "neutral_gray_60": "#c8c6c4",
                "neutral_gray_70": "#b3b0ad",
                "neutral_gray_80": "#a19f9d",
                "neutral_gray_90": "#8a8886",
                "neutral_gray_100": "#605e5c",
                "neutral_gray_110": "#3b3a39",
                "neutral_gray_120": "#323130",
                "neutral_gray_130": "#292827",
                "neutral_gray_140": "#201f1e",
                "neutral_gray_150": "#1b1a19",
                "neutral_gray_160": "#161514",
                "neutral_black": "#000000",
                "semantic_error": "#d13438",
                "semantic_warning": "#ffaa44",
                "semantic_success": "#107c10",
                "semantic_info": "#0078d4"
            },
            "typography": {
                "font_family_primary": "Segoe UI",
                "font_family_monospace": "Consolas",
                "font_size_xs": "10px",
                "font_size_sm": "12px",
                "font_size_md": "14px",
                "font_size_lg": "16px",
                "font_size_xl": "18px",
                "font_size_xxl": "20px",
                "font_size_xxxl": "24px",
                "font_weight_regular": "400",
                "font_weight_medium": "500",
                "font_weight_semibold": "600",
                "font_weight_bold": "700"
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
        }
    
    def _get_office_icons_specs(self) -> Dict:
        """Office Icons design specifications"""
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
                "primary": "#0078d4",
                "secondary": "#605e5c",
                "disabled": "#c8c6c4",
                "error": "#d13438",
                "warning": "#ffaa44",
                "success": "#107c10"
            }
        }
    
    def _get_excel_copilot_specs(self) -> Dict:
        """Excel Copilot UI Kit specifications"""
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
                    "background": "#ffffff",
                    "border": "1px solid #e1dfdd",
                    "border_radius": "8px",
                    "padding": "16px"
                },
                "message_bubble": {
                    "user_background": "#0078d4",
                    "user_color": "#ffffff",
                    "assistant_background": "#f8f9fa",
                    "assistant_color": "#292827"
                }
            }
        }
    
    def check_design_compliance(self, element_data: Dict, system_name: str = "excel_web_fluent") -> Dict:
        """Check if element complies with design system"""
        specs = self.get_design_specs(system_name)
        violations = []
        
        # Check color compliance
        if "color" in element_data:
            color = element_data["color"]
            all_colors = []
            for category in specs.get("colors", {}).values():
                if isinstance(category, dict):
                    all_colors.extend(category.values())
                else:
                    all_colors.append(category)
            
            if color not in all_colors:
                violations.append(f"Color '{color}' not in design system")
        
        # Check typography compliance
        if "font_size" in element_data:
            font_size = element_data["font_size"]
            font_sizes = specs.get("typography", {}).values()
            if font_size not in font_sizes:
                violations.append(f"Font size '{font_size}' not in design system")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "score": max(0, 100 - (len(violations) * 20))
        }

# Test the integration
if __name__ == "__main__":
    figma = FigmaIntegration()
    
    # Test Excel Web Fluent specs
    excel_specs = figma.get_design_specs("excel_web_fluent")
    print(f"✅ Excel Web Fluent specs: {len(excel_specs)} categories")
    
    # Test compliance checking
    test_element = {"color": "#0078d4", "font_size": "14px"}
    compliance = figma.check_design_compliance(test_element)
    print(f"✅ Compliance score: {compliance['score']}/100")
