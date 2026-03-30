"""
NaviAid Pydantic Schemas (v2) – Request/Response models.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


# ─────────────────────────── Auth ────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class UserOut(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    is_onboarded: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_user_and_profile(cls, user, profile=None):
        return cls(
            id=user.id, email=user.email, name=user.name,
            role=user.role, is_active=user.is_active,
            is_onboarded=profile.onboarding_complete if profile else False,
            created_at=user.created_at,
        )


# ─────────────────────── User Profile ────────────────────────

class ProfileCreate(BaseModel):
    age: Optional[int] = Field(None, ge=5, le=100)
    gender: Optional[str] = None
    district: Optional[str] = None
    state: str = "Tamil Nadu"
    pincode: Optional[str] = None
    education_level: Optional[str] = None
    stream: Optional[str] = None
    institution: Optional[str] = None
    annual_income: Optional[int] = Field(None, ge=0)
    caste_category: Optional[str] = None
    is_differently_abled: bool = False
    skills: list[str] = []
    interests: list[str] = []
    draft_step: int = 0
    onboarding_complete: bool = False


class ProfileUpdate(ProfileCreate):
    pass


class ProfileOut(ProfileCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────── Opportunity ─────────────────────────

class OpportunityBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    title_ta: Optional[str] = None
    description: str
    description_ta: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    eligibility: dict[str, Any] = {}
    documents_required: list[str] = []
    benefits: Optional[str] = None
    amount: Optional[int] = None
    deadline: Optional[str] = None  # ISO date string
    is_recurring: bool = False
    locations: list[str] = []
    is_pan_india: bool = False
    trust_score: float = Field(0.8, ge=0.0, le=1.0)
    is_active: bool = True


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityUpdate(OpportunityBase):
    pass


class OpportunityOut(OpportunityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────── Recommendations ─────────────────────

class RecoItem(BaseModel):
    opportunity: OpportunityOut
    score: float
    rules_score: float
    semantic_score: float
    geo_score: float
    trust_score: float
    reasons: list[str]
    eligibility_status: dict[str, bool]


class RecoResponse(BaseModel):
    total: int
    items: list[RecoItem]


# ─────────────────────── Search ──────────────────────────────

class SearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=500)
    category: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)
    offset: int = Field(0, ge=0)


class SearchResponse(BaseModel):
    total: int
    query: str
    items: list[OpportunityOut]


# ─────────────────────── Application ─────────────────────────

class ApplicationCreate(BaseModel):
    opportunity_id: str
    status: str = "saved"
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: str
    user_id: str
    opportunity_id: str
    status: str
    notes: Optional[str]
    applied_at: Optional[datetime]
    created_at: datetime
    opportunity: OpportunityOut

    model_config = {"from_attributes": True}


# ─────────────────────── Pagination ──────────────────────────

class PaginatedOpportunities(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[OpportunityOut]
