from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class QuestionType(str, Enum):
    RATING = "rating"
    MULTIPLE_CHOICE = "multipleChoice"
    OPEN_TEXT = "openText"
    DROPDOWN = "dropdown"
    MATRIX = "matrix"

class Question(BaseModel):
    type: QuestionType
    headline: str
    required: bool = True
    choices: Optional[List[str]] = None
    range: Optional[int] = Field(default=5, ge=1, le=10)
    scale: Optional[str] = "number"
    id: Optional[str] = None

class WelcomeCard(BaseModel):
    enabled: bool = True
    headline: str = "Welcome!"
    html: str = "<p>Thank you for participating in our survey.</p>"

class ThankYouCard(BaseModel):
    enabled: bool = True
    headline: str = "Thank You!"
    html: str = "<p>Your response has been recorded.</p>"

class Survey(BaseModel):
    name: str
    questions: List[Question]
    welcomeCard: WelcomeCard = WelcomeCard()
    thankYouCard: ThankYouCard = ThankYouCard()
    type: str = "link"
    status: str = "inProgress"
    language: str = "en"
    
    class Config:
        use_enum_values = True