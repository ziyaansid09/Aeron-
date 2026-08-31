"""
Mass-Casualty allocation — Backend Member 2 (B2) deliverable.

AERON's strongest demo feature (Section 19): instead of sending every
casualty to the nearest hospital and overloading it, casualties are
allocated one at a time — most critical first — each time re-running
the SAME decision engine used for a single emergency, against a
working copy of hospital capacity that is decremented after every
assignment. That's what produces network-level distribution instead
of everyone piling onto the single best-scoring hospital.

Formal OR-Tools optimization is explicitly future scope (Section 20);
this greedy heuristic is what the action plan calls for in Round 1.
"""
from __future__ import annotations
import copy
import random

from .decision_engine import rank_hospitals
from .utils import new_id, now_iso

_SEVERITY_ORDER = {"critical": 0, "serious": 1, "moderate": 2}

# A small, fixed pool of plausible per-casualty requirements so an
# auto-generated batch still produces a mix of specialties/blood needs,
# without pulling in a full randomized-vitals generator.
_AUTO_SPECIALTIES = [None, "orthopedics", "neurosurgery", "general_surgery", "cardiology", "burns"]
_AUTO_BLOOD = [None, "O+", "O-", "A+", "B+"]


def _auto_generate_casualties(critical: int, serious: int, moderate: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    casualties: list[dict] = []
    counts = [("critical", critical), ("serious", serious), ("moderate", moderate)]
    n = 1
    for severity, count in counts:
        for _ in range(count):
            specialty = rng.choice(_AUTO_SPECIALTIES)
            blood_group = rng.choice(_AUTO_BLOOD)
            casualties.append({
                "casualty_id": f"P{n:02d}",
                "severity": severity,
                "required_specialty": specialty,
                # Critical cases are the ones most likely to need an ICU bed.
                "requires_icu": severity == "critical" and rng.random() < 0.7,
                "blood_group": blood_group,
                "blood_units": (rng.choice([1, 2]) if blood_group else None),
            })
            n += 1
    return casualties


def simulate_mass_casualty(
    hospitals: list[dict],
    *,
    lat: float,
    lng: float,
    location_label: str,
    critical_count: int,
    serious_count: int,
    moderate_count: int,
    explicit_casualties: list[dict] | None = None,
) -> dict:
    casualties = explicit_casualties or _auto_generate_casualties(critical_count, serious_count, moderate_count)
    # Order most-severe first so critical patients get first pick of capacity —
    # mirrors real triage priority.
    ordered = sorted(enumerate(casualties), key=lambda pair: _SEVERITY_ORDER.get(pair[1]["severity"], 9))

    working_hospitals = copy.deepcopy(hospitals)
    by_id = {h["hospital_id"]: h for h in working_hospitals}

    allocations: list[dict] = []
    distribution: dict[str, int] = {h["hospital_id"]: 0 for h in working_hospitals}
    unassigned = 0

    for original_index, casualty in ordered:
        ranked, rejected = rank_hospitals(
            working_hospitals,
            severity=casualty["severity"],
            origin_lat=lat,
            origin_lng=lng,
            required_specialty=casualty.get("required_specialty"),
            requires_icu=casualty.get("requires_icu", False),
            blood_group=casualty.get("blood_group"),
            blood_units=casualty.get("blood_units"),
        )
        if ranked:
            chosen = ranked[0]
            hospital = by_id[chosen.hospital_id]
            # Reserve the capacity this casualty would consume so the NEXT
            # casualty's ranking reflects a hospital that is now busier.
            if casualty.get("requires_icu"):
                hospital["icu_beds_available"] = max(0, hospital["icu_beds_available"] - 1)
            else:
                hospital["general_beds_available"] = max(0, hospital["general_beds_available"] - 1)
            hospital["emergency_load_pct"] = min(100, hospital["emergency_load_pct"] + 2)

            distribution[chosen.hospital_id] += 1
            allocations.append({
                "casualty_id": casualty["casualty_id"],
                "severity": casualty["severity"],
                "required_specialty": casualty.get("required_specialty"),
                "assigned_hospital_id": chosen.hospital_id,
                "assigned_hospital_name": chosen.name,
                "score": round(chosen.total_score),
                "eta_min": chosen.eta_min,
            })
        else:
            unassigned += 1
            reason = rejected[0].reason if rejected else "No hospital met the requirements at the time of allocation."
            allocations.append({
                "casualty_id": casualty["casualty_id"],
                "severity": casualty["severity"],
                "required_specialty": casualty.get("required_specialty"),
                "assigned_hospital_id": None,
                "assigned_hospital_name": None,
                "score": None,
                "eta_min": None,
                "reason": reason,
            })

    # Restore original casualty order for display.
    allocations.sort(key=lambda a: int(a["casualty_id"][1:]) if a["casualty_id"][1:].isdigit() else 0)
    distribution_named = [
        {"hospital_id": hid, "hospital_name": by_id[hid]["name"], "patients_assigned": count}
        for hid, count in distribution.items() if count > 0
    ]
    distribution_named.sort(key=lambda d: d["patients_assigned"], reverse=True)

    return {
        "event_id": new_id("CAS"),
        "created_at": now_iso(),
        "location_label": location_label,
        "lat": lat,
        "lng": lng,
        "total_casualties": len(casualties),
        "unassigned": unassigned,
        "allocations": allocations,
        "distribution": distribution_named,
    }
