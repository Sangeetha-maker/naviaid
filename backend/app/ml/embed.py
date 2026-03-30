"""
NaviAid ML – Embedding stubs for local dev (no sentence-transformers needed).
In production, install sentence-transformers and uncomment the real implementation.
"""
from typing import Optional
import math


def encode_text(text: str) -> list[float]:
    """Stub: returns a zero vector. Replace with real embeddings in production."""
    return [0.0] * 384


def encode_texts(texts: list[str]) -> list[list[float]]:
    return [encode_text(t) for t in texts]


def build_profile_text(profile_data: dict) -> str:
    parts = []
    if profile_data.get("age"):
        parts.append(f"Age {profile_data['age']} years old")
    if profile_data.get("gender"):
        parts.append(f"Gender: {profile_data['gender']}")
    if profile_data.get("district"):
        parts.append(f"From {profile_data['district']}, Tamil Nadu")
    if profile_data.get("education_level") or profile_data.get("education"):
        edu = profile_data.get("education_level") or profile_data.get("education")
        parts.append(f"Education: {edu}")
    if profile_data.get("annual_income"):
        parts.append(f"Annual income: Rs {profile_data['annual_income']}")
    if profile_data.get("caste_category") or profile_data.get("caste"):
        caste = profile_data.get("caste_category") or profile_data.get("caste")
        parts.append(f"Category: {caste}")
    if profile_data.get("interests") or profile_data.get("interested_categories"):
        interests = profile_data.get("interests") or profile_data.get("interested_categories") or []
        parts.append(f"Interests: {', '.join(interests)}")
    return ". ".join(parts) or "Tamil Nadu resident seeking government schemes and support"


def build_opportunity_text(opp_data: dict) -> str:
    parts = [opp_data.get("title", ""), opp_data.get("description", "")]
    if opp_data.get("category"):
        parts.append(f"Category: {opp_data['category']}")
    if opp_data.get("benefits"):
        parts.append(f"Benefits: {opp_data['benefits']}")
    return ". ".join(filter(None, parts))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
