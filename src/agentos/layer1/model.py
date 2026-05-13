from datetime import datetime, UTC
from typing import Literal
from pydantic import BaseModel, Field
import uuid


def _id() -> str:
    return str(uuid.uuid4())[:8]


class Goal(BaseModel):
    id: str = Field(default_factory=_id)
    title: str
    description: str | None = None
    status: Literal["active", "completed", "abandoned"] = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Decision(BaseModel):
    id: str = Field(default_factory=_id)
    title: str
    rationale: str
    alternatives: list[str] = []
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OpenQuestion(BaseModel):
    id: str = Field(default_factory=_id)
    question: str
    options: list[str] = []


class Project(BaseModel):
    id: str
    name: str
    description: str
    status: Literal["active", "paused", "archived"] = "active"
    active_goal_id: str | None = None
    current_focus: str | None = None
    goals: list[Goal] = []
    decisions: list[Decision] = []
    open_questions: list[OpenQuestion] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
