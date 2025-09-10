"""
Mobile Video UX Analyzer
Specialized analyzer for mobile Excel handoff scenarios (Outlook/Teams → Excel Mobile)
"""

import json
import asyncio
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path
import cv2
import logging
from datetime import datetime
import uuid

# OCR imports
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR not available - install pytesseract and Pillow for text extraction")

logger = logging.getLogger(__name__)

class MobileVideoAnalyzer:
    """Mobile-specific video analyzer for Excel handoff scenarios"""
    
    def __init__(self):
        self.mobile_prompt = self._get_mobile_prompt_template()
        
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

    def extract_frames_with_ocr(self, video_path: str, frame_interval: int = 2) -> List[Dict[str, Any]]:
        """Extract frames from video with OCR text extraction"""
        frames_catalog = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            frame_interval_frames = int(fps * frame_interval) if fps > 0 else 30
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Extract frame at specified intervals
                if frame_count % frame_interval_frames == 0:
                    timestamp_ms = int((frame_count / fps) * 1000) if fps > 0 else frame_count * 33
                    
                    # Extract OCR text if available
                    ocr_text = ""
                    if OCR_AVAILABLE:
                        try:
                            # Convert BGR to RGB for PIL
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_image = Image.fromarray(rgb_frame)
                            ocr_text = pytesseract.image_to_string(pil_image, config='--psm 6').strip()
                        except Exception as e:
                            logger.warning(f"OCR failed for frame {frame_count}: {e}")
                    
                    frame_id = f"f{extracted_count:04d}"
                    frame_info = {
                        "frame_id": frame_id,
                        "timestamp_ms": timestamp_ms,
                        "step_index": extracted_count + 1,  # Will be mapped to actual steps later
                        "image_ref": f"frames/{frame_id}_{timestamp_ms:06d}.jpg",
                        "ocr_text": ocr_text,
                        "frame_number": frame_count,
                        "timestamp_seconds": frame_count / fps if fps > 0 else 0
                    }
                    
                    frames_catalog.append(frame_info)
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"🎞️ Extracted {len(frames_catalog)} frames with OCR from video")
            return frames_catalog
            
        except Exception as e:
            logger.error(f"❌ Frame extraction failed: {e}")
            raise

    def create_mobile_scenario_metadata(self, 
                                      scenario_name: str = "excel_mobile_handoff",
                                      persona: str = "Power User",
                                      platform: str = "Android",
                                      open_path: str = "link",
                                      file_size: str = "large",
                                      protection: str = "password",
                                      account_state: str = "work_profile") -> Dict[str, Any]:
        """Create mobile scenario metadata with test matrix"""
        return {
            "scenario": scenario_name,
            "persona": persona,
            "matrix": {
                "platform": platform,
                "open_path": open_path,
                "file_size": file_size,
                "protection": protection,
                "account_state": account_state
            }
        }

    def create_mobile_steps_catalog(self, surface: str = "Outlook Mobile") -> List[Dict[str, Any]]:
        """Create mobile-specific steps catalog based on surface"""
        if surface == "Outlook Mobile":
            return [
                {"index": 1, "surface": "Outlook Mobile", "name": "Tap shared Excel link"},
                {"index": 2, "surface": "Outlook Mobile", "name": "Previewer initializing"},
                {"index": 3, "surface": "Excel Mobile (Previewer)", "name": "File preview visible"},
                {"index": 4, "surface": "Excel Mobile (Previewer)", "name": "View comments panel"},
                {"index": 5, "surface": "Excel Mobile (Previewer)", "name": "Use pan/zoom gestures"},
                {"index": 6, "surface": "Excel Mobile (Previewer)", "name": "Open in app"},
                {"index": 7, "surface": "Excel Mobile (Editor)", "name": "Workbook opened in app"}
            ]
        elif surface == "Teams Mobile":
            return [
                {"index": 1, "surface": "Teams Mobile", "name": "Tap shared Excel link in Teams"},
                {"index": 2, "surface": "Teams Mobile", "name": "Teams file viewer initializing"},
                {"index": 3, "surface": "Excel Mobile (Previewer)", "name": "Excel preview visible"},
                {"index": 4, "surface": "Excel Mobile (Previewer)", "name": "Open in app"},
                {"index": 5, "surface": "Excel Mobile (Editor)", "name": "Editor opened"}
            ]
        elif surface == "M365 App":
            return [
                {"index": 1, "surface": "M365 App", "name": "Tap shared Excel link in M365"},
                {"index": 2, "surface": "M365 App", "name": "M365 file viewer initializing"},
                {"index": 3, "surface": "Excel Mobile (Previewer)", "name": "Preview visible / error"},
                {"index": 4, "surface": "Excel Mobile (Previewer)", "name": "Open in app"},
                {"index": 5, "surface": "Excel Mobile (Editor)", "name": "Editor opened"}
            ]
        else:
            # Default generic steps
            return [
                {"index": 1, "surface": "Mobile App", "name": "Tap shared Excel link"},
                {"index": 2, "surface": "Mobile App", "name": "File viewer initializing"},
                {"index": 3, "surface": "Excel Mobile (Previewer)", "name": "File preview visible"},
                {"index": 4, "surface": "Excel Mobile (Previewer)", "name": "Open in app"},
                {"index": 5, "surface": "Excel Mobile (Editor)", "name": "Workbook opened in app"}
            ]

    def map_frames_to_steps(self, frames_catalog: List[Dict], steps_catalog: List[Dict]) -> List[Dict]:
        """Map frames to appropriate steps based on content analysis"""
        mapped_frames = []
        
        for i, frame in enumerate(frames_catalog):
            # Simple mapping: distribute frames evenly across steps
            step_index = min(i + 1, len(steps_catalog))
            frame["step_index"] = step_index
            mapped_frames.append(frame)
        
        return mapped_frames

    async def analyze_mobile_video(self, 
                                 video_path: str,
                                 scenario_metadata: Dict[str, Any],
                                 steps_catalog: List[Dict[str, Any]],
                                 frame_interval: int = 2) -> Dict[str, Any]:
        """Analyze mobile video with enhanced schema and mobile-specific prompt"""
        try:
            # Extract frames with OCR
            frames_catalog = self.extract_frames_with_ocr(video_path, frame_interval)
            
            # Map frames to steps
            mapped_frames = self.map_frames_to_steps(frames_catalog, steps_catalog)
            
            # Create the enhanced prompt with mobile-specific data
            prompt_parts = [
                self.mobile_prompt,
                "",
                "SCENARIO:",
                json.dumps(scenario_metadata, indent=2),
                "",
                "STEPS_CATALOG:",
                json.dumps(steps_catalog, indent=2),
                "",
                "FRAMES_CATALOG:",
                json.dumps(mapped_frames, indent=2),
                "",
                "SCREENSHOTS:",
                json.dumps([], indent=2)  # No additional screenshots for now
            ]
            
            full_prompt = "\n".join(prompt_parts)
            
            # For now, return the structured data
            # In a full implementation, this would call the LLM with the enhanced prompt
            return {
                "scenario_metadata": scenario_metadata,
                "steps_catalog": steps_catalog,
                "frames_catalog": mapped_frames,
                "prompt": full_prompt,
                "analysis_ready": True
            }
            
        except Exception as e:
            logger.error(f"❌ Mobile video analysis failed: {e}")
            raise

    def save_frames_to_disk(self, frames_catalog: List[Dict], video_path: str, output_dir: Path) -> List[Dict]:
        """Save extracted frames to disk and update image_ref paths"""
        frames_dir = output_dir / "frames"
        frames_dir.mkdir(exist_ok=True)
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            saved_frames = []
            frame_count = 0
            
            for frame_info in frames_catalog:
                # Seek to the specific frame
                target_frame = frame_info["frame_number"]
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                
                ret, frame = cap.read()
                if ret:
                    # Save frame
                    frame_filename = f"{frame_info['frame_id']}_{frame_info['timestamp_ms']:06d}.jpg"
                    frame_path = frames_dir / frame_filename
                    cv2.imwrite(str(frame_path), frame)
                    
                    # Update frame info with actual path
                    frame_info["image_ref"] = str(frame_path)
                    frame_info["saved_path"] = str(frame_path)
                    saved_frames.append(frame_info)
                    
                    logger.info(f"💾 Saved frame {frame_info['frame_id']} to {frame_path}")
            
            cap.release()
            return saved_frames
            
        except Exception as e:
            logger.error(f"❌ Frame saving failed: {e}")
            raise

