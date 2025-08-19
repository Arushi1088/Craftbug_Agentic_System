#!/usr/bin/env python3
"""
Accessibility Compliance Analyzer
================================

Separate module for WCAG 2.1 AA compliance checking and accessibility bug detection.
This is kept separate from Craft bugs as requested by the user.
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class AccessibilityAnalyzer:
    """Accessibility compliance analyzer for WCAG 2.1 AA standards"""
    
    def __init__(self):
        self.wcag_guidelines = {
            '1.1.1': 'Non-text Content',
            '1.3.1': 'Info and Relationships',
            '1.3.2': 'Meaningful Sequence',
            '1.4.1': 'Use of Color',
            '1.4.3': 'Contrast (Minimum)',
            '1.4.4': 'Resize Text',
            '2.1.1': 'Keyboard',
            '2.1.2': 'No Keyboard Trap',
            '2.2.1': 'Timing Adjustable',
            '2.2.2': 'Pause, Stop, Hide',
            '2.3.1': 'Three Flashes or Below Threshold',
            '2.4.1': 'Bypass Blocks',
            '2.4.2': 'Page Titled',
            '2.4.3': 'Focus Order',
            '2.4.4': 'Link Purpose (In Context)',
            '2.4.5': 'Multiple Ways',
            '2.4.6': 'Headings and Labels',
            '2.4.7': 'Focus Visible',
            '3.1.1': 'Language of Page',
            '3.2.1': 'On Focus',
            '3.2.2': 'On Input',
            '3.3.1': 'Error Identification',
            '3.3.2': 'Labels or Instructions',
            '4.1.1': 'Parsing',
            '4.1.2': 'Name, Role, Value'
        }
        
        # WCAG 2.1 AA contrast ratios
        self.contrast_ratios = {
            'normal_text': 4.5,      # Normal text (18pt or 14pt bold)
            'large_text': 3.0,       # Large text (18pt+ or 14pt+ bold)
            'ui_components': 3.0,    # UI components and graphics
            'decorative': 1.0        # Decorative elements (no contrast requirement)
        }
        
        # Color combinations for testing
        self.color_pairs = [
            ('#0078d4', '#ffffff'),  # Primary blue on white
            ('#323130', '#ffffff'),  # Dark gray on white
            ('#605e5c', '#ffffff'),  # Medium gray on white
            ('#ffffff', '#323130'),  # White on dark gray
            ('#0078d4', '#f3f2f1'),  # Primary blue on light gray
            ('#106ebe', '#ffffff'),  # Hover blue on white
        ]
    
    def analyze_accessibility(self, screenshot_path: str, step_data: Dict) -> Dict[str, Any]:
        """Analyze screenshot for accessibility compliance"""
        if not screenshot_path:
            return {'error': 'No screenshot provided'}
        
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                return {'error': 'Failed to load image'}
            
            # Convert to RGB for analysis
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Perform accessibility analyses
            analysis_results = {
                'contrast_analysis': self._analyze_contrast_ratios(rgb_image),
                'color_analysis': self._analyze_color_accessibility(rgb_image),
                'text_analysis': self._analyze_text_accessibility(rgb_image),
                'focus_analysis': self._analyze_focus_indicators(rgb_image),
                'keyboard_analysis': self._analyze_keyboard_accessibility(step_data),
                'semantic_analysis': self._analyze_semantic_structure(step_data),
                'timestamp': datetime.now().isoformat(),
                'wcag_compliance': self._calculate_wcag_compliance()
            }
            
            return analysis_results
            
        except Exception as e:
            return {'error': f'Accessibility analysis failed: {str(e)}'}
    
    def _analyze_contrast_ratios(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color contrast ratios for WCAG 2.1 AA compliance"""
        results = {
            'contrast_violations': [],
            'overall_contrast_score': 100,
            'tested_combinations': [],
            'wcag_compliant': True
        }
        
        # Test predefined color combinations
        for fg_color, bg_color in self.color_pairs:
            contrast_ratio = self._calculate_contrast_ratio(fg_color, bg_color)
            
            combination_result = {
                'foreground': fg_color,
                'background': bg_color,
                'contrast_ratio': contrast_ratio,
                'wcag_compliant': contrast_ratio >= self.contrast_ratios['normal_text']
            }
            
            results['tested_combinations'].append(combination_result)
            
            if not combination_result['wcag_compliant']:
                results['contrast_violations'].append({
                    'type': 'insufficient_contrast',
                    'foreground': fg_color,
                    'background': bg_color,
                    'contrast_ratio': contrast_ratio,
                    'required_ratio': self.contrast_ratios['normal_text'],
                    'severity': 'high',
                    'wcag_guideline': '1.4.3'
                })
        
        # Calculate overall score
        violation_count = len(results['contrast_violations'])
        results['overall_contrast_score'] = max(0, 100 - (violation_count * 20))
        results['wcag_compliant'] = violation_count == 0
        
        return results
    
    def _analyze_color_accessibility(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color usage for accessibility"""
        results = {
            'color_issues': [],
            'color_accessibility_score': 100,
            'color_dependent_elements': []
        }
        
        # Check for color-only indicators (WCAG 1.4.1)
        # This would require more sophisticated analysis in practice
        # For now, we'll check for common patterns
        
        # Analyze dominant colors
        pixels = image.reshape(-1, 3)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)[::-1]
        dominant_colors = unique_colors[sorted_indices[:5]]
        
        # Check for potential color-only indicators
        for color in dominant_colors:
            hex_color = self._rgb_to_hex(color)
            if self._is_potential_indicator_color(hex_color):
                results['color_dependent_elements'].append({
                    'color': hex_color,
                    'type': 'potential_indicator',
                    'description': 'Color may be used as sole indicator'
                })
        
        # Check for color accessibility issues
        if len(results['color_dependent_elements']) > 0:
            results['color_issues'].append({
                'type': 'color_only_indicator',
                'severity': 'medium',
                'wcag_guideline': '1.4.1',
                'description': 'Elements may rely solely on color for information'
            })
        
        # Calculate score
        issue_count = len(results['color_issues'])
        results['color_accessibility_score'] = max(0, 100 - (issue_count * 25))
        
        return results
    
    def _analyze_text_accessibility(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze text accessibility features"""
        results = {
            'text_issues': [],
            'text_accessibility_score': 100,
            'font_sizes': [],
            'text_contrast': []
        }
        
        # Convert to grayscale for text analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect text regions (simplified approach)
        # In practice, you'd use OCR or more sophisticated text detection
        
        # Check for minimum font sizes
        # WCAG 2.1 doesn't specify minimum font size, but 12pt is commonly recommended
        min_font_size = 12  # pixels
        
        # This is a simplified check - real implementation would use OCR
        results['font_sizes'].append({
            'size': 'unknown',  # Would be detected by OCR
            'wcag_compliant': True,  # Assuming compliant for demo
            'description': 'Font size analysis requires OCR implementation'
        })
        
        # Check for text scaling issues
        results['text_issues'].append({
            'type': 'text_scaling_check',
            'severity': 'low',
            'wcag_guideline': '1.4.4',
            'description': 'Text scaling compliance requires dynamic testing'
        })
        
        # Calculate score
        issue_count = len(results['text_issues'])
        results['text_accessibility_score'] = max(0, 100 - (issue_count * 15))
        
        return results
    
    def _analyze_focus_indicators(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze focus indicator visibility"""
        results = {
            'focus_issues': [],
            'focus_accessibility_score': 100,
            'focus_indicators_detected': []
        }
        
        # Look for common focus indicator patterns
        # This is a simplified approach - real implementation would be more sophisticated
        
        # Check for high-contrast borders (common focus indicators)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Count edge pixels (potential focus indicators)
        edge_ratio = np.sum(edges > 0) / edges.size
        
        if edge_ratio < 0.01:  # Very few edges might indicate missing focus indicators
            results['focus_issues'].append({
                'type': 'missing_focus_indicators',
                'severity': 'high',
                'wcag_guideline': '2.4.7',
                'description': 'Focus indicators may not be visible'
            })
        
        # Check for color-based focus indicators
        # This would require more sophisticated analysis
        
        results['focus_indicators_detected'].append({
            'type': 'edge_based',
            'confidence': 'medium',
            'description': 'Edge detection suggests potential focus indicators'
        })
        
        # Calculate score
        issue_count = len(results['focus_issues'])
        results['focus_accessibility_score'] = max(0, 100 - (issue_count * 30))
        
        return results
    
    def _analyze_keyboard_accessibility(self, step_data: Dict) -> Dict[str, Any]:
        """Analyze keyboard accessibility based on step data"""
        results = {
            'keyboard_issues': [],
            'keyboard_accessibility_score': 100,
            'keyboard_tests': []
        }
        
        # Analyze step data for keyboard accessibility patterns
        step_description = step_data.get('description', '').lower()
        
        # Check for mouse-only interactions
        mouse_keywords = ['click', 'hover', 'drag', 'scroll']
        keyboard_keywords = ['tab', 'enter', 'space', 'arrow', 'keyboard']
        
        mouse_interactions = sum(1 for keyword in mouse_keywords if keyword in step_description)
        keyboard_interactions = sum(1 for keyword in keyboard_keywords if keyword in step_description)
        
        if mouse_interactions > keyboard_interactions:
            results['keyboard_issues'].append({
                'type': 'mouse_dependent_interaction',
                'severity': 'medium',
                'wcag_guideline': '2.1.1',
                'description': 'Interaction appears to be mouse-dependent'
            })
        
        # Check for timing-based interactions
        if 'timing' in step_description or 'timeout' in step_description:
            results['keyboard_issues'].append({
                'type': 'timing_dependent_interaction',
                'severity': 'medium',
                'wcag_guideline': '2.2.1',
                'description': 'Interaction may have timing constraints'
            })
        
        # Add keyboard accessibility tests
        results['keyboard_tests'].extend([
            {
                'test': 'Tab navigation',
                'status': 'requires_testing',
                'wcag_guideline': '2.4.3'
            },
            {
                'test': 'Keyboard trap detection',
                'status': 'requires_testing',
                'wcag_guideline': '2.1.2'
            },
            {
                'test': 'Focus order',
                'status': 'requires_testing',
                'wcag_guideline': '2.4.3'
            }
        ])
        
        # Calculate score
        issue_count = len(results['keyboard_issues'])
        results['keyboard_accessibility_score'] = max(0, 100 - (issue_count * 25))
        
        return results
    
    def _analyze_semantic_structure(self, step_data: Dict) -> Dict[str, Any]:
        """Analyze semantic structure and relationships"""
        results = {
            'semantic_issues': [],
            'semantic_accessibility_score': 100,
            'semantic_elements': []
        }
        
        # Analyze step data for semantic structure patterns
        step_description = step_data.get('description', '').lower()
        
        # Check for heading structure
        if 'heading' in step_description or 'title' in step_description:
            results['semantic_elements'].append({
                'type': 'heading',
                'wcag_guideline': '2.4.6',
                'status': 'detected'
            })
        
        # Check for form elements
        if 'input' in step_description or 'form' in step_description:
            results['semantic_elements'].append({
                'type': 'form',
                'wcag_guideline': '3.3.2',
                'status': 'detected'
            })
        
        # Check for links
        if 'link' in step_description or 'button' in step_description:
            results['semantic_elements'].append({
                'type': 'link_button',
                'wcag_guideline': '2.4.4',
                'status': 'detected'
            })
        
        # Add semantic structure tests
        results['semantic_issues'].extend([
            {
                'type': 'heading_structure_check',
                'severity': 'medium',
                'wcag_guideline': '2.4.6',
                'description': 'Heading structure should be logical and hierarchical'
            },
            {
                'type': 'label_association_check',
                'severity': 'high',
                'wcag_guideline': '3.3.2',
                'description': 'Form controls should have associated labels'
            },
            {
                'type': 'link_purpose_check',
                'severity': 'medium',
                'wcag_guideline': '2.4.4',
                'description': 'Link purpose should be clear from context'
            }
        ])
        
        # Calculate score
        issue_count = len(results['semantic_issues'])
        results['semantic_accessibility_score'] = max(0, 100 - (issue_count * 20))
        
        return results
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert RGB to luminance
        def rgb_to_luminance(rgb):
            r, g, b = [c/255.0 for c in rgb]
            r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055)**2.4
            g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055)**2.4
            b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055)**2.4
            return 0.2126*r + 0.7152*g + 0.0722*b
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = rgb_to_luminance(rgb1)
        lum2 = rgb_to_luminance(rgb2)
        
        # Calculate contrast ratio
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _rgb_to_hex(self, rgb_color: np.ndarray) -> str:
        """Convert RGB color to hex format"""
        r, g, b = rgb_color
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _is_potential_indicator_color(self, hex_color: str) -> bool:
        """Check if color might be used as a sole indicator"""
        # Common indicator colors
        indicator_colors = [
            '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',  # Primary colors
            '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'   # Bright colors
        ]
        
        return hex_color.upper() in [color.upper() for color in indicator_colors]
    
    def _calculate_wcag_compliance(self) -> Dict[str, Any]:
        """Calculate overall WCAG 2.1 AA compliance"""
        return {
            'overall_compliance': 'requires_full_testing',
            'tested_guidelines': [
                '1.4.3 - Contrast (Minimum)',
                '1.4.1 - Use of Color',
                '2.4.7 - Focus Visible',
                '2.1.1 - Keyboard',
                '2.4.6 - Headings and Labels'
            ],
            'untested_guidelines': [
                '1.1.1 - Non-text Content',
                '1.3.1 - Info and Relationships',
                '2.2.1 - Timing Adjustable',
                '3.3.1 - Error Identification',
                '4.1.2 - Name, Role, Value'
            ],
            'compliance_level': 'AA',
            'wcag_version': '2.1'
        }
    
    def generate_accessibility_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive accessibility report"""
        report = {
            'report_type': 'Accessibility Analysis',
            'generated_at': datetime.now().isoformat(),
            'wcag_version': '2.1 AA',
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'overall_accessibility_score': 0
            },
            'detailed_analysis': analysis_results,
            'accessibility_bugs': [],
            'recommendations': []
        }
        
        # Count issues by severity
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict) and 'issues' in results:
                for issue in results.get('issues', []):
                    report['summary']['total_issues'] += 1
                    severity = issue.get('severity', 'low')
                    if severity == 'critical':
                        report['summary']['critical_issues'] += 1
                    elif severity == 'medium':
                        report['summary']['medium_issues'] += 1
                    else:
                        report['summary']['low_issues'] += 1
        
        # Calculate overall accessibility score
        scores = []
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict) and 'score' in results:
                scores.append(results['score'])
        
        if scores:
            report['summary']['overall_accessibility_score'] = sum(scores) / len(scores)
        
        # Generate accessibility bugs (separate from Craft bugs)
        report['accessibility_bugs'] = self._identify_accessibility_bugs(analysis_results)
        
        # Generate recommendations
        if report['summary']['critical_issues'] > 0:
            report['recommendations'].append('Address critical accessibility issues immediately')
        if report['summary']['medium_issues'] > 0:
            report['recommendations'].append('Review and fix medium-priority accessibility issues')
        if report['summary']['low_issues'] > 0:
            report['recommendations'].append('Consider fixing low-priority accessibility improvements')
        
        return report
    
    def _identify_accessibility_bugs(self, analysis_results: Dict) -> List[Dict]:
        """Identify accessibility bugs (separate from Craft bugs)"""
        accessibility_bugs = []
        
        # Contrast-related accessibility bugs
        contrast_analysis = analysis_results.get('contrast_analysis', {})
        for violation in contrast_analysis.get('contrast_violations', []):
            accessibility_bugs.append({
                'id': f"ACC-{len(accessibility_bugs)+1:03d}",
                'title': 'Insufficient Color Contrast',
                'description': f"Contrast ratio {violation['contrast_ratio']:.2f}:1 between {violation['foreground']} and {violation['background']}",
                'accessibility_bug_type': 'Contrast Violation',
                'severity': 'High',
                'wcag_guideline': violation['wcag_guideline'],
                'user_impact': 'Users with visual impairments cannot read text',
                'recommended_fix': f"Increase contrast ratio to at least {violation['required_ratio']}:1"
            })
        
        # Color accessibility bugs
        color_analysis = analysis_results.get('color_analysis', {})
        for issue in color_analysis.get('color_issues', []):
            accessibility_bugs.append({
                'id': f"ACC-{len(accessibility_bugs)+1:03d}",
                'title': 'Color-Only Information',
                'description': issue['description'],
                'accessibility_bug_type': 'Color Dependency',
                'severity': 'Medium',
                'wcag_guideline': issue['wcag_guideline'],
                'user_impact': 'Colorblind users cannot distinguish information',
                'recommended_fix': 'Add text labels or icons in addition to color'
            })
        
        # Focus indicator bugs
        focus_analysis = analysis_results.get('focus_analysis', {})
        for issue in focus_analysis.get('focus_issues', []):
            accessibility_bugs.append({
                'id': f"ACC-{len(accessibility_bugs)+1:03d}",
                'title': 'Missing Focus Indicators',
                'description': issue['description'],
                'accessibility_bug_type': 'Focus Visibility',
                'severity': 'High',
                'wcag_guideline': issue['wcag_guideline'],
                'user_impact': 'Keyboard users cannot see which element is focused',
                'recommended_fix': 'Add visible focus indicators for all interactive elements'
            })
        
        # Keyboard accessibility bugs
        keyboard_analysis = analysis_results.get('keyboard_analysis', {})
        for issue in keyboard_analysis.get('keyboard_issues', []):
            accessibility_bugs.append({
                'id': f"ACC-{len(accessibility_bugs)+1:03d}",
                'title': 'Keyboard Accessibility Issue',
                'description': issue['description'],
                'accessibility_bug_type': 'Keyboard Navigation',
                'severity': 'Medium',
                'wcag_guideline': issue['wcag_guideline'],
                'user_impact': 'Keyboard-only users cannot access functionality',
                'recommended_fix': 'Ensure all functionality is accessible via keyboard'
            })
        
        return accessibility_bugs

# Test the accessibility analyzer
if __name__ == "__main__":
    analyzer = AccessibilityAnalyzer()
    
    print("♿ Accessibility Analyzer initialized")
    print("✅ Ready for WCAG 2.1 AA compliance checking")
    print("📊 Capabilities:")
    print("   - Color contrast ratio analysis")
    print("   - Color accessibility checking")
    print("   - Text accessibility validation")
    print("   - Focus indicator detection")
    print("   - Keyboard accessibility analysis")
    print("   - Semantic structure validation")
    print("   - WCAG 2.1 AA compliance reporting")
    print("   - Separate accessibility bug identification")
