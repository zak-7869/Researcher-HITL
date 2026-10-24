from typing import Literal
from pydantic import BaseModel, Field, field_validator

class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    max_iterations: int = Field(default=2, ge=1, le=3)

    @field_validator("topic")
    @classmethod
    def clean_topic(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("topic must not be blank")
        return value

class ReviewRequest(BaseModel):
    decision: Literal["approve", "request_changes"]
    comment: str = Field(default="", max_length=2000)
