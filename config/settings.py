import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import json

#Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT/".env"
CONFIG_PATH = PROJECT_ROOT/"config"/"config.json"
CONFIG_EXAMPLE_PATH = PROJECT_ROOT/"config"/"config.example.json"

@dataclass
class Settings:
    '''
    Holds every configurable value the app needs
    Build once at startup and use wherever
    '''

    onboarded : bool = False

    igdb_client_id : str = ""
    igdb_client_secret : str = ""
    steam_api_key : str = ""
    rawg_api_key : str = ""

    active_theme : str = "dark"
    enabled_sources : dict = field(default_factory = dict)

    def save_config(self, updates : dict) -> None:
        '''
        merges updates into the config.json
        '''
        config_data = {}
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                config_data = json.load(f)

        config_data.update(updates)

        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)

    def mark_onboarding_completed(self) -> None:
        '''
        Persists onboarded = True to config.json
        '''
        self.onboarded = True

        self.save_config({"onboarded" : True})

    def set_active_theme(self, theme_name : str) -> None:
        '''
        Sets the app theme
        '''
        self.active_theme = theme_name
        self.save_config({"active_theme" : theme_name})

    def set_source_enabled(self, source_key : str, enabled : bool) -> None:
        '''
        Sets the enabled config of a source
        '''
        self.enabled_sources[source_key] = enabled
        self.save_config({"enabled_sources" : self.enabled_sources})

    @classmethod
    def load(cls) -> "Settings":
        '''
        Reads .env and config.json and returns a populated Settings object
        '''

        #Load .env - nothing if .env DNE
        load_dotenv(ENV_PATH)

        #Read config.json - default to config.example.json is DNE
        config_path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_EXAMPLE_PATH
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        return cls(
            onboarded = config_data.get("onboarded", False),
            igdb_client_id = os.getenv("IGDB_CLIENT_ID", ""),
            igdb_client_secret = os.getenv("IGDB_CLIENT_SECRET", ""),
            steam_api_key = os.getenv("STEAM_API_KEY", ""),
            rawg_api_key = os.getenv("RAWG_API_KEY", ""),
            active_theme = config_data.get("active_theme", "dark"),
            enabled_sources = config_data.get("enabled_sources", {})
            )


