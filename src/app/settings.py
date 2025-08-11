"""Application settings and configuration management."""

import os
from typing import Optional
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key for LLM access")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Logging format")
    
    # Reproducibility
    random_seed: int = Field(default=42, description="Random seed for reproducibility")
    
    # Output Configuration
    output_dir: str = Field(default="out", description="Output directory path")
    
    # CrewAI Configuration
    crew_verbose: bool = Field(default=False, description="Enable CrewAI verbose mode")
    crew_memory: bool = Field(default=False, description="Enable CrewAI memory")
    
    # Generation Configuration
    max_retries: int = Field(default=3, description="Maximum retries for failed operations")
    request_timeout: int = Field(default=120, description="Request timeout in seconds")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_output_path(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.output_dir)

    def ensure_output_dir(self) -> Path:
        """Ensure output directory exists and return Path."""
        output_path = self.get_output_path()
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


class ConfigModel(BaseModel):
    """Configuration model for YAML config files."""
    
    industry: str
    company: dict
    time_window: dict
    org: dict
    project: dict
    volumes: dict
    mail: dict
    privacy: dict
    outputs: list[str]

    def validate_config(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate required fields
        required_company_fields = ["name", "mission", "tone", "values"]
        for field in required_company_fields:
            if field not in self.company:
                errors.append(f"Missing required company field: {field}")
        
        required_time_fields = ["start", "end", "timezone"]
        for field in required_time_fields:
            if field not in self.time_window:
                errors.append(f"Missing required time_window field: {field}")
        
        required_org_fields = ["team_name", "geo", "levels", "manager_span"]
        for field in required_org_fields:
            if field not in self.org:
                errors.append(f"Missing required org field: {field}")
        
        required_project_fields = ["key", "name", "sprint_length_days"]
        for field in required_project_fields:
            if field not in self.project:
                errors.append(f"Missing required project field: {field}")
        
        # Validate volumes
        volume_fields = ["jira_tickets_in_window", "emails_per_person_per_week"]
        for field in volume_fields:
            if field not in self.volumes:
                errors.append(f"Missing required volumes field: {field}")
            elif not isinstance(self.volumes[field], dict):
                errors.append(f"volumes.{field} must be a dict with min/max")
            elif "min" not in self.volumes[field] or "max" not in self.volumes[field]:
                errors.append(f"volumes.{field} must have min and max values")
        
        # Validate mail categories
        if "categories" not in self.mail:
            errors.append("Missing required mail.categories")
        
        # Validate outputs
        valid_outputs = ["jira", "email"]
        for output in self.outputs:
            if output not in valid_outputs:
                errors.append(f"Invalid output type: {output}. Must be one of {valid_outputs}")
        
        return errors


def load_settings() -> Settings:
    """Load application settings from environment."""
    return Settings()


def load_config(config_path: str) -> ConfigModel:
    """Load configuration from YAML file."""
    import yaml
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    return ConfigModel(**config_data)
