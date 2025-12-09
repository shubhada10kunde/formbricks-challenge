from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"
    MANAGER = "manager"

class User(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.VIEWER
    organization: str = Field(default="Acme Inc.")
    
    class Config:
        use_enum_values = True