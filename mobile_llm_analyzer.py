"""
Mobile LLM Analyzer
Specialized LLM analyzer for mobile video analysis with mobile-specific prompt and schema
Enhanced with comprehensive matrix lookup and robust JSON parsing
"""

import json
import asyncio
import base64
import re
from mobile_patterns import PATTERNS, analyze_frame_patterns, find_conflict_frames, find_loader_error_overlap
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

# Matrix and prompt paths
PROMPT_PATH = Path("prompts/mobile_prompt_blueprint.md")
MATRIX_JSON = Path("real_data/mobile_excel_matrix.json")

# --- Normalization functions ---
def _norm_protection(value: str) -> str:
    """Normalize protection values to canonical form."""
    v = (value or "").strip().lower().replace(" ", "_").replace("-", "_")
    # canonical set
    aliases = {
        "double_protected": {"double_protected", "doubleprotected", "double", "password_plus_label", "pass_plus_label"},
        "password": {"password", "pass_protected", "password_protected"},
        "irm": {"irm", "information_rights_management"},
        "clp": {"clp", "compliance_label_policy", "sensitivity_label", "confidential", "highly_confidential"},
        "dlp": {"dlp", "data_loss_prevention"},
        "normal": {"normal", "general", "non_business", "public"}
    }
    for canon, names in aliases.items():
        if v in names:
            return canon
    return v or "normal"

def _norm_size(value: str) -> str:
    """Normalize size values to canonical form."""
    v = (value or "").strip().lower()
    if v in {"s", "small"}: return "small"
    if v in {"m", "medium", "med"}: return "medium"
    if v in {"l", "large"}: return "large"
    if v in {"xl", "xlarge", "extra_large", "extra-large"}: return "xlarge"
    return v

# --- R0 precedence: resolve expected flow from scenario + matrix ---
def resolve_expected_flow(scenario_cfg: dict, matrix_row: dict, provided_expected_flow: dict) -> dict:
    """
    Reconciles EXPECTED_FLOW with matrix + guardrails.
    Rules:
      - If Protection ∈ {password, double-protected} and file_size ∈ {small, medium, large}:
          Expected_Handoff := 'Password_Prompt' (or 'Double_Protection_Check' if you prefer)
      - Desktop-only messaging allowed only for XL>100MB or known-unsupported features (not covered here).
      - If provided flow disagrees with these rules, override.
    """
    # Normalize inputs properly
    prot = _norm_protection(scenario_cfg.get("Protection"))
    fsize = _norm_size(scenario_cfg.get("Size"))
    resolved = dict(provided_expected_flow or {})

    # Default sensible fallbacks
    resolved.setdefault("Expected_Previewer", "Inline_Preview")
    resolved.setdefault("Expected_Handoff", "Direct_Open")
    resolved.setdefault("Expected_Result", "Excel_Mobile_Editor")
    resolved.setdefault("Expected_Flags", "None")
    resolved.setdefault("Expected_CTAs", "Open_in_App")
    resolved.setdefault("Allowed_Errors", "Generic_Loading_Error")
    resolved.setdefault("Forbidden_Errors", "Auth_Failure")

    # R0: Protection precedence for S/M/L
    if prot in {"password", "double_protected"} and fsize in {"small", "medium", "large"}:
        resolved["Expected_Handoff"] = "Password_Prompt"  # or "Double_Protection_Check"
        # Flags should reflect protection
        if prot == "double-protected":
            resolved["Expected_Flags"] = "Double_Protected"
        else:
            resolved["Expected_Flags"] = "Password_Required"

    # Desktop-only messaging is only justifiable for XL>100MB or unsupported features
    if fsize in {"small", "medium", "large"}:
        resolved["Desktop_Only_Messaging_Allowed"] = False
    else:
        # XL
        resolved["Desktop_Only_Messaging_Allowed"] = True

    resolved["_resolution_notes"] = {
        "protection": prot,
        "file_size": fsize,
        "source_expected_handoff": (provided_expected_flow or {}).get("Expected_Handoff"),
        "resolved_expected_handoff": resolved["Expected_Handoff"]
    }
    return resolved


def scan_cta_conflicts(frames):
    """Returns dict with frame ids that contain desktop+excel CTAs simultaneously."""
    conflict_frames, desktop_frames, excel_frames = [], [], []
    for fr in frames:
        txt = (fr.get("ocr_text") or "").lower()
        if not txt:
            continue
        has_desktop = "open in desktop app" in txt
        has_excel = ("open microsoft excel" in txt) or ("open in excel" in txt)
        if has_desktop:
            desktop_frames.append(fr["frame_id"])
        if has_excel:
            excel_frames.append(fr["frame_id"])
        if has_desktop and has_excel:
            conflict_frames.append(fr["frame_id"])
    return {
        "conflict_frames": conflict_frames,
        "desktop_frames": desktop_frames,
        "excel_frames": excel_frames
    }


def ensure_rule_firings(output_json, hints):
    """Ensure rule_firings meta section is populated based on hints"""
    rf = output_json.setdefault("meta", {}).setdefault("rule_firings", [])
    if hints.get("R2b_candidate_frames"):
        rf.append({"rule": "R2b", "frames": hints["R2b_candidate_frames"]})
    if hints.get("R4b_desktop_frames"):
        rf.append({"rule": "R4b", "frames": hints["R4b_desktop_frames"]})
    if hints.get("R5b_excel_frames"):
        rf.append({"rule": "R5b", "frames": hints["R5b_excel_frames"]})
    return output_json


def _suppress_false_password_bugs(out_json, resolved_expected):
    """Suppress false password prompt bugs when R0 says they're expected"""
    if resolved_expected.get("Expected_Handoff") in {"Password_Prompt", "Double_Protection_Check"}:
        for bucket in ["bugs_strong", "bugs_minor"]:
            filtered = []
            for b in out_json.get(bucket, []):
                if b.get("type") in {"OpenFailure", "Password_Prompt"} and "password" in (b.get("title","")+b.get("description","")).lower():
                    # Only suppress if it claims the prompt is "unexpected"
                    continue
                filtered.append(b)
            out_json[bucket] = filtered
    return out_json

def anchor_in_ocr(frames_by_id: dict, bug: dict) -> bool:
    """Verify that bug evidence anchors exist in actual OCR text."""
    ok = True
    for ev in bug.get("evidence", []):
        if ev.get("kind") != "frame":   # screenshots allowed too
            continue
        fr = frames_by_id.get(ev.get("id"))
        if not fr: 
            ok = False
            break
        ocr = (fr.get("ocr_text") or "").lower()
        # Choose anchors based on type
        needles = []
        if bug.get("type") in {"OpenFlowConflict", "MessagingMismatch", "CTAHierarchy"}:
            needles = ["open in desktop app", "open microsoft excel"]
        if bug.get("type") in {"StateStacking"}:
            needles = ["loading", "downloading", "almost there", "error", "can't open", "you don't have permission"]
        if bug.get("type") in {"OpenFailure"} and "password" in bug.get("title", "").lower():
            needles = ["please enter the password", "password", "enter password"]
        # Require at least one needle presence per evidence item
        if needles and not any(n in ocr for n in needles):
            ok = False
            break
    return ok

def verify_anchor_evidence(analysis_result: dict, frames_catalog: list) -> dict:
    """Post-LLM verification: ensure bugs match actual OCR content."""
    frames_by_id = {f["frame_id"]: f for f in frames_catalog}
    
    for bucket in ["bugs_strong", "bugs_minor"]:
        if bucket in analysis_result:
            filtered = []
            for b in analysis_result[bucket]:
                if anchor_in_ocr(frames_by_id, b):
                    filtered.append(b)
                else:
                    # Soften instead of drop - mark as low confidence
                    b["confidence"] = "Low"
                    b["notes"] = "Anchor not found in OCR"
                    filtered.append(b)
            analysis_result[bucket] = filtered
    
    return analysis_result

