"""
Configuration loader for Reddit Lead Generation System
Handles YAML parsing and environment variable substitution
"""

import os
import yaml
import re
from typing import Dict, Any
from pathlib import Path

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Process environment variable substitutions
        self._substitute_env_vars(config)
        
        return config
        
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in config"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = self._substitute_env_vars(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = self._substitute_env_vars(item)
        elif isinstance(obj, str):
            # Replace ${VAR_NAME} with environment variable
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, obj)
            for var_name in matches:
                env_value = os.getenv(var_name)
                if env_value is None:
                    # Try loading from existing config.py
                    try:
                        from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
                        if var_name == 'REDDIT_CLIENT_ID':
                            env_value = REDDIT_CLIENT_ID
                        elif var_name == 'REDDIT_CLIENT_SECRET':
                            env_value = REDDIT_CLIENT_SECRET
                        elif var_name == 'REDDIT_USER_AGENT':
                            env_value = REDDIT_USER_AGENT
                    except ImportError:
                        pass
                
                if env_value is not None:
                    obj = obj.replace(f'${{{var_name}}}', env_value)
                else:
                    print(f"Warning: Environment variable {var_name} not found")
                    
        return obj
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation
        
        Example:
            config.get('reddit.api_rate_limit')  # Returns 1.2
            config.get('reddit.subreddits')      # Returns list of subreddits
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
        
    def get_reddit_config(self) -> Dict[str, Any]:
        """Get Reddit-specific configuration"""
        return self.get('reddit', {})
        
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration"""
        return self.get('analysis', {})
        
    def get_scheduler_config(self) -> Dict[str, Any]:
        """Get scheduler configuration"""
        return self.get('scheduler', {})
        
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.get('database', {})
        
    def get_creator_keywords(self) -> Dict[str, int]:
        """Get creator keywords as a dictionary with weights"""
        keywords_config = self.get('analysis.creator_keywords', [])
        return {item['keyword']: item['weight'] for item in keywords_config}
        
    def get_lead_scoring_weights(self) -> Dict[str, float]:
        """Get lead scoring weights"""
        return self.get('analysis.lead_scoring', {})
        
    def reload(self):
        """Reload configuration from file"""
        self._config = self._load_config()
        
    @property
    def reddit_client_id(self) -> str:
        return self.get('reddit.client_id', '')
        
    @property
    def reddit_client_secret(self) -> str:
        return self.get('reddit.client_secret', '')
        
    @property
    def reddit_user_agent(self) -> str:
        return self.get('reddit.user_agent', 'RedditLeadGen/1.0')
        
    @property
    def subreddits(self) -> list:
        return self.get('reddit.subreddits', ['patreon'])
        
    @property
    def database_path(self) -> str:
        return self.get('database.path', 'reddit_leads.db')
        
    def __repr__(self):
        return f"Config(path='{self.config_path}')"

# Global config instance
config = Config()

if __name__ == "__main__":
    # Test configuration loading
    print("Testing configuration loader...")
    print(f"Subreddits: {config.subreddits}")
    print(f"API Rate Limit: {config.get('reddit.api_rate_limit')}")
    print(f"Creator Keywords: {config.get_creator_keywords()}")
    print(f"Database Path: {config.database_path}")