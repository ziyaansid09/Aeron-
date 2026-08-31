from fastapi import APIRouter, Depends, HTTPException

from ..database import Store, get_store
from ..decision_engine import rank_hospitals, build_recommendation_summary
from ..schemas import EmergencyAnalyzeRequest, ConfirmDestinationRequest
from ..utils import new_id, now_iso, haversine_km

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.post("/analyze")
def analyze_emergency(body: EmergencyAnalyzeRequest, store: Store = Depends(get_store)):
    """
    The 'ANALYZE WITH AERON' action. Runs the decision engine against
    every hospital currently in the store and returns a ranked,
    explainable list plus the hard-rejected hospitals and why.
    Also stores the emergency (status='analyzed') so it shows up on the
    Control Centre's active-emergencies list and can later be confirmed.
    """
    hospitals = store.list_hospitals()
    ranked, rejected = rank_hospitals(
        hospitals,
        severity=body.severity,
        origin_lat=body.lat,
        origin_lng=body.lng,
        required_specialty=body.required_specialty,
        requires_icu=body.requires_icu,
        blood_group=body.blood_group,
        blood_units=body.blood_units,
    )

    emergency_id = new_id("E")
    emergency = {
        "emergency_id": emergency_id,
        "created_at": now_iso(),
        "status": "analyzed",
        **body.model_dump(),
        "ranked_hospital_ids": [h.hospital_id for h in ranked],
        "confirmed_hospital_id": None,
        "assigned_ambulance_id": None,
    }
    store.save_emergency(emergency)

    return {
        "emergency_id": emergency_id,
        "emergency": emergency,
        "ranked_hospitals": [h.to_dict() for h in ranked],
        "rejected_hospitals": [h.to_dict() for h in rejected],
        "top_recommendation": ranked[0].to_dict() if ranked else None,
        "summary": build_recommendation_summary(ranked),
        "weights": {
            "clinical_capability": "30%", "capacity": "25%", "eta": "20%",
            "doctor_availability": "15%", "resource_availability": "10%",
        },
    }


@router.get("")
def list_emergencies(limit: int = 50, store: Store = Depends(get_store)):
    return {"emergencies": store.list_emergencies(limit)}


@router.get("/{emergency_id}")
def get_emergency(emergency_id: str, store: Store = Depends(get_store)):
    e = store.get_emergency(emergency_id)
    if e is None:
        raise HTTPException(status_code=404, detail=f"Emergency '{emergency_id}' not found")
    return e


@router.post("/{emergency_id}/confirm")
def confirm_destination(emergency_id: str, body: ConfirmDestinationRequest, store: Store = Depends(get_store)):
    """
    The 'CONFIRM DESTINATION' action. Locks in a hospital (defaults to
    the top recommendation), assigns the nearest available ambulance,
    reserves a bed at the destination, and marks the hospital as having
    an incoming patient — this is what makes the Hospital and Ambulance
    dashboards light up together.
    """
    emergency = store.get_emergency(emergency_id)
    if emergency is None:
        raise HTTPException(status_code=404, detail=f"Emergency '{emergency_id}' not found")

    hospital_id = body.hospital_id or (
        emergency["ranked_hospital_ids"][0] if emergency.get("ranked_hospital_ids") else None
    )
    if not hospital_id:
        raise HTTPException(status_code=400, detail="No hospital_id given and no prior recommendation to fall back on.")
    hospital = store.get_hospital(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail=f"Hospital '{hospital_id}' not found")

    if body.ambulance_id:
        ambulance = store.get_ambulance(body.ambulance_id)
        if ambulance is None:
            raise HTTPException(status_code=404, detail=f"Ambulance '{body.ambulance_id}' not found")
        if ambulance["status"] != "available":
            raise HTTPException(status_code=409, detail=f"Ambulance '{body.ambulance_id}' is not available.")
    else:
        candidates = store.list_ambulances(status="available")
        if not candidates:
            raise HTTPException(status_code=409, detail="No ambulance is currently available.")
        ambulance = min(
            candidates,
            key=lambda a: haversine_km(emergency["lat"], emergency["lng"], a["lat"], a["lng"]),
        )

    store.update_ambulance(ambulance["ambulance_id"], {
        "status": "dispatched",
        "assigned_emergency_id": emergency_id,
        "target_hospital_id": hospital_id,
    })

    bed_field = "icu_beds_available" if emergency.get("requires_icu") else "general_beds_available"
    store.update_hospital(hospital_id, {bed_field: max(0, hospital[bed_field] - 1)})
    store.add_incoming_patient(hospital_id, emergency_id)

    updated = store.update_emergency(emergency_id, {
        "status": "dispatched",
        "confirmed_hospital_id": hospital_id,
        "assigned_ambulance_id": ambulance["ambulance_id"],
    })

    return {
        "emergency": updated,
        "hospital": store.get_hospital(hospital_id),
        "ambulance": store.get_ambulance(ambulance["ambulance_id"]),
    }