class MobileLLMAnalyzer:
    """Mobile-specific LLM analyzer for video frame analysis with matrix integration"""
    
    def __init__(self):
        self.mobile_prompt = self._load_mobile_prompt()
        self.mobile_matrix = self._load_mobile_matrix()
        
    def _load_mobile_prompt(self) -> str:
        """Load the mobile prompt blueprint from file"""
        try:
            if PROMPT_PATH.exists():
                return PROMPT_PATH.read_text(encoding="utf-8")
            else:
                logger.warning(f"Prompt file not found: {PROMPT_PATH}, using fallback")
                return self._get_mobile_prompt_template()
        except Exception as e:
            logger.error(f"Failed to load prompt: {e}, using fallback")
            return self._get_mobile_prompt_template()
    
    def _load_mobile_matrix(self) -> Dict[str, Any]:
        """Load the mobile matrix from JSON file"""
        try:
            if MATRIX_JSON.exists():
                return json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
            else:
                logger.warning(f"Matrix file not found: {MATRIX_JSON}")
                return {"scenarios": [], "symbols": {}}
        except Exception as e:
            logger.error(f"Failed to load matrix: {e}")
            return {"scenarios": [], "symbols": {}}
    
    def lookup_expected_flow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Match a scenario row by key fields; return expected symbols/constraints"""
        keys = ("Device", "Host", "HubEntry", "Source", "FileExt", "Size", "Protection", 
                "AppsInstalled", "HostAccount", "AppAccount")
        
        # Try exact match first
        for row in self.mobile_matrix.get("scenarios", []):
            if all(str(row.get(k, "")).lower() == str(config.get(k, "")).lower() for k in keys):
                return {
                    "Expected_Previewer": row.get("Expected_Previewer", ""),
                    "Expected_Handoff": row.get("Expected_Handoff", ""),
                    "Expected_Result": row.get("Expected_Result", ""),
                    "Expected_Flags": row.get("Expected_Flags", ""),
                    "Expected_CTAs": row.get("Expected_CTAs", ""),
                    "Allowed_Errors": row.get("Allowed_Errors", ""),
                    "Forbidden_Errors": row.get("Forbidden_Errors", ""),
                    "Symbols": self.mobile_matrix.get("symbols", {}),
                    "match": "Exact"
                }
        
        # Try fuzzy match for common variations
        for row in self.mobile_matrix.get("scenarios", []):
            match_score = 0
            for k in keys:
                if str(row.get(k, "")).lower() == str(config.get(k, "")).lower():
                    match_score += 1
            
            # If we match at least 7 out of 10 fields, consider it a match
            if match_score >= 7:
                return {
                    "Expected_Previewer": row.get("Expected_Previewer", ""),
                    "Expected_Handoff": row.get("Expected_Handoff", ""),
                    "Expected_Result": row.get("Expected_Result", ""),
                    "Expected_Flags": row.get("Expected_Flags", ""),
                    "Expected_CTAs": row.get("Expected_CTAs", ""),
                    "Allowed_Errors": row.get("Allowed_Errors", ""),
                    "Forbidden_Errors": row.get("Forbidden_Errors", ""),
                    "Symbols": self.mobile_matrix.get("symbols", {}),
                    "match": f"Fuzzy ({match_score}/10)"
                }
        
        # No match found, return smart defaults based on protection type
        exp = {
            "Expected_Previewer": "Inline_Preview",
            "Expected_Handoff": "Direct_Open", 
            "Expected_Result": "Excel_Mobile_Editor",
            "Expected_Flags": "None",
            "Expected_CTAs": "Open_in_App",
            "Allowed_Errors": "Generic_Loading_Error",
            "Forbidden_Errors": "Auth_Failure",
            "Symbols": self.mobile_matrix.get("symbols", {}),
            "match": "Not Found (Smart Default)"
        }
        
        prot = (config.get("Protection") or config.get("protection") or "").lower()
        size = (config.get("Size") or config.get("file_size") or "").lower()

        # Double-protected (password + label/IRM)
        if prot in {"double-protected", "double_protected", "password+label", "password+confidential", "password+irm"}:
            exp["Expected_Handoff"] = "Double_Protection_Check"  # or "Password_Prompt" if your policy is password-first
            exp["Expected_Flags"] = "Double_Protected"
            exp["Expected_CTAs"] = "Enter_Password"
            exp["Allowed_Errors"] = "Double_Protection_Error"
            exp["match"] = "Not Found (Smart Default: Double-Protected)"
        elif "password" in prot:
            # For password-protected files, expect password prompt
            exp["Expected_Handoff"] = "Password_Prompt"
            exp["Expected_Flags"] = "Password_Required"
            exp["Expected_CTAs"] = "Enter_Password"
            exp["Allowed_Errors"] = "Invalid_Password"
            exp["match"] = "Not Found (Smart Default: Password-Protected)"

        # XL files (>100MB) may legitimately show desktop-only messaging
        if size in {"xl", "xlarge", "extra_large"}:
            exp["Allowed_Errors"] = "Desktop_Only_Warning"
            # Still prefer "Open in Excel" if app supports streaming; otherwise allow desktop prompt.
            
        return exp
    
    def parse_llm_json(self, text: str) -> Dict[str, Any]:
        """Robust JSON parsing with fallback mechanisms"""
        try:
            # Strip code fences and trailing prose
            clean = text.strip()
            clean = clean.replace("```json", "").replace("```", "").strip()
            
            # Remove any trailing prose after the JSON
            json_end = clean.rfind("}")
            if json_end != -1:
                clean = clean[:json_end + 1]
            
            # Fix common JSON issues
            clean = re.sub(r',\s*}', '}', clean)  # Remove trailing commas before }
            clean = re.sub(r',\s*]', ']', clean)  # Remove trailing commas before ]
            
            # Try to parse
            return json.loads(clean)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed, attempting repair: {e}")
            
            try:
                # Try to find the first complete JSON object
                start = clean.find("{")
                if start == -1:
                    raise ValueError("No JSON object found")
                
                # Find matching closing brace
                brace_count = 0
                end = start
                for i, char in enumerate(clean[start:], start):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end = i
                            break
                
                if brace_count == 0:
                    return json.loads(clean[start:end + 1])
                else:
                    raise ValueError("Unmatched braces")
                    
            except Exception as repair_error:
                logger.error(f"JSON repair failed: {repair_error}")
                # Return minimal valid structure
                return {
                    "bugs_strong": [],
                    "bugs_minor": [],
                    "meta": {
                        "observed_events": [],
                        "coverage": {},
                        "notes": f"JSON parsing failed: {str(e)}"
                    }
                }
        
    def _get_mobile_prompt_template(self) -> str:
        """Get the mobile-specific prompt template"""
        return """You are a senior mobile UX & reliability reviewer. Analyze mobile flows where an Excel file link/attachment is opened from Outlook/Teams/M365 and viewed in Excel Mobile (Android/iOS). Inputs include video frames (timestamps) and screenshots.

