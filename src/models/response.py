from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class Response(BaseModel):
    survey_id: str
    answers: Dict[str, Any]
    completed: bool = True
    user_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=lambda: {
        "userAgent": "Formbricks Seeder/1.0",
        "source": "api",
        "timestamp": datetime.utcnow().isoformat()
    })