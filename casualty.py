from fastapi import APIRouter, Depends, HTTPException

from ..database import Store, get_store
from ..casualty_engine import simulate_mass_casualty
from ..schemas import MassCasualtyRequest

router = APIRouter(prefix="/mass-casualty", tags=["mass-casualty"])


@router.post("/simulate")
def simulate(body: MassCasualtyRequest, store: Store = Depends(get_store)):
    hospitals = store.list_hospitals()
    explicit = [c.model_dump() for c in body.casualties] if body.casualties else None
    for i, c in enumerate(explicit or [], start=1):
        c.setdefault("casualty_id", f"P{i:02d}")

    result = simulate_mass_casualty(
        hospitals,
        lat=body.lat,
        lng=body.lng,
        location_label=body.location_label or "Mass-casualty incident site",
        critical_count=body.critical_count,
        serious_count=body.serious_count,
        moderate_count=body.moderate_count,
        explicit_casualties=explicit,
    )
    store.save_casualty_event(result)
    return result


@router.get("/events")
def list_events(limit: int = 20, store: Store = Depends(get_store)):
    return {"events": store.list_casualty_events(limit)}


@router.get("/events/{event_id}")
def get_event(event_id: str, store: Store = Depends(get_store)):
    event = store.get_casualty_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Casualty event '{event_id}' not found")
    return event