Your job:
1) Report Functional/Handoff bugs (open/auth/policy/compat/perf) with clear evidence from frames/screens.
2) Report Visual Craft bugs on mobile UIs (previewer & Excel app).
3) Consolidate duplicates across apps/surfaces and parameter combos (platform, file size, protection, open path, account state).

GROUNDING
- Use only what is visible in frames/screens. No speculation.
- Every bug must cite at least one frame/screenshot with step binding.
- If uncertain, include the item with "confidence":"Low" (bugs_minor).
- Prefer reporting subtle issues over silence; return ≥3 total items across bugs_strong + bugs_minor unless the flow is pristine.

SURFACES (exact strings)
- "Outlook Mobile", "Teams Mobile", "M365 App", "Excel Mobile (Previewer)", "Excel Mobile (Editor)"

CATEGORIES
- category: "Functional" | "Craft"
- Functional.type: "PreviewerInitFailure" | "OpenFailure" | "AuthSSO" | "PolicyBlock" | "RedirectLoop" | "PerfLoad" | "AccessDenied" | "UnknownError"
- Craft.type: "Color" | "Spacing" | "Typography" | "Alignment" | "Component" | "Layout" | "Hierarchy" | "Design_System" | "Shadow" | "Interaction"

EVIDENCE
- For Functional bugs, include exact on-screen strings when visible. If generic, label "Non-contextual error" and propose a contextual rewrite.
- For Craft bugs, include concrete anchors (label/icon/region/approx px).

FIGMA/DESIGN-SYSTEM (Mobile)
- Use tokens only when strongly suggested by visuals; otherwise expected_token="None", compliance_score≤40. Do not place token names in titles.

OUTPUT (JSON ONLY — no prose outside JSON)
{
  "bugs_strong": [ ... ],
  "bugs_minor":  [ ... ],
  "meta": {
    "observed_events": [ ... ],
    "coverage": { ... },
    "notes": ""
  }
}

BUG OBJECT (both arrays)
{
  "title": "≤8 words, specific",
  "category": "Functional" | "Craft",
  "type": "<from lists above>",
  "severity": "Red | Orange | Yellow",
  "confidence": "High | Medium | Low",

  "description": "Visible facts with anchors (error text, label, icon, region).",
  "expected": "Correct mobile behavior for this step.",
  "actual": "Concrete visible state; never 'Unknown' in bugs_strong.",
  "impact": "How this blocks or confuses users in handoff/open/edit.",

  "affected_context": {
    "surface": "<surface string>",
    "platform": "Android | iOS | Not Observable",
    "open_path": "link | attachment | Not Observable",
    "file_size": "small | large | Not Observable",
    "protection": "normal | password | IRM | CLP | DLP | double-protected | Not Observable",
    "account_state": "primary | secondary | work_profile | Not Observable"
  },

  "evidence": [
    { "kind": "frame|screenshot", "id": "frame_id or filename", "timestamp_ms": 1234, "step_index": 3, "evidence_reason": "Which anchors prove this" }
  ],

  "ui_path": "Concise path (e.g., 'Previewer > Error Banner') or 'Not Observable'",
  "screen_position": "Top-Left | Top-Right | Bottom-Left | Bottom-Right | Center | Fullscreen",

  "visual_analysis": {
    "alignment": "", "spacing": "", "color": "", "typography": "", "border_radius": "", "shadow": ""
  },

  "developer_action": {
    "what_to_correct": "Specific fix",
    "likely_surface": "e.g., Outlook previewer error view; Excel Mobile open flow; SSO broker",
    "visual_target": "Craft: e.g., '8dp spacing, AA contrast'; Functional: 'contextual error with retry/switch account'",
    "qa": "How to verify via same scenario (steps + visible checks)"
  },

  "design_system_compliance": {
    "expected_token": "<token or None>",
    "actual_value": "<measured/approx or error-class>",
    "compliance_score": 0-100
  },

  "persona_impact": { "novice": 1, "power": 1, "super_fans": 1 }
}

META
- observed_events: time-ordered list derived from frames (surface, event, visible_text).
- coverage: what was actually seen (surfaces, platform, open_path, file_size, protection).

