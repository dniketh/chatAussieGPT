from accelerate.commands.config.update import description
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class UserProfileInput(BaseModel):
    user_id: str


# Pydantic model for User Profile output
class UserSkillProfile(BaseModel):
    skills: List[str] = Field(description = "Skills")
    resume_skills: List[str] = Field(description = " Skills from Resume")
    competencies: Dict[str, Any] = Field(description = "Core Competency Ratings given by the User")