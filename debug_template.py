#!/usr/bin/env python3

import json
from jinja2 import Template

# Read the latest telemetry file
with open('telemetry_output/telemetry_document_creation_20250818_190010.json', 'r') as f:
    telemetry_data = json.load(f)

print("📊 Telemetry data keys:", list(telemetry_data.keys()))
print("📊 UX analysis results keys:", list(telemetry_data['ux_analysis_results'].keys()))

ux_analysis = telemetry_data['ux_analysis_results']
craft_bugs = ux_analysis.get("craft_bugs", [])
print(f"🎯 Craft bugs found: {len(craft_bugs)}")

# Prepare data for template (same as in FastAPI)
craft_bugs = ux_analysis.get("craft_bugs", [])
ux_score = ux_analysis.get("ux_score", 0)

# Determine UX score class for styling
if ux_score >= 80:
    ux_score_class = "success"
elif ux_score >= 60:
    ux_score_class = "warning"
else:
    ux_score_class = "error"

# Prepare steps data for template
steps = []
for step in telemetry_data.get("steps", []):
    step_data = {
        "name": step.get("step_name", "Unknown"),  # Use step_name from telemetry
        "duration_ms": step.get("duration_ms", 0),
        "success": step.get("success", False),
        "dialog_detected": step.get("dialog_detected", False),
        "dialog_type": step.get("dialog_type", ""),
        "interaction_attempted": step.get("interaction_attempted", False),
        "interaction_successful": step.get("interaction_successful", False),
        "status_class": "success" if step.get("success") else "error"
    }
    steps.append(step_data)

report_data = {
    "timestamp": "2025-08-18 19:00:10",
    "scenario_name": "Excel Document Creation",
    "telemetry": telemetry_data,
    "ux_analysis": ux_analysis,
    "craft_bugs": craft_bugs,
    "craft_bugs_count": len(craft_bugs),
    "ux_score": ux_score,
    "ux_score_class": ux_score_class,
    "total_steps": len(telemetry_data.get("steps", [])),
    "execution_time": round(telemetry_data.get("total_duration_ms", 0) / 1000, 1),
    "steps": steps,
    "performance_issues": ux_analysis.get("performance_issues", []),
    "interaction_issues": ux_analysis.get("interaction_issues", []),
    "recommendations": ux_analysis.get("recommendations", []),
    "report_id": f"excel_ux_{int(1755523810)}"
}

print(f"📊 Report data keys: {list(report_data.keys())}")
print(f"🎯 Craft bugs count in report_data: {report_data['craft_bugs_count']}")
print(f"📊 Steps count in report_data: {report_data['total_steps']}")
print(f"📊 UX score: {report_data['ux_score']}")

# Test template rendering
with open('excel_ux_report_template.html', 'r') as f:
    template_content = f.read()

template = Template(template_content)
html_content = template.render(**report_data)

# Check if craft bugs are in the rendered HTML
if "craft-bug" in html_content:
    print("✅ Craft bugs found in rendered HTML")
else:
    print("❌ No craft bugs found in rendered HTML")

# Save debug output
with open('debug_report.html', 'w') as f:
    f.write(html_content)

print("💾 Debug report saved to debug_report.html")
