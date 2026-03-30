"""
NaviAid ML – Rules Engine + Geo scoring + Composite ranker.
Final score = 0.4*rules + 0.3*semantic + 0.2*geo + 0.1*trust
"""
from math import radians, cos, sin, asin, sqrt
from typing import Any, Optional


# ─────────────────── Rules Engine ────────────────────────────

TN_DISTRICT_COORDS: dict[str, tuple[float, float]] = {
    "Chennai": (13.0827, 80.2707),
    "Coimbatore": (11.0168, 76.9558),
    "Madurai": (9.9252, 78.1198),
    "Tiruchirappalli": (10.7905, 78.7047),
    "Salem": (11.6643, 78.1460),
    "Tirunelveli": (8.7139, 77.7567),
    "Vellore": (12.9165, 79.1325),
    "Erode": (11.3410, 77.7172),
    "Thoothukudi": (8.7642, 78.1348),
    "Dindigul": (10.3624, 77.9695),
    "Kanchipuram": (12.8185, 79.6947),
    "Thanjavur": (10.7870, 79.1378),
    "Tirupur": (11.1085, 77.3411),
    "Ranipet": (12.9224, 79.3332),
    "Dharmapuri": (12.1280, 78.1577),
    "Krishnagiri": (12.5186, 78.2137),
    "Namakkal": (11.2196, 78.1674),
    "Cuddalore": (11.7480, 79.7714),
    "Nagapattinam": (10.7672, 79.8446),
    "Virudhunagar": (9.5810, 77.9624),
    "Sivaganga": (9.8441, 78.4801),
    "Ramanathapuram": (9.3762, 78.8301),
    "Theni": (10.0104, 77.4777),
    "Pudukkottai": (10.3797, 78.8202),
    "Karur": (10.9601, 78.0766),
    "Ariyalur": (11.1413, 79.0767),
    "Perambalur": (11.2340, 78.8793),
    "Tiruvallur": (13.1435, 79.9093),
    "Kanyakumari": (8.0883, 77.5385),
    "Tenkasi": (8.9596, 77.3152),
    "Chengalpattu": (12.6921, 79.9769),
    "Kallakurichi": (11.7380, 78.9586),
    "Tirupattur": (12.4966, 78.5720),
    "Nilgiris": (11.4916, 76.7337),
    "Mayiladuthurai": (11.1034, 79.6508),
    "Tenkasi": (8.9596, 77.3152),
    "Villupuram": (11.9392, 79.4924),
}


def evaluate_rules(user_profile: dict, eligibility: dict) -> tuple[float, dict[str, bool], list[str]]:
    """
    Evaluate eligibility rules against user profile.
    Returns (score 0-1, dict of criteria results, list of match reasons).
    """
    if not eligibility:
        return 1.0, {}, ["Open to all"]

    checks: dict[str, bool] = {}
    reasons: list[str] = []
    total = 0
    matched = 0

    def check(key: str, result: bool, reason_true: str, reason_false: str = ""):
        nonlocal total, matched
        total += 1
        checks[key] = result
        if result:
            matched += 1
            reasons.append(reason_true)

    # Age check
    min_age = eligibility.get("min_age")
    max_age = eligibility.get("max_age")
    user_age = user_profile.get("age")
    if min_age is not None and user_age is not None:
        check("min_age", user_age >= min_age, f"Age ≥ {min_age} ✓")
    if max_age is not None and user_age is not None:
        check("max_age", user_age <= max_age, f"Age ≤ {max_age} ✓")

    # Income check
    max_income = eligibility.get("max_income")
    user_income = user_profile.get("annual_income")
    if max_income is not None and user_income is not None:
        check("income", user_income <= max_income, f"Income ≤ ₹{max_income:,} ✓")

    # Gender check
    allowed_gender = eligibility.get("gender")
    user_gender = user_profile.get("gender")
    if allowed_gender and user_gender:
        check("gender", user_gender in allowed_gender, f"Gender ({user_gender}) eligible ✓")

    # Caste category check
    caste_cats = eligibility.get("caste_categories")
    user_caste = user_profile.get("caste_category")
    if caste_cats and user_caste:
        check("caste", user_caste in caste_cats, f"Category ({user_caste}) eligible ✓")

    # Education check
    allowed_edu = eligibility.get("education_levels")
    user_edu = user_profile.get("education_level")
    if allowed_edu and user_edu:
        check("education", user_edu in allowed_edu, f"Education ({user_edu}) qualifies ✓")

    # State/District check
    allowed_locs = eligibility.get("locations")
    user_district = user_profile.get("district")
    if allowed_locs:
        is_pan = eligibility.get("is_pan_india", False)
        if is_pan or user_district in allowed_locs or "Tamil Nadu" in allowed_locs:
            check("location", True, f"{user_district or 'Tamil Nadu'} is eligible ✓")
        else:
            check("location", False, "")

    # Disability check
    requires_disability = eligibility.get("is_differently_abled")
    if requires_disability is True:
        user_disabled = user_profile.get("is_differently_abled", False)
        check("disability", user_disabled, "Person with disability eligible ✓")

    # Minimum education
    min_edu_map = {
        "none": 0, "primary": 1, "secondary": 2,
        "higher_secondary": 3, "ug": 4, "pg": 5, "phd": 6,
    }
    min_edu = eligibility.get("min_education")
    if min_edu and user_edu:
        check("min_edu", min_edu_map.get(user_edu, 0) >= min_edu_map.get(min_edu, 0),
              f"Education level meets requirement ✓")

    score = (matched / total) if total > 0 else 1.0
    return score, checks, reasons


# ─────────────────── Geo Scoring ─────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def geo_score(user_profile: dict, opp: dict) -> float:
    """Score 0-1 based on proximity. Always 1.0 for pan-India schemes."""
    if opp.get("is_pan_india"):
        return 1.0
    opp_locations = opp.get("locations", [])
    if not opp_locations:
        return 0.5  # unknown location
    user_district = user_profile.get("district")
    if not user_district:
        return 0.5
    # Exact district match
    if user_district in opp_locations:
        return 1.0
    # Haversine-based partial score
    user_coords = TN_DISTRICT_COORDS.get(user_district)
    if not user_coords:
        return 0.3
    best_score = 0.0
    for loc in opp_locations:
        loc_coords = TN_DISTRICT_COORDS.get(loc)
        if loc_coords:
            dist = haversine_km(user_coords[0], user_coords[1], loc_coords[0], loc_coords[1])
            # 0 km -> 1.0, 500 km -> 0.0 (linear decay)
            s = max(0.0, 1.0 - dist / 500.0)
            best_score = max(best_score, s)
    return best_score


# ─────────────────── Composite Ranker ────────────────────────

def composite_score(
    rules: float,
    semantic: float,
    geo: float,
    trust: float,
) -> float:
    """
    Final ranking score.
    weights: rules=0.4, semantic=0.3, geo=0.2, trust=0.1
    """
    return round(0.4 * rules + 0.3 * semantic + 0.2 * geo + 0.1 * trust, 4)
