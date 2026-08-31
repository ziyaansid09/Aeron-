from fastapi import APIRouter, Depends, HTTPException

from ..database import Store, get_store
from ..schemas import HospitalStatusUpdate

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("")
def list_hospitals(store: Store = Depends(get_store)):
    return {"hospitals": store.list_hospitals()}


@router.get("/{hospital_id}")
def get_hospital(hospital_id: str, store: Store = Depends(get_store)):
    hospital = store.get_hospital(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail=f"Hospital '{hospital_id}' not found")
    return hospital


@router.patch("/{hospital_id}/status")
def update_hospital_status(hospital_id: str, body: HospitalStatusUpdate, store: Store = Depends(get_store)):
    """
    Live operator control used by the Hospital Emergency Coordinator role
    (Section 6) and by the Monday-night demo beat: "change the recommended
    hospital's ICU status to unavailable, re-run ANALYZE, show the
    recommendation changes."
    """
    hospital = store.get_hospital(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail=f"Hospital '{hospital_id}' not found")

    patch: dict = {}
    if body.icu_beds_available is not None:
        patch["icu_beds_available"] = min(body.icu_beds_available, hospital["icu_beds_total"])
    if body.general_beds_available is not None:
        patch["general_beds_available"] = min(body.general_beds_available, hospital["general_beds_total"])
    if body.emergency_load_pct is not None:
        patch["emergency_load_pct"] = body.emergency_load_pct
    if body.status is not None:
        patch["status"] = body.status
    if body.specialist_on_call is not None:
        merged = dict(hospital.get("specialist_on_call", {}))
        merged.update(body.specialist_on_call)
        patch["specialist_on_call"] = merged
    if body.blood_inventory_delta is not None:
        merged_inv = dict(hospital.get("blood_inventory", {}))
        for group, delta in body.blood_inventory_delta.items():
            merged_inv[group] = max(0, merged_inv.get(group, 0) + delta)
        patch["blood_inventory"] = merged_inv

    updated = store.update_hospital(hospital_id, patch)
    return updated
