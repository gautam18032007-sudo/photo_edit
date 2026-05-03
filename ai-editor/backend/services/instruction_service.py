"""
Instruction-based editing service.
Parses natural language commands into structured edit operations.
"""
import re
from typing import Optional

# ── Intent patterns ──
PATTERNS = [
    # Video effects
    (r"add blur(?:\s+at\s+(\d+:\d+))?", "video_blur", "timestamp"),
    (r"remove(?:\s+background|\s+bg)", "image_remove_bg", None),
    (r"enhance(?:\s+face)?(?:\s+brightness)?", "image_enhance_face", None),
    (r"remove(?:\s+background)?\s+noise", "audio_noise_reduction", None),
    (r"trim\s+silence", "audio_trim_silence", None),
    (r"increase\s+(?:volume|gain)\s+by\s+([\d.]+)\s*(?:db)?", "audio_volume", "gain_db"),
    (r"decrease\s+(?:volume|gain)\s+by\s+([\d.]+)\s*(?:db)?", "audio_volume_down", "gain_db"),
    (r"apply\s+(?:cinematic\s+)?lut", "image_apply_lut", None),
    (r"stabilize(?:\s+shaky)?(?:\s+footage)?", "video_stabilize", None),
    (r"auto\s+enhance", "image_auto_enhance", None),
    (r"brightness\s+([\d.+-]+)", "image_brightness", "value"),
    (r"contrast\s+([\d.+-]+)", "image_contrast", "value"),
    (r"saturation\s+([\d.+-]+)", "image_saturation", "value"),
    (r"sharpen(?:\s+([\d.]+))?", "image_sharpen", "value"),
    (r"export\s+as\s+(jpeg|png|mp4|wav)", "export", "format"),
    (r"crop\s+(\d+)x(\d+)", "image_crop", "dimensions"),
    (r"rotate\s+(90|180|270)", "image_rotate", "degrees"),
    (r"speed\s+up\s+([\d.]+)x", "video_speed", "factor"),
    (r"slow\s+down\s+([\d.]+)x", "video_slow", "factor"),
    (r"add\s+(?:text|title)\s+\"(.+?)\"", "video_add_text", "text"),
]

def parse_instruction(instruction: str) -> dict:
    """
    Returns:
      { "action": str, "params": dict, "description": str, "supported": bool }
    """
    text = instruction.lower().strip()
    for pattern, action, param_key in PATTERNS:
        m = re.search(pattern, text)
        if m:
            params = {}
            if param_key and m.lastindex:
                groups = [g for g in m.groups() if g is not None]
                if param_key == "dimensions" and len(groups) >= 2:
                    params = {"width": int(groups[0]), "height": int(groups[1])}
                elif groups:
                    val = groups[0]
                    try:
                        val = float(val)
                    except ValueError:
                        pass
                    params[param_key] = val
            return {
                "action": action,
                "params": params,
                "description": _describe(action, params),
                "supported": True,
            }
    return {
        "action": "unknown",
        "params": {},
        "description": f"Could not parse: \"{instruction}\"",
        "supported": False,
    }

def _describe(action: str, params: dict) -> str:
    descriptions = {
        "video_blur": f"Apply Gaussian blur{' at ' + str(params.get('timestamp','')) if params.get('timestamp') else ''}",
        "image_remove_bg": "Remove image background using AI segmentation",
        "image_enhance_face": "Detect and enhance face region with adaptive brightness",
        "audio_noise_reduction": "Apply spectral noise reduction to audio",
        "audio_trim_silence": "Trim leading/trailing silence",
        "audio_volume": f"Increase volume by {params.get('gain_db', 3)} dB",
        "audio_volume_down": f"Decrease volume by {params.get('gain_db', 3)} dB",
        "image_apply_lut": "Apply cinematic color LUT",
        "video_stabilize": "Warp-stabilize shaky video footage",
        "image_auto_enhance": "AI one-click brightness, contrast and sharpness enhancement",
        "image_brightness": f"Set brightness to {params.get('value', 1.0)}",
        "image_contrast": f"Set contrast to {params.get('value', 1.0)}",
        "image_saturation": f"Set saturation to {params.get('value', 1.0)}",
        "image_sharpen": f"Sharpen image (factor: {params.get('value', 1.5)})",
        "export": f"Export as {params.get('format', 'jpeg').upper()}",
        "image_crop": f"Crop to {params.get('width')}×{params.get('height')}",
        "image_rotate": f"Rotate {params.get('degrees', 90)}°",
        "video_speed": f"Speed up {params.get('factor', 2)}×",
        "video_slow": f"Slow down to {params.get('factor', 0.5)}× speed",
        "video_add_text": f"Add text overlay: \"{params.get('text','')}\"",
    }
    return descriptions.get(action, action)
