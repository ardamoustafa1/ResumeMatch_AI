from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AnalysisRequest(BaseModel):
    """
    Request payload to initiate a new CV + JD analysis.
    """

    cv_text: str = Field(..., description="The full text of the candidate's CV")
    jd_text: str = Field(..., description="The full text of the Job Description")
    company: Optional[str] = Field(None, description="The name of the hiring company")
    recruiter_name: Optional[str] = Field(None, description="The name of the recruiter")

    @field_validator("cv_text")
    @classmethod
    def validate_cv_length(cls, v: str) -> str:
        if len(v.strip()) < 100:
            raise ValueError("CV text must be at least 100 characters long")
        if len(v.strip()) > 100000:
            raise ValueError("CV text must be at most 100,000 characters long")
        return v

    @field_validator("jd_text")
    @classmethod
    def validate_jd_length(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Job Description text must be at least 50 characters long")
        if len(v.strip()) > 50000:
            raise ValueError(
                "Job Description text must be at most 50,000 characters long"
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cv_text": "Experienced Python developer with 5 years in FastAPI, PostgreSQL, and AWS...",
                "jd_text": "Looking for a Senior Backend Engineer proficient in Python, AsyncIO, and Redis...",
                "company": "TechCorp",
                "recruiter_name": "Alice Smith",
            }
        }
    )


class AnalysisResponse(BaseModel):
    """
    Response model for an analysis record.
    """

    id: str
    user_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174999",
                "status": "completed",
                "result": {"match_score": 85, "strengths": ["Python"]},
                "created_at": "2026-04-27T21:00:00Z",
            }
        },
    )


class MessageOutput(BaseModel):
    """
    Model representing an outreach message.
    """

    id: str
    analysis_id: str
    generated_message: str
    model_used: str
    is_edited: bool
    final_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174111",
                "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
                "generated_message": "Hi there! I saw your profile and...",
                "model_used": "gpt-4o-mini",
                "is_edited": False,
                "final_message": None,
                "created_at": "2026-04-27T21:05:00Z",
            }
        },
    )


class MatchResult(BaseModel):
    """
    Result of the CV to Job Description matching analysis.
    """

    score: int = Field(..., ge=0, le=100, description="Match score from 0 to 100")
    matched_skills: List[str] = Field(
        ..., description="List of skills present in both CV and JD"
    )
    missing_skills: List[str] = Field(
        ..., description="List of skills required by JD but missing in CV"
    )
    improvement_suggestions: List[str] = Field(
        ..., description="Actionable suggestions to improve the CV match"
    )


class OutreachMessages(BaseModel):
    """
    Generated outreach messages tailored to the candidate and role.
    """

    dm_first_contact: str = Field(
        ..., description="Warm, specific first contact message (3-4 sentences)"
    )
    dm_follow_up: str = Field(..., description="Brief day 7 follow-up message")
    connection_note: str = Field(
        ...,
        max_length=280,
        description="Short LinkedIn connection note (max 280 chars)",
    )


class ProfileImprovements(BaseModel):
    """
    Suggestions for improving the candidate's LinkedIn profile.
    """

    headline_before: str = Field(
        ..., description="The original headline extracted from CV"
    )
    headline_after: str = Field(
        ..., max_length=120, description="Keyword-optimized headline (max 120 chars)"
    )
    about_section: str = Field(
        ...,
        description="4-5 sentences, achievement-focused, first person about section",
    )


class FullAnalysisResult(BaseModel):
    """
    Aggregated result of the full AI analysis pipeline.
    """

    match_result: Optional[MatchResult] = None
    outreach_messages: Optional[OutreachMessages] = None
    profile_improvements: Optional[ProfileImprovements] = None
    errors: Dict[str, str] = Field(default_factory=dict)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        checks = (
            any(character.islower() for character in value),
            any(character.isupper() for character in value),
            any(character.isdigit() for character in value),
            any(not character.isalnum() for character in value),
        )
        if not all(checks):
            raise ValueError(
                "Password must include uppercase, lowercase, number and symbol."
            )
        return value


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    email_verified: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return UserCreate.validate_password_strength(value)


class TelegramConfig(BaseModel):
    chat_id: str = Field(min_length=1, max_length=50)
    is_active: bool = True


class AnalysisProgressEvent(BaseModel):
    analysis_id: str
    event: str
    step: str
    progress: int | None = Field(default=None, ge=0, le=100)
    message: str
    data: Dict[str, Any] = Field(default_factory=dict)
