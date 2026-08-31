"""
Prototype-grade geo helpers.

IMPORTANT (see docs/implemented_simulated_future.md): this is a
straight-line haversine distance converted to a flat average speed —
NOT real road routing, traffic, or GPS. It exists so the demo has a
believable, explainable ETA number. Swapping this for OSRM /
openrouteservice / Google Routes is explicitly future scope.
"""
import math
import uuid
from datetime import datetime, timezone

from .config import settings


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometres."""
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def eta_minutes(distance_km: float) -> float:
    """Straight-line ETA estimate: dispatch delay + travel time at a fixed average speed."""
    travel_min = (distance_km / settings.AVG_AMBULANCE_SPEED_KMPH) * 60
    return round(settings.DISPATCH_DELAY_MIN + travel_min, 1)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
