import json
import os
from datetime import datetime

SETTINGS_FILE = "countdown_settings.json"

DEFAULT_SETTINGS = {
    "is_active": True,
    "launch_date": "2025-01-15T00:00:00",
    "launch_message": "🚀 Website Will Be Live Soon!",
    "subtitle": "Get ready for an amazing experience! Our coaching platform is launching soon with incredible features and opportunities.",
    "show_gate_button": True,
    "gate_button_text": "🚪 Open Website",
    "background_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "logo_text": "COACHING",
    "logo_emoji": "🎓"
}

def load_settings():
    """Load countdown settings from JSON file."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save countdown settings to JSON file."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def update_setting(key, value):
    """Update a specific setting."""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)

def get_launch_status():
    """Check if website is live based on launch date."""
    settings = load_settings()
    if not settings.get("is_active", True):
        return False
    
    try:
        launch_date = datetime.fromisoformat(settings["launch_date"])
        return datetime.now() >= launch_date
    except:
        return False

def toggle_countdown():
    """Toggle countdown page on/off."""
    settings = load_settings()
    settings["is_active"] = not settings.get("is_active", True)
    return save_settings(settings)