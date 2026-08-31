"""
AERON Decision Engine — Backend Member 1 (B1) core deliverable.

This is a TRANSPARENT, RULE-BASED scorer on purpose (Section 14/44 of
the master spec): every hospital gets a 0-100 suitability score built
from five weighted, independently-inspectable factors, plus a
human-readable checklist explaining *why*. There is no black-box ML
here for Round 1 — that is explicitly future scope.

    Clinical capability   30%
    Capacity               25%
    ETA                    20%
    Doctor availability    15%
    Resource availability  10%

A hospital is HARD-REJECTED (excluded from the ranked list, shown
separately with a reason) only when it structurally cannot take the
case: it doesn't offer the required specialty at all, or it is
currently diverting/full. Everything else — an empty ICU, an
off-shift specialist, a blood shortfall — is a SOFT penalty: the
hospital stays on the ranked list but drops in score and is flagged,
which is what lets the "change ICU to 0 and re-analyze" demo beat work.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from .config import settings
from .constants import SEVERITY_TRAUMA_REQUIREMENT
from .utils import haversine_km, eta_minutes


@dataclass
class ScoredHospital:
    hospital_id: str
    name: str
    lat: float
    lng: float
    total_score: float
    distance_km: float
    eta_min: float
    breakdown: dict[str, float]           # per-factor 0-100 scores
    checklist: list[dict]                 # [{"label": "...", "ok": True/False, "detail": "..."}]
    status: str
    phone: str

    def to_dict(self) -> dict:
        return {
            "hospital_id": self.hospital_id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "score": round(self.total_score),
            "distance_km": round(self.distance_km, 1),
            "eta_min": self.eta_min,
            "breakdown": {k: round(v, 1) for k, v in self.breakdown.items()},
            "checklist": self.checklist,
            "status": self.status,
            "phone": self.phone,
        }


@dataclass
class RejectedHospital:
    hospital_id: str
    name: str
    reason: str

    def to_dict(self) -> dict:
        return {"hospital_id": self.hospital_id, "name": self.name, "reason": self.reason}


def _clinical_capability_score(hospital: dict, severity: str) -> tuple[float, bool]:
    """Trauma-level fit for the case severity. Returns (score, meets_requirement)."""
    required_level = SEVERITY_TRAUMA_REQUIREMENT[severity]
    actual_level = hospital["trauma_level"]
    diff = actual_level - required_level  # 0 or negative = meets/exceeds requirement
    if diff <= 0:
        return 100.0, True
    # one level short = -35, two levels short = -70, floor at 0
    return max(0.0, 100.0 - diff * 35.0), False


def _capacity_score(hospital: dict, requires_icu: bool) -> tuple[float, bool]:
    """Bed availability + current ED load. Returns (score, capacity_ok)."""
    if requires_icu:
        available, total = hospital["icu_beds_available"], hospital["icu_beds_total"]
    else:
        available, total = hospital["general_beds_available"], hospital["general_beds_total"]

    capacity_ok = available > 0
    if not capacity_ok:
        bed_score = 5.0  # heavy penalty, kept > 0 so a hospital can still be shown down-ranked
    else:
        ratio = available / max(1, total)
        bed_score = min(100.0, ratio * 140.0)  # ~70% free -> full marks

    load_score = 100.0 - hospital.get("emergency_load_pct", 50)
    score = 0.65 * bed_score + 0.35 * load_score
    return score, capacity_ok


def _eta_score(distance_km: float) -> tuple[float, float]:
    """Straight-line ETA heuristic. Returns (score, eta_minutes)."""
    eta = eta_minutes(distance_km)
    score = max(0.0, 100.0 - eta * 2.2)
    return score, eta


def _doctor_score(hospital: dict, required_specialty: str | None) -> tuple[float, bool]:
    on_call = hospital.get("specialist_on_call", {})
    if required_specialty:
        available = bool(on_call.get(required_specialty, False))
        return (100.0 if available else 25.0), available
    values = list(on_call.values())
    if not values:
        return 60.0, True
    ratio = sum(1 for v in values if v) / len(values)
    return ratio * 100.0, ratio >= 0.3


def _resource_score(hospital: dict, blood_group: str | None, blood_units: int | None) -> tuple[float, bool]:
    parts: list[float] = []
    blood_ok = True
    if blood_group and blood_units:
        available = hospital.get("blood_inventory", {}).get(blood_group, 0)
        if available >= blood_units:
            parts.append(100.0)
        else:
            blood_ok = False
            parts.append(max(0.0, (available / max(1, blood_units)) * 100.0))
    vent = hospital.get("resources", {}).get("ventilators_available", 0)
    parts.append(100.0 if vent > 0 else 40.0)
    return (sum(parts) / len(parts) if parts else 100.0), blood_ok


def score_hospital(
    hospital: dict,
    *,
    severity: str,
    origin_lat: float,
    origin_lng: float,
    required_specialty: str | None,
    requires_icu: bool,
    blood_group: str | None,
    blood_units: int | None,
) -> ScoredHospital | RejectedHospital:
    """Score one hospital, or hard-reject it with a stated reason."""

    if hospital.get("status") in ("diverting", "full"):
        return RejectedHospital(
            hospital["hospital_id"], hospital["name"],
            f"Hospital is currently marked '{hospital['status']}' and not accepting new emergencies.",
        )

    if required_specialty and required_specialty not in hospital.get("specialties", []):
        return RejectedHospital(
            hospital["hospital_id"], hospital["name"],
            f"Does not offer {required_specialty.replace('_', ' ')} at this facility.",
        )

    clinical, trauma_ok = _clinical_capability_score(hospital, severity)
    capacity, capacity_ok = _capacity_score(hospital, requires_icu)
    distance_km = haversine_km(origin_lat, origin_lng, hospital["lat"], hospital["lng"])
    eta_sc, eta_min = _eta_score(distance_km)
    doctor, doctor_ok = _doctor_score(hospital, required_specialty)
    resource, blood_ok = _resource_score(hospital, blood_group, blood_units)

    total = (
        clinical * settings.WEIGHT_CLINICAL_CAPABILITY
        + capacity * settings.WEIGHT_CAPACITY
        + eta_sc * settings.WEIGHT_ETA
        + doctor * settings.WEIGHT_DOCTOR_AVAILABILITY
        + resource * settings.WEIGHT_RESOURCE_AVAILABILITY
    )

    checklist = [
        {"label": "Trauma capability", "ok": trauma_ok,
         "detail": f"Level {hospital['trauma_level']} trauma centre"},
    ]
    if requires_icu:
        checklist.append({"label": "ICU bed available", "ok": capacity_ok,
                           "detail": f"{hospital['icu_beds_available']}/{hospital['icu_beds_total']} ICU beds free"})
    else:
        checklist.append({"label": "General bed available", "ok": capacity_ok,
                           "detail": f"{hospital['general_beds_available']}/{hospital['general_beds_total']} beds free"})
    if required_specialty:
        checklist.append({"label": required_specialty.replace("_", " ").title() + " on call", "ok": doctor_ok,
                           "detail": "On shift now" if doctor_ok else "Not currently on shift"})
    if blood_group and blood_units:
        have = hospital.get("blood_inventory", {}).get(blood_group, 0)
        checklist.append({"label": f"{blood_group} blood ({blood_units} units needed)", "ok": blood_ok,
                           "detail": f"{have} units in stock"})
    checklist.append({"label": "ETA", "ok": eta_min <= 20,
                       "detail": f"{eta_min} min ({round(distance_km, 1)} km, straight-line estimate)"})

    return ScoredHospital(
        hospital_id=hospital["hospital_id"],
        name=hospital["name"],
        lat=hospital["lat"],
        lng=hospital["lng"],
        total_score=total,
        distance_km=distance_km,
        eta_min=eta_min,
        breakdown={
            "clinical_capability": clinical,
            "capacity": capacity,
            "eta": eta_sc,
            "doctor_availability": doctor,
            "resource_availability": resource,
        },
        checklist=checklist,
        status=hospital.get("status", "active"),
        phone=hospital.get("phone", ""),
    )


def rank_hospitals(
    hospitals: list[dict],
    *,
    severity: str,
    origin_lat: float,
    origin_lng: float,
    required_specialty: str | None = None,
    requires_icu: bool = False,
    blood_group: str | None = None,
    blood_units: int | None = None,
) -> tuple[list[ScoredHospital], list[RejectedHospital]]:
    """
    Score every hospital and return (ranked_eligible, rejected), both
    sorted — ranked descending by score, rejected in input order.
    This is the single function every route/simulation calls, so the
    live API and the mass-casualty simulator always agree on logic.
    """
    ranked: list[ScoredHospital] = []
    rejected: list[RejectedHospital] = []

    for hospital in hospitals:
        result = score_hospital(
            hospital,
            severity=severity,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            required_specialty=required_specialty,
            requires_icu=requires_icu,
            blood_group=blood_group,
            blood_units=blood_units,
        )
        if isinstance(result, RejectedHospital):
            rejected.append(result)
        else:
            ranked.append(result)

    ranked.sort(key=lambda h: h.total_score, reverse=True)
    return ranked, rejected


def build_recommendation_summary(ranked: list[ScoredHospital]) -> str:
    """One-sentence, judge-facing explanation of the top pick — never a black box."""
    if not ranked:
        return "No suitable hospital was found for the stated requirements."
    top = ranked[0]
    passed = [c["label"] for c in top.checklist if c["ok"]]
    failed = [c["label"] for c in top.checklist if not c["ok"]]
    text = f"{top.name} ranked highest ({round(top.total_score)}%): meets {', '.join(passed)}."
    if failed:
        text += f" Watch: {', '.join(failed)}."
    return text
