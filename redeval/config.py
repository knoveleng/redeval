"""
Configuration management for RedEval.
Handles environment variables, credentials, and global settings.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class EnvironmentConfig:
    """Environment configuration for RedEval."""
    
    # API Keys
    openai_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    
    # Paths
    project_root: Path = field(default_factory=lambda: Path.cwd())
    log_dir: Path = field(default_factory=lambda: Path.cwd() / "logs")
    recipes_dir: Path = field(default_factory=lambda: Path.cwd() / "recipes")
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        
        # Override paths if environment variables are set
        if project_root := os.getenv("REDEVAL_PROJECT_ROOT"):
            self.project_root = Path(project_root)
            
        if log_dir := os.getenv("REDEVAL_LOG_DIR"):
            self.log_dir = Path(log_dir)
        else:
            self.log_dir = self.project_root / "logs"
            
        if recipes_dir := os.getenv("REDEVAL_RECIPES_DIR"):
            self.recipes_dir = Path(recipes_dir)
        else:
            self.recipes_dir = self.project_root / "recipes"
            
        self.log_level = os.getenv("REDEVAL_LOG_LEVEL", "INFO")
        
        # Create directories if they don't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        missing = []
        
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
            
        if not self.huggingface_token:
            missing.append("HUGGINGFACE_TOKEN")
            
        if missing:
            logging.warning(f"Missing environment variables: {', '.join(missing)}")
            return False
            
        return True
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.log_dir / "redeval.log")
            ]
        )


# Global configuration instance
env_config = EnvironmentConfig()
