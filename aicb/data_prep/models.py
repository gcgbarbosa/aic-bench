"""Pydantic models for AICB data structures."""

from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    timestamp: datetime = Field(..., description="Timestamp of the message", alias="datetime")
    role: str = Field(..., description="Role of the message sender (user, operator, etc.)")
    content: str = Field(..., description="Content of the message")


class Metadata(BaseModel):
    """Metadata associated with a conversation."""

    timestamp: datetime = Field(..., description="Timestamp when the conversation was created")
    source: str = Field(..., description="Source of the conversation data")


class Conversation(BaseModel):
    """A conversation dataset entry."""

    id: str = Field(..., description="Unique identifier for the conversation")
    topic: str = Field(..., description="Topic or category of the conversation")
    messages: list[Message] = Field(..., description="List of messages in the conversation")
    raw: str = Field(..., description="Raw data associated with the conversation")
    metadata: Metadata = Field(..., description="Metadata about the conversation")


class CandidateAnswers(BaseModel):
    """Candidate answers from different models for a conversation."""

    id: str = Field(..., description="Conversation ID that matches the input dataset")
    candidates: dict[str, str] = Field(..., description="Model name to response mapping")

    class Config:
        """Pydantic configuration."""

        extra = "allow"  # Allow additional model candidates beyond the documented ones
