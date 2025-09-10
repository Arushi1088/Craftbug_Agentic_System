#!/usr/bin/env python3
"""
Mobile video analysis patterns for OCR text matching
Centralized regex patterns for consistent detection across OCR and post-processing
"""

import re

# Compiled regex patterns for mobile video analysis
PATTERNS = {
    "desktop_cta": re.compile(r"\bOpen in Desktop App\b", re.I),
    "excel_cta": re.compile(r"\bOpen (Microsoft )?Excel\b", re.I),
    "loader": re.compile(r"\b(Downloading\.{0,3}|Loading\.{0,3}|Almost there)\b", re.I),
    "policy_err": re.compile(r"(can.?t open|you don.?t have permission|should be opened in Desktop app)", re.I),
    "password_prompt": re.compile(r"Please enter the password", re.I),
    "double_protected": re.compile(r"(double.?protected|password.*confidential|password.*sensitivity|password.*irm)", re.I),
    "file_size_xl": re.compile(r"(xl|xlarge|extra.?large|>.*100.*mb)", re.I),
    "error_generic": re.compile(r"(error|failed|unable|cannot)", re.I),
    "auth_required": re.compile(r"(sign in|authenticate|login|authorization)", re.I),
    "install_prompt": re.compile(r"(install|download.*app|get.*app)", re.I)
}

def match_pattern(pattern_name: str, text: str) -> bool:
    """Check if text matches a specific pattern"""
    if pattern_name not in PATTERNS:
        return False
    return bool(PATTERNS[pattern_name].search(text))

def find_pattern_matches(pattern_name: str, text: str) -> list:
    """Find all matches of a pattern in text"""
    if pattern_name not in PATTERNS:
        return []
    return PATTERNS[pattern_name].findall(text)

def get_pattern_regex(pattern_name: str) -> str:
    """Get the raw regex string for a pattern"""
    if pattern_name not in PATTERNS:
        return ""
    return PATTERNS[pattern_name].pattern

# Convenience functions for common checks
def has_desktop_cta(text: str) -> bool:
    """Check if text contains desktop CTA"""
    return match_pattern("desktop_cta", text)

def has_excel_cta(text: str) -> bool:
    """Check if text contains Excel CTA"""
    return match_pattern("excel_cta", text)

def has_loader(text: str) -> bool:
    """Check if text contains loader indicators"""
    return match_pattern("loader", text)

def has_policy_error(text: str) -> bool:
    """Check if text contains policy/error messages"""
    return match_pattern("policy_err", text)

def has_password_prompt(text: str) -> bool:
    """Check if text contains password prompt"""
    return match_pattern("password_prompt", text)

def is_double_protected(text: str) -> bool:
    """Check if text indicates double protection"""
    return match_pattern("double_protected", text)

def is_xl_file(text: str) -> bool:
    """Check if text indicates XL file size"""
    return match_pattern("file_size_xl", text)

# Frame analysis helpers
def analyze_frame_patterns(frame_data: dict) -> dict:
    """Analyze a frame for all relevant patterns"""
    ocr_text = frame_data.get("ocr_text", "")
    
    return {
        "has_desktop_cta": has_desktop_cta(ocr_text),
        "has_excel_cta": has_excel_cta(ocr_text),
        "has_loader": has_loader(ocr_text),
        "has_policy_error": has_policy_error(ocr_text),
        "has_password_prompt": has_password_prompt(ocr_text),
        "is_double_protected": is_double_protected(ocr_text),
        "is_xl_file": is_xl_file(ocr_text),
        "pattern_matches": {
            "desktop_cta": find_pattern_matches("desktop_cta", ocr_text),
            "excel_cta": find_pattern_matches("excel_cta", ocr_text),
            "loader": find_pattern_matches("loader", ocr_text),
            "policy_err": find_pattern_matches("policy_err", ocr_text),
            "password_prompt": find_pattern_matches("password_prompt", ocr_text)
        }
    }

def find_conflict_frames(frames: list) -> list:
    """Find frames that show desktop CTA conflicts"""
    conflict_frames = []
    for frame in frames:
        analysis = analyze_frame_patterns(frame)
        if analysis["has_desktop_cta"] and analysis["has_excel_cta"]:
            conflict_frames.append({
                "frame": frame,
                "analysis": analysis
            })
    return conflict_frames

def find_loader_error_overlap(frames: list) -> list:
    """Find frames showing loader + error overlap"""
    overlap_frames = []
    for frame in frames:
        analysis = analyze_frame_patterns(frame)
        if analysis["has_loader"] and (analysis["has_policy_error"] or analysis["has_desktop_cta"]):
            overlap_frames.append({
                "frame": frame,
                "analysis": analysis
            })
    return overlap_frames
