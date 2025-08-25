import json
from pathlib import Path
import logging

def load_figma_tokens_safe(minified_path: str = "context/tokens_fluent2_min.json", char_limit: int = 2000) -> str:
    """Safely load Figma tokens with fallback"""
    try:
        p = Path(minified_path)
        if not p.exists():
            logging.warning(f"Figma tokens file not found: {minified_path}")
            return "{}"
        
        data = json.loads(p.read_text(encoding="utf-8"))
        # keep only keys we care about
        keep = {
            "colors": data.get("colors", {}),
            "typography": data.get("typography", {}),
            "spacing": data.get("spacing", []),
            "radius": data.get("radius", {}),
            "shadows": data.get("shadows", {})
        }
        s = json.dumps(keep, separators=(",", ":"))
        return s[:char_limit]  # hard cap
    except Exception as e:
        logging.warning(f"Failed to load Figma tokens: {e}")
        return "{}"

def load_ado_examples_safe(path: str = "context/ado_examples_min.json", max_examples: int = 8, char_limit: int = 1200) -> str:
    """Safely load ADO examples with fallback"""
    try:
        p = Path(path)
        if not p.exists():
            logging.warning(f"ADO examples file not found: {path}")
            return "{}"
        
        examples = json.loads(p.read_text(encoding="utf-8"))
        # take a balanced subset across categories
        bucketed = []
        for cat in ["color_contrast","spacing_alignment","typography","border_radius","dialog_layout","ribbon_consistency"]:
            bucketed.extend(examples.get(cat, [])[:2])  # up to 2 per category
        subset = bucketed[:max_examples]
        s = json.dumps(subset, separators=(",", ":"))
        return s[:char_limit]
    except Exception as e:
        logging.warning(f"Failed to load ADO examples: {e}")
        return "{}"
