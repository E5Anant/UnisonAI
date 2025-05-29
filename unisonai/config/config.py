import os
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    _instance = None
    _config_file = Path.home() / '.unisonai' / 'config.json'
    _config: Dict[str, Any] = {
        'api_keys': {
            'gemini': None,
            'openai': None,
            'anthropic': None,
            'cohere': None,
            'groq': None,
            'mixtral': None
        }
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from file if it exists."""
        if self._config_file.exists():
            try:
                with open(self._config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self._config['api_keys'].update(
                        loaded_config.get('api_keys', {}))
            except Exception as e:
                print(f"Error loading config: {e}")

    def _save_config(self):
        """Save configuration to file."""
        try:
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a specific provider."""
        if provider in self._config['api_keys']:
            self._config['api_keys'][provider] = api_key
            self._save_config()
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider."""
        return self._config['api_keys'].get(provider)

    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys."""
        return self._config['api_keys'].copy()


# Create a global config instance
config = Config()
