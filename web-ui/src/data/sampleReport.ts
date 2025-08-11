// Enhanced sample report with full analytics modules for testing
export const ENHANCED_SAMPLE_REPORT = {
  "analysis_id": "enhanced_sample_20250809_test",
  "timestamp": "2025-08-09T12:00:00.000000",
  "type": "url_scenario",
  "url": "https://example.com",
  "overall_score": 84,
  "status": "completed",
  "total_issues": 8,
  "scenario_results": [
    {
      "name": "Page Load and Navigation",
      "score": 87,
      "status": "completed",
      "duration_ms": 2150,
      "steps": [
        {
          "action": "navigate_to_url",
          "status": "success",
          "duration_ms": 1200,
          "url": "https://example.com"
        },
        {
          "action": "wait_for_element",
          "status": "success", 
          "duration_ms": 300,
          "selector": "h1"
        },
        {
          "action": "accessibility_scan",
          "status": "success",
          "duration_ms": 650,
          "violations": 3
        }
      ]
    }
  ],
  "module_results": {
    "craft_bug": {
      "score": 78,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "UX Pattern Violation",
          "message": "Primary button lacks sufficient visual hierarchy - appears too similar to secondary actions",
          "severity": "medium",
          "element": ".btn-primary",
          "recommendation": "Increase button size, use stronger color contrast, or add visual weight through shadow/border",
          "ado_work_item_id": "12345",
          "ado_status": "Active",
          "ado_url": "https://dev.azure.com/your-org/_workitems/edit/12345"
        },
        {
          "type": "Information Architecture Issue",
          "message": "Menu structure contains more than 7 items in main navigation, violating Miller's Rule",
          "severity": "low",
          "element": ".main-nav",
          "recommendation": "Group related items into categories or use progressive disclosure"
        }
      ],
      "recommendations": [
        "Follow established design patterns for button hierarchy",
        "Limit main navigation to 5-7 top-level items",
        "Use progressive disclosure for complex information"
      ]
    },
    "accessibility": {
      "score": 81,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "Color Contrast",
          "message": "Text color contrast ratio is 3.2:1, below WCAG AA standard of 4.5:1",
          "severity": "medium",
          "element": ".secondary-text",
          "recommendation": "Darken text color to achieve minimum 4.5:1 contrast ratio",
          "fixed": true,
          "fix_timestamp": "2025-08-09T11:30:00.000000"
        },
        {
          "type": "Missing Alt Text",
          "message": "Decorative images missing alt attributes",
          "severity": "high",
          "element": "img.hero-image",
          "recommendation": "Add alt='' for decorative images or descriptive alt text for content images"
        }
      ],
      "recommendations": [
        "Ensure all interactive elements meet WCAG AA contrast requirements",
        "Provide meaningful alt text for all images",
        "Test with screen readers regularly"
      ]
    },
    "performance": {
      "score": 92,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "Large Bundle Size", 
          "message": "JavaScript bundle size exceeds 250KB, may impact load performance",
          "severity": "low",
          "element": "bundle.js",
          "recommendation": "Implement code splitting and lazy loading for non-critical features"
        }
      ],
      "recommendations": [
        "Optimize images and use modern formats (WebP, AVIF)",
        "Implement lazy loading for below-the-fold content", 
        "Use CDN for static assets"
      ]
    },
    "ux_heuristics": {
      "score": 88,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "User Control Violation",
          "message": "Auto-playing video without user control violates user autonomy",
          "severity": "medium",
          "element": ".hero-video",
          "recommendation": "Add play/pause controls and respect user's motion preferences"
        }
      ],
      "recommendations": [
        "Always provide user control over multimedia content",
        "Show system status through loading indicators",
        "Maintain consistency in navigation patterns"
      ]
    },
    "keyboard": {
      "score": 75,
      "threshold_met": false,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "Focus Indicators",
          "message": "Interactive elements lack visible focus indicators for keyboard navigation",
          "severity": "high",
          "element": ".btn, .nav-link",
          "recommendation": "Add clear focus styles with outline or border change"
        },
        {
          "type": "Tab Order",
          "message": "Tab order skips important interactive elements",
          "severity": "medium", 
          "element": ".sidebar-nav",
          "recommendation": "Review tabindex values and ensure logical tab sequence"
        }
      ],
      "recommendations": [
        "Ensure all interactive elements are keyboard accessible",
        "Provide visible focus indicators",
        "Test navigation with keyboard only"
      ]
    },
    "best_practices": {
      "score": 85,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [
        {
          "type": "Mobile Optimization",
          "message": "Viewport meta tag missing for responsive design",
          "severity": "medium",
          "element": "<head>",
          "recommendation": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>"
        }
      ],
      "recommendations": [
        "Follow responsive design principles",
        "Use semantic HTML elements",
        "Implement progressive enhancement"
      ]
    },
    "health_alerts": {
      "score": 95,
      "threshold_met": true,
      "analytics_enabled": true,
      "findings": [],
      "recommendations": [
        "Monitor for security vulnerabilities regularly",
        "Keep dependencies updated",
        "Implement error tracking and monitoring"
      ]
    }
  },
  "metadata": {
    "total_scenarios": 1,
    "total_steps": 3,
    "analysis_duration": 2.15,
    "scenarios_passed": 1,
    "analytics_features": ["craft_bug_detection", "accessibility_scan", "performance_audit"],
    "deterministic_mode": false
  },
  "storage_metadata": {
    "analysis_id": "enhanced_sample_20250809_test",
    "saved_timestamp": "2025-08-09T12:00:00.000000",
    "file_path": "reports/analysis/enhanced_sample_20250809_test.json",
    "filename": "enhanced_sample_20250809_test.json",
    "version": "2.0",
    "file_size_bytes": 4250
  },
  "ado_integration": {
    "work_items_created": 3,
    "last_sync_date": "2025-08-09T11:45:00.000000",
    "sync_status": "completed"
  }
};