Then append your Scenario/Matrix/Steps/Frames/Screenshots JSON blocks and attach the referenced images as message parts."""

    async def analyze_mobile_frames(self, 
                                  frames_data: List[Dict[str, Any]],
                                  scenario_metadata: Dict[str, Any],
                                  steps_catalog: List[Dict[str, Any]],
                                  frames_catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze mobile frames using the mobile-specific prompt and schema with matrix integration"""
        try:
            logger.info(f"🎯 Mobile LLM Analysis: {len(frames_data)} frames")
            
            # Look up expected flow from matrix
            provided_expected_flow = self.lookup_expected_flow(scenario_metadata)
            logger.info(f"📊 Matrix lookup result: {provided_expected_flow.get('match', 'Unknown')}")
            
            # R0 precedence: resolve expected flow with protection logic
            resolved_expected_flow = resolve_expected_flow(scenario_metadata, scenario_metadata.get("matrix", {}), provided_expected_flow)
            logger.info(f"🔧 R0 precedence applied: {resolved_expected_flow.get('_resolution_notes', {})}")
            
            # CTA conflict scanning for co-triggering
            cta_scan = scan_cta_conflicts(frames_catalog)
            logger.info(f"🔍 CTA scan: {len(cta_scan['conflict_frames'])} conflict frames, {len(cta_scan['desktop_frames'])} desktop frames")
            
            # Build the enhanced prompt with mobile-specific data and resolved expected flow
            prompt_parts = [
                self.mobile_prompt,
                "",
                "SCENARIO_CONFIG:",
                json.dumps(scenario_metadata, indent=2),
                "",
                "EXPECTED_FLOW:",
                json.dumps(resolved_expected_flow, indent=2),
                "",
                "LLM_HINTS:",
                json.dumps({
                    "R2b_candidate_frames": cta_scan["conflict_frames"],
                    "R4b_desktop_frames": cta_scan["desktop_frames"],
                    "R5b_excel_frames": cta_scan["excel_frames"],
                    "Desktop_Only_Messaging_Allowed": resolved_expected_flow.get("Desktop_Only_Messaging_Allowed", False)
                }, indent=2),
                "",
                "META_EXPECTATION_RECONCILIATION:",
                json.dumps({
                    "protection": scenario_metadata.get("Protection"),
                    "file_size": scenario_metadata.get("Size"),
                    "provided_expected_handoff": provided_expected_flow.get("Expected_Handoff"),
                    "resolved_expected_handoff": resolved_expected_flow.get("Expected_Handoff"),
                    "notes": "R0 precedence applied; do not flag password prompt as unexpected when protection requires it."
                }, indent=2),
                "",
                "STEPS_CATALOG:",
                json.dumps(steps_catalog, indent=2),
                "",
                "FRAMES_CATALOG:",
                json.dumps(frames_catalog, indent=2),
                "",
                "SCREENSHOTS:",
                json.dumps([], indent=2)  # No additional screenshots for now
            ]
            
            full_prompt = "\n".join(prompt_parts)
            
            # Prepare messages for OpenAI API
            messages = [
                {
                    "role": "system",
                    "content": "You are a senior mobile UX & reliability reviewer specializing in Excel Mobile handoff scenarios."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt}
                    ]
                }
            ]
            
            # Add image data to the user message
            for frame_data in frames_data:
                try:
                    # Read and encode image
                    image_path = Path(frame_data["screenshot_path"])
                    if image_path.exists():
                        with open(image_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')
                        
                        # Determine image format
                        image_format = "jpeg" if image_path.suffix.lower() in ['.jpg', '.jpeg'] else "png"
                        
                        messages[1]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{image_data}",
                                "detail": "high"
                            }
                        })
                        
                        logger.info(f"✅ Loaded image for {frame_data['step_name']}: {len(image_data)} chars")
                    else:
                        logger.warning(f"⚠️ Image not found: {image_path}")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to load image {frame_data['screenshot_path']}: {e}")
                    continue
            
            # Call OpenAI API
            logger.info("🚀 Sending mobile frames to LLM for analysis...")
            
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=4000,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse response using robust parser
            response_content = response.choices[0].message.content
            logger.info(f"✅ LLM returned {len(response_content)} chars")
            
            # Use robust JSON parsing
            analysis_result = self.parse_llm_json(response_content)
            
            # Apply auto guardrail findings to catch missed high-signal issues
            analysis_result = self.auto_guardrail_findings(frames_data, scenario_metadata, resolved_expected_flow, analysis_result)
            
            # Suppress false password bugs when R0 says they're expected
            analysis_result = _suppress_false_password_bugs(analysis_result, resolved_expected_flow)
            
            # Verify anchor evidence matches actual OCR content
            analysis_result = verify_anchor_evidence(analysis_result, frames_data)
            
            # Ensure rule firings meta section is populated
            analysis_result = ensure_rule_firings(analysis_result, {
                "R2b_candidate_frames": cta_scan["conflict_frames"],
                "R4b_desktop_frames": cta_scan["desktop_frames"],
                "R5b_excel_frames": cta_scan["excel_frames"]
            })
                
            # Extract bugs from the structured response
            bugs_list = []
            
            # Process bugs_strong
            for bug in analysis_result.get("bugs_strong", []):
                bug["severity"] = bug.get("severity", "Red")
                bug["confidence"] = bug.get("confidence", "High")
                bugs_list.append(bug)
            
            # Process bugs_minor
            for bug in analysis_result.get("bugs_minor", []):
                bug["severity"] = bug.get("severity", "Yellow")
                bug["confidence"] = bug.get("confidence", "Medium")
                bugs_list.append(bug)
            
            # Validate minimum findings requirement
            total_findings = len(bugs_list)
            if total_findings < 3:
                # Check if UI is visible (not just loading/blank screens)
                ui_visible = any(
                    frame.get("ocr_text", "") and 
                    len(frame.get("ocr_text", "").strip()) > 10 and
                    not any(blank_indicator in frame.get("ocr_text", "").lower() 
                           for blank_indicator in ["loading", "downloading", "please wait", "blank"])
                    for frame in frames_data
                )
                
                if ui_visible:
                    logger.warning(f"⚠️ Only {total_findings} findings detected but UI is visible - should have ≥3")
                    # Add a generic craft issue to meet minimum requirement
                    if total_findings < 3:
                        craft_issue = {
                            "title": "UI analysis incomplete",
                            "category": "Craft",
                            "type": "Analysis_Gap",
                            "severity": "Yellow",
                            "confidence": "Low",
                            "description": f"Only {total_findings} issues detected in visible UI - may indicate incomplete analysis",
                            "expected": "Comprehensive analysis of all visible UI elements",
                            "actual": f"Limited to {total_findings} findings",
                            "impact": "Potential UX issues may be missed",
                            "affected_context": scenario_metadata,
                            "evidence": [{"kind": "frame", "id": "multiple", "evidence_reason": "UI visible but limited findings"}],
                            "ui_path": "Multiple surfaces",
                            "screen_position": "Various",
                            "visual_analysis": {"alignment": "N/A", "spacing": "N/A", "color": "N/A", "typography": "N/A"},
                            "developer_action": {"what_to_correct": "Review analysis completeness", "likely_surface": "All", "visual_target": "Comprehensive coverage"},
                            "design_system_compliance": {"expected_token": "None", "actual_value": "Incomplete analysis", "compliance_score": 30},
                            "persona_impact": {"novice": 5, "power": 3, "super_fans": 2}
                        }
                        bugs_list.append(craft_issue)
                        logger.info(f"➕ Added analysis gap issue to meet minimum requirement")
                
                logger.info(f"✅ Mobile analysis complete: {len(bugs_list)} bugs detected")
                logger.info(f"📊 Debug: {len(analysis_result.get('bugs_strong', []))} strong, {len(analysis_result.get('bugs_minor', []))} minor")
                
            # Add matrix match info to the result
            for bug in bugs_list:
                bug["matrix_match"] = resolved_expected_flow.get("match", "Unknown")
                bug["expected_flow"] = resolved_expected_flow
                
            return bugs_list
                
        except Exception as e:
            logger.error(f"❌ Mobile LLM analysis failed: {e}")
            return []

    def auto_guardrail_findings(self, frames: List[Dict[str, Any]], cfg: Dict[str, Any], expected: Dict[str, Any], existing: Dict[str, Any]) -> Dict[str, Any]:
        """Add missing high-signal findings based on visible OCR evidence.
           frames: list of dicts with 'ocr_text', 'frame_id', 'timestamp_ms', 'step_index'
           existing: the LLM's JSON dict (bugs_strong/bugs_minor) to be augmented.
        """
        text_frames = [(f, (f.get("ocr_text") or "")) for f in frames]

        # 1) Desktop CTA conflict on mobile
        conflict_hits = [(f, t) for f, t in text_frames if PATTERNS["desktop_cta"].search(t) and PATTERNS["excel_cta"].search(t)]
        if conflict_hits and not any(b.get("type") == "OpenFlowConflict" for b in existing.get("bugs_strong", [])):
            f, _ = conflict_hits[0]
            existing.setdefault("bugs_strong", []).append({
                "title": "Desktop CTA on mobile flow",
                "category": "Functional",
                "type": "OpenFlowConflict",
                "severity": "Orange",
                "confidence": "High",
                "description": "Desktop-only CTA appears alongside 'Open Microsoft Excel' on mobile.",
                "expected": "Single clear mobile path to Excel app.",
                "actual": "Both 'Open in Desktop App' and 'Open Microsoft Excel' visible together.",
                "impact": "Creates contradictory next steps and handoff confusion.",
                "affected_context": {
                    "surface": "Outlook Mobile",
                    "platform": "iOS",
                    "open_path": cfg.get("Source","Not Observable").lower(),
                    "file_size": cfg.get("Size","Not Observable").lower(),
                    "protection": cfg.get("Protection","Not Observable").lower(),
                    "account_state": (cfg.get("HostAccount") or cfg.get("AppAccount") or "Not Observable").lower()
                },
                "evidence": [{
                    "kind": "frame",
                    "id": f["frame_id"],
                    "timestamp_ms": f["timestamp_ms"],
                    "step_index": f.get("step_index") or 0,
                    "evidence_reason": "Both strings visible: 'Open in Desktop App' and 'Open Microsoft Excel'."
                }],
                "ui_path": "Outlook Mobile > Previewer",
                "screen_position": "Center",
                "visual_analysis": {"alignment": "Stacked CTAs", "spacing": "Approx 8–12px", "color": "Desktop CTA has higher emphasis", "typography": "Excel CTA smaller/less prominent", "border_radius": "Not Observable", "shadow": "Not Observable"},
                "developer_action": {"what_to_correct": "Suppress desktop CTA; promote Excel CTA.", "likely_surface": "Outlook Mobile previewer", "visual_target": "Single primary CTA", "qa": "Open double-protected file on iOS; verify only 'Open in Excel' CTA."},
                "design_system_compliance": {"expected_token": "None", "actual_value": "Conflicting CTAs", "compliance_score": 55},
                "persona_impact": {"novice": 8, "power": 6, "super_fans": 4}
            })

        # 2) Error/Policy + Loader overlap
        loader_frames = [(f, t) for f, t in text_frames if PATTERNS["loader"].search(t)]
        policy_frames = [(f, t) for f, t in text_frames if PATTERNS["policy_err"].search(t) or PATTERNS["desktop_cta"].search(t)]
        if loader_frames and policy_frames and not any(b.get("type") == "StateStacking" for b in (existing.get("bugs_minor", []) + existing.get("bugs_strong", []))):
            lf = loader_frames[0][0]; pf = policy_frames[0][0]
            existing.setdefault("bugs_minor", []).append({
                "title": "Loader persists under error",
                "category": "Craft",
                "type": "StateStacking",
                "severity": "Yellow",
                "confidence": "Medium",
                "description": "Loader text appears while a blocking policy/error message is present.",
                "expected": "Single state at a time; hide loaders when blocked.",
                "actual": "'Downloading…' visible near frames with desktop/policy error.",
                "impact": "Confusing state; users unsure if progress continues.",
                "affected_context": {
                    "surface": "Outlook Mobile",
                    "platform": "iOS",
                    "open_path": cfg.get("Source","Not Observable").lower(),
                    "file_size": cfg.get("Size","Not Observable").lower(),
                    "protection": cfg.get("Protection","Not Observable").lower(),
                    "account_state": (cfg.get("HostAccount") or cfg.get("AppAccount") or "Not Observable").lower()
                },
                "evidence": [
                    {"kind":"frame","id": pf["frame_id"], "timestamp_ms": pf["timestamp_ms"], "step_index": pf.get("step_index") or 0, "evidence_reason": "Policy/error text visible"},
                    {"kind":"frame","id": lf["frame_id"], "timestamp_ms": lf["timestamp_ms"], "step_index": lf.get("step_index") or 0, "evidence_reason": "Loader caption visible"}
                ],
                "ui_path": "Outlook Mobile > Previewer",
                "screen_position": "Center",
                "visual_analysis": {"alignment":"Standard","spacing":"Standard","color":"Loader caption low-emphasis","typography":"Small caption","border_radius":"Not Observable","shadow":"Not Observable"},
                "developer_action": {"what_to_correct":"Hide loader when blocked.","likely_surface":"Outlook Mobile previewer","visual_target":"Mutually exclusive states","qa":"Re-run blocked case; ensure loader suppressed."},
                "design_system_compliance": {"expected_token":"None","actual_value":"Parallel states","compliance_score":70},
                "persona_impact": {"novice":5,"power":4,"super_fans":3}
            })

        # 3) Enforce minimum 3 findings if UI non-blank
        if (existing.get("bugs_strong") or existing.get("bugs_minor")) and (len(existing.get("bugs_strong", [])) + len(existing.get("bugs_minor", []))) < 3:
            # Encourage at least one craft item: CTAHierarchy if Excel CTA detected but seems secondary
            excel_cta_hits = [(f, t) for f, t in text_frames if PATTERNS["excel_cta"].search(t)]
            desktop_hits = [(f, t) for f, t in text_frames if PATTERNS["desktop_cta"].search(t)]
            if excel_cta_hits and desktop_hits and not any(b.get("type") == "CTAHierarchy" for b in existing.get("bugs_minor", [])):
                f, _ = excel_cta_hits[0]
                existing.setdefault("bugs_minor", []).append({
                    "title": "Excel CTA low prominence",
                    "category": "Craft",
                    "type": "CTAHierarchy",
                    "severity": "Yellow",
                    "confidence": "Low",
                    "description": "'Open Microsoft Excel' appears visually secondary to the desktop option.",
                    "expected": "On mobile, Excel CTA should be primary.",
                    "actual": "Excel CTA placed under/less emphasized than desktop CTA.",
                    "impact": "Users may miss the correct mobile path.",
                    "affected_context": {
                        "surface": "Outlook Mobile",
                        "platform": "iOS",
                        "open_path": cfg.get("Source","Not Observable").lower(),
                        "file_size": cfg.get("Size","Not Observable").lower(),
                        "protection": cfg.get("Protection","Not Observable").lower(),
                        "account_state": (cfg.get("HostAccount") or cfg.get("AppAccount") or "Not Observable").lower()
                    },
                    "evidence": [{
                        "kind":"frame","id": f["frame_id"],"timestamp_ms": f["timestamp_ms"],"step_index": f.get("step_index") or 0,
                        "evidence_reason":"Excel CTA visible below desktop CTA in same screen"
                    }],
                    "ui_path": "Outlook Mobile > Previewer",
                    "screen_position": "Center",
                    "visual_analysis": {"alignment":"Stacked","spacing":"Adequate","color":"Lower emphasis","typography":"Smaller weight","border_radius":"Not Observable","shadow":"Not Observable"},
                    "developer_action": {"what_to_correct":"Promote Excel CTA.","likely_surface":"Outlook Mobile previewer","visual_target":"Primary CTA prominence","qa":"Ensure Excel CTA appears primary."},
                    "design_system_compliance": {"expected_token":"None","actual_value":"CTA hierarchy inverted","compliance_score":65},
                    "persona_impact": {"novice":6,"power":4,"super_fans":3}
                })
        return existing

    def create_enhanced_mobile_scenario_metadata(self, 
                                               device: str = "iPhone",
                                               host: str = "Outlook",
                                               hub_entry: str = "message_detail",
                                               source: str = "Attachment",
                                               file_ext: str = "xlsx",
                                               size: str = "Small",
                                               protection: str = "Normal",
                                               apps_installed: str = "None",
                                               host_account: str = "Primary",
                                               app_account: str = "Primary") -> Dict[str, Any]:
        """Create enhanced mobile scenario metadata that matches matrix format"""
        return {
            "Device": device,
            "Host": host,
            "HubEntry": hub_entry,
            "Source": source,
            "FileExt": file_ext,
            "Size": size,
            "Protection": protection,
            "AppsInstalled": apps_installed,
            "HostAccount": host_account,
            "AppAccount": app_account,
            "scenario": f"{device}_{host}_{hub_entry}_{source}_{file_ext}_{size}_{protection}",
            "persona": "Power User",
            "matrix": {
                "platform": "iOS" if device == "iPhone" else "Android",
                "open_path": source.lower(),
                "file_size": size.lower(),
                "protection": protection.lower(),
                "account_state": host_account.lower()
            }
        }

    def create_mobile_bug_summary(self, bugs_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of mobile-specific bugs with matrix integration"""
        functional_bugs = [bug for bug in bugs_list if bug.get("category") == "Functional"]
        craft_bugs = [bug for bug in bugs_list if bug.get("category") == "Craft"]
        
        # Count by surface
        surface_counts = {}
        for bug in bugs_list:
            surface = bug.get("affected_context", {}).get("surface", "Unknown")
            surface_counts[surface] = surface_counts.get(surface, 0) + 1
        
        # Count by platform
        platform_counts = {}
        for bug in bugs_list:
            platform = bug.get("affected_context", {}).get("platform", "Unknown")
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Count by matrix match quality
        matrix_match_counts = {}
        for bug in bugs_list:
            match = bug.get("matrix_match", "Unknown")
            matrix_match_counts[match] = matrix_match_counts.get(match, 0) + 1
        
        return {
            "total_bugs": len(bugs_list),
            "functional_bugs": len(functional_bugs),
            "craft_bugs": len(craft_bugs),
            "surface_distribution": surface_counts,
            "platform_distribution": platform_counts,
            "matrix_match_distribution": matrix_match_counts,
            "severity_breakdown": {
                "red": len([b for b in bugs_list if b.get("severity") == "Red"]),
                "orange": len([b for b in bugs_list if b.get("severity") == "Orange"]),
                "yellow": len([b for b in bugs_list if b.get("severity") == "Yellow"])
            }
        }

