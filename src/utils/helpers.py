import json
import hashlib
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    hash_obj = hashlib.md5(timestamp.encode())
    return f"{prefix}_{hash_obj.hexdigest()[:8]}"

def save_json(data: Any, filepath: Path, indent: int = 2) -> bool:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def load_json(filepath: Path) -> Any:
    """Load data from JSON file"""
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def format_survey_for_api(survey: Dict) -> Dict:
    """Format survey for Formbricks API"""
    return {
        "name": survey.get("name", "Unnamed Survey"),
        "type": "link",
        "questions": survey.get("questions", []),
        "welcomeCard": survey.get("welcomeCard", {}),
        "thankYouCard": survey.get("thankYouCard", {}),
        "status": "inProgress",
        "language": "en",
        "created_at": datetime.utcnow().isoformat()
    }