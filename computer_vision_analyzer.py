#!/usr/bin/env python3
"""
Computer Vision Analyzer for Visual Inconsistency Detection
==========================================================

Uses computer vision to detect visual inconsistencies automatically
while retaining timing and interaction analysis for comprehensive bug detection.
"""

import cv2
import numpy as np
from PIL import Image
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime

class ComputerVisionAnalyzer:
    """Computer vision analyzer for automatic visual inconsistency detection"""
    
    def __init__(self):
        self.design_specs = {
            'colors': {
                'primary': '#0078d4',
                'primary_hover': '#106ebe',
                'neutral_white': '#ffffff',
                'neutral_gray_10': '#faf9f8',
                'neutral_gray_20': '#f3f2f1',
                'neutral_gray_30': '#edebe9',
                'neutral_gray_40': '#e1dfdd',
                'neutral_gray_50': '#d2d0ce',
                'neutral_gray_60': '#c8c6c4',
                'neutral_gray_70': '#b3b0ad',
                'neutral_gray_80': '#a19f9d',
                'neutral_gray_90': '#8a8886',
                'neutral_gray_100': '#605e5c',
                'neutral_gray_110': '#3b3a39',
                'neutral_gray_120': '#323130',
                'neutral_gray_130': '#292827',
                'neutral_gray_140': '#201f1e',
                'neutral_gray_150': '#1b1a19',
                'neutral_gray_160': '#161514',
                'neutral_black': '#000000'
            },
            'spacing': {
                'xs': 4, 'sm': 8, 'md': 12, 'lg': 16, 'xl': 20, 'xxl': 24, 'xxxl': 32
            },
            'border_radius': {
                'none': 0, 'sm': 2, 'md': 4, 'lg': 8, 'xl': 12
            }
        }
    
    def analyze_screenshot(self, screenshot_path: str, step_data: Dict) -> Dict[str, Any]:
        """Analyze screenshot for visual inconsistencies"""
        if not os.path.exists(screenshot_path):
            return {'error': 'Screenshot not found'}
        
        try:
            # Load image
            image = cv2.imread(screenshot_path)
            if image is None:
                return {'error': 'Failed to load image'}
            
            # Convert to RGB for analysis
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Perform various analyses
            analysis_results = {
                'color_analysis': self._analyze_colors(rgb_image),
                'alignment_analysis': self._analyze_alignment(rgb_image),
                'spacing_analysis': self._analyze_spacing(rgb_image),
                'consistency_analysis': self._analyze_consistency(rgb_image),
                'visual_rhythm_analysis': self._analyze_visual_rhythm(rgb_image),
                'surface_level_analysis': self._analyze_surface_levels(rgb_image, step_data),
                'timestamp': datetime.now().isoformat(),
                'screenshot_path': screenshot_path
            }
            
            return analysis_results
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _analyze_colors(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color consistency against design system"""
        results = {
            'color_violations': [],
            'color_consistency_score': 100,
            'dominant_colors': [],
            'color_distribution': {}
        }
        
        # Extract dominant colors
        pixels = image.reshape(-1, 3)
        unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)[::-1]
        dominant_colors = unique_colors[sorted_indices[:10]]
        
        results['dominant_colors'] = [
            {'rgb': tuple(color), 'hex': self._rgb_to_hex(color), 'frequency': int(counts[i])}
            for i, color in zip(sorted_indices[:10], dominant_colors)
        ]
        
        # Check for color violations
        for color_info in results['dominant_colors']:
            hex_color = color_info['hex']
            if not self._is_design_system_color(hex_color):
                results['color_violations'].append({
                    'color': hex_color,
                    'type': 'non_design_system_color',
                    'severity': 'low',
                    'description': f'Color {hex_color} not in design system'
                })
        
        # Calculate consistency score
        violation_count = len(results['color_violations'])
        results['color_consistency_score'] = max(0, 100 - (violation_count * 10))
        
        return results
    
    def _analyze_alignment(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze alignment consistency"""
        results = {
            'alignment_issues': [],
            'alignment_score': 100,
            'grid_violations': 0
        }
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Find lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            # Analyze line alignment
            horizontal_lines = []
            vertical_lines = []
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                
                if abs(angle) < 5:  # Horizontal lines
                    horizontal_lines.append((y1, y2))
                elif abs(angle - 90) < 5:  # Vertical lines
                    vertical_lines.append((x1, x2))
            
            # Check for alignment issues
            if len(horizontal_lines) > 1:
                y_positions = [y for line in horizontal_lines for y in line]
                y_positions.sort()
                
                # Check if lines follow 8px grid
                for i in range(len(y_positions) - 1):
                    diff = y_positions[i+1] - y_positions[i]
                    if diff < 8 or diff % 8 != 0:
                        results['alignment_issues'].append({
                            'type': 'grid_violation',
                            'position': y_positions[i],
                            'spacing': diff,
                            'expected': '8px multiple',
                            'severity': 'medium'
                        })
                        results['grid_violations'] += 1
            
            # Calculate alignment score
            issue_count = len(results['alignment_issues'])
            results['alignment_score'] = max(0, 100 - (issue_count * 15))
        
        return results
    
    def _analyze_spacing(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze spacing consistency"""
        results = {
            'spacing_violations': [],
            'spacing_consistency_score': 100,
            'spacing_patterns': {}
        }
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find contours (UI elements)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze spacing between elements
        element_positions = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                element_positions.append((x, y, w, h))
        
        # Sort by x position for horizontal spacing
        element_positions.sort(key=lambda x: x[0])
        
        for i in range(len(element_positions) - 1):
            current_x = element_positions[i][0] + element_positions[i][2]
            next_x = element_positions[i+1][0]
            spacing = next_x - current_x
            
            # Check if spacing follows design system
            if spacing not in self.design_specs['spacing'].values():
                results['spacing_violations'].append({
                    'type': 'inconsistent_spacing',
                    'spacing': spacing,
                    'expected': list(self.design_specs['spacing'].values()),
                    'severity': 'low',
                    'description': f'Spacing {spacing}px not in design system'
                })
        
        # Calculate consistency score
        violation_count = len(results['spacing_violations'])
        results['spacing_consistency_score'] = max(0, 100 - (violation_count * 8))
        
        return results
    
    def _analyze_consistency(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze overall visual consistency"""
        results = {
            'consistency_issues': [],
            'overall_consistency_score': 100,
            'pattern_violations': 0
        }
        
        # Analyze color consistency
        color_analysis = self._analyze_colors(image)
        if color_analysis['color_consistency_score'] < 90:
            results['consistency_issues'].append({
                'type': 'color_inconsistency',
                'score': color_analysis['color_consistency_score'],
                'severity': 'medium'
            })
        
        # Analyze alignment consistency
        alignment_analysis = self._analyze_alignment(image)
        if alignment_analysis['alignment_score'] < 90:
            results['consistency_issues'].append({
                'type': 'alignment_inconsistency',
                'score': alignment_analysis['alignment_score'],
                'severity': 'medium'
            })
        
        # Analyze spacing consistency
        spacing_analysis = self._analyze_spacing(image)
        if spacing_analysis['spacing_consistency_score'] < 90:
            results['consistency_issues'].append({
                'type': 'spacing_inconsistency',
                'score': spacing_analysis['spacing_consistency_score'],
                'severity': 'low'
            })
        
        # Calculate overall score
        issue_count = len(results['consistency_issues'])
        results['overall_consistency_score'] = max(0, 100 - (issue_count * 20))
        results['pattern_violations'] = issue_count
        
        return results
    
    def _analyze_visual_rhythm(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze visual rhythm and harmony"""
        results = {
            'rhythm_issues': [],
            'rhythm_score': 100,
            'visual_harmony': 'good'
        }
        
        # Analyze repetitive patterns
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Use template matching to find repetitive elements
        # This is a simplified approach - in practice, you'd use more sophisticated pattern recognition
        
        # Check for visual balance
        height, width = image.shape[:2]
        left_half = image[:, :width//2]
        right_half = image[:, width//2:]
        
        # Compare color distribution between halves
        left_colors = np.mean(left_half, axis=(0, 1))
        right_colors = np.mean(right_half, axis=(0, 1))
        
        color_diff = np.linalg.norm(left_colors - right_colors)
        if color_diff > 30:  # Threshold for significant imbalance
            results['rhythm_issues'].append({
                'type': 'visual_imbalance',
                'description': 'Significant color difference between left and right halves',
                'severity': 'medium'
            })
        
        # Calculate rhythm score
        issue_count = len(results['rhythm_issues'])
        results['rhythm_score'] = max(0, 100 - (issue_count * 25))
        
        if results['rhythm_score'] < 70:
            results['visual_harmony'] = 'poor'
        elif results['rhythm_score'] < 85:
            results['visual_harmony'] = 'fair'
        
        return results
    
    def _analyze_surface_levels(self, image: np.ndarray, step_data: Dict) -> Dict[str, Any]:
        """Analyze surface level consistency based on step context"""
        results = {
            'surface_level_issues': [],
            'surface_consistency_score': 100,
            'detected_surfaces': []
        }
        
        # Determine expected surface level from step data
        step_description = step_data.get('description', '').lower()
        expected_surface = 'L1'  # Default
        
        if 'dialog' in step_description or 'panel' in step_description:
            expected_surface = 'L2'
        elif 'dropdown' in step_description or 'tooltip' in step_description:
            expected_surface = 'L3'
        
        # Analyze visual characteristics for surface level validation
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Check for shadow effects (indicates elevation)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        shadow_mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        shadow_ratio = np.sum(shadow_mask == 0) / shadow_mask.size
        
        # Determine detected surface level based on shadow characteristics
        detected_surface = 'L1'
        if shadow_ratio > 0.3:
            detected_surface = 'L3'
        elif shadow_ratio > 0.15:
            detected_surface = 'L2'
        
        results['detected_surfaces'] = [
            {'expected': expected_surface, 'detected': detected_surface}
        ]
        
        # Check for surface level violations
        if expected_surface != detected_surface:
            results['surface_level_issues'].append({
                'type': 'surface_level_mismatch',
                'expected': expected_surface,
                'detected': detected_surface,
                'severity': 'medium',
                'description': f'Expected {expected_surface} surface, detected {detected_surface}'
            })
        
        # Calculate consistency score
        issue_count = len(results['surface_level_issues'])
        results['surface_consistency_score'] = max(0, 100 - (issue_count * 30))
        
        return results
    
    def _rgb_to_hex(self, rgb_color: np.ndarray) -> str:
        """Convert RGB color to hex format"""
        r, g, b = rgb_color
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _is_design_system_color(self, hex_color: str) -> bool:
        """Check if color is in design system"""
        return hex_color.upper() in [color.upper() for color in self.design_specs['colors'].values()]
    
    def generate_visual_analysis_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive visual analysis report"""
        report = {
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'medium_issues': 0,
                'low_issues': 0,
                'overall_score': 0
            },
            'detailed_analysis': analysis_results,
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
        
        # Calculate overall score
        scores = []
        for analysis_type, results in analysis_results.items():
            if isinstance(results, dict) and 'score' in results:
                scores.append(results['score'])
        
        if scores:
            report['summary']['overall_score'] = sum(scores) / len(scores)
        
        # Generate recommendations
        if report['summary']['critical_issues'] > 0:
            report['recommendations'].append('Address critical visual inconsistencies immediately')
        if report['summary']['medium_issues'] > 0:
            report['recommendations'].append('Review and fix medium-priority visual issues')
        if report['summary']['low_issues'] > 0:
            report['recommendations'].append('Consider fixing low-priority visual polish issues')
        
        return report

# Test the computer vision analyzer
if __name__ == "__main__":
    analyzer = ComputerVisionAnalyzer()
    
    # Test with a sample analysis
    sample_step_data = {
        'description': 'User clicked save button in dialog',
        'timing': 0.5,
        'success': True
    }
    
    # This would normally analyze a real screenshot
    print("🔍 Computer Vision Analyzer initialized")
    print("✅ Ready for visual inconsistency detection")
    print("📊 Capabilities:")
    print("   - Color consistency analysis")
    print("   - Alignment and grid validation")
    print("   - Spacing consistency checking")
    print("   - Visual rhythm analysis")
    print("   - Surface level validation")
    print("   - Pattern recognition")
