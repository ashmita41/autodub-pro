"""
Configuration management for AutoDub Pro.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

# Default configuration 
DEFAULT_CONFIG = {
    "aws": {
        "access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "region": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    },
    "openai": {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    },
    "elevenlabs": {
        "api_key": os.environ.get("ELEVENLABS_API_KEY", ""),
        "voice_id": os.environ.get("ELEVENLABS_VOICE_ID", ""),
    },
    "google_drive": {
        "enabled": os.environ.get("GOOGLE_DRIVE_ENABLED", "false").lower() == "true",
        "credentials_file": os.environ.get("GOOGLE_DRIVE_CREDENTIALS_FILE", "credentials.json"),
        "folder_id": os.environ.get("GOOGLE_DRIVE_FOLDER_ID", ""),
    },
    "app": {
        "temp_dir": os.environ.get("TEMP_DIR", str(Path.home() / ".autodub_pro" / "temp")),
        "data_dir": os.environ.get("DATA_DIR", str(Path.home() / ".autodub_pro" / "data")),
    }
}

# Config file location
CONFIG_DIR = Path.home() / ".autodub_pro"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config file, falling back to defaults.
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # If config file exists, load it
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                user_config = json.load(f)
                
            # Merge user config with defaults
            config = DEFAULT_CONFIG.copy()
            for section, values in user_config.items():
                if section in config:
                    config[section].update(values)
                else:
                    config[section] = values
                    
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG
    else:
        # Create default config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config file.
    """
    # Ensure config directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")


def get_api_key(service: str) -> Optional[str]:
    """
    Get API key for a specific service.
    """
    config = load_config()
    if service in config and "api_key" in config[service]:
        return config[service]["api_key"]
    return None


def update_api_key(service: str, api_key: str) -> None:
    """
    Update API key for a specific service.
    """
    config = load_config()
    if service in config:
        config[service]["api_key"] = api_key
        save_config(config)
    else:
        raise ValueError(f"Unknown service: {service}") 