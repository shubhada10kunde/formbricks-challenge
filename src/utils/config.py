import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    SRC_DIR = BASE_DIR / "src"
    
    # Formbricks
    FORMBRICKS_URL = os.getenv("FORMBRICKS_URL", "http://localhost:3000")
    FORMBRICKS_API_KEY = os.getenv("FORMBRICKS_API_KEY", "")
    
    # Ollama
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # Application
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> list:
        """Validate configuration"""
        errors = []
        
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code != 200:
                errors.append(f"Cannot connect to Ollama at {cls.OLLAMA_URL}")
        except:
            errors.append(f"Ollama not running at {cls.OLLAMA_URL}")
        
        if not cls.FORMBRICKS_API_KEY:
            errors.append("FORMBRICKS_API_KEY not set (will be needed for seeding)")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print configuration"""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        config_items = {
            "FORMBRICKS_URL": cls.FORMBRICKS_URL,
            "FORMBRICKS_API_KEY": "***" + (cls.FORMBRICKS_API_KEY[-4:] if cls.FORMBRICKS_API_KEY else ""),
            "OLLAMA_URL": cls.OLLAMA_URL,
            "OLLAMA_MODEL": cls.OLLAMA_MODEL,
            "LOG_LEVEL": cls.LOG_LEVEL,
            "MAX_RETRIES": cls.MAX_RETRIES,
            "REQUEST_TIMEOUT": cls.REQUEST_TIMEOUT
        }
        
        for key, value in config_items.items():
            table.add_row(key, str(value))
        
        console.print(table)