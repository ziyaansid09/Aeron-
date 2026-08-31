"""
AERON storage layer — Backend Member 2 (B2) core deliverable.

Two interchangeable stores implement the SAME explicit interface
(`Store`), so every router calls e.g. `store.list_hospitals()` and
never knows or cares whether the data is coming from MongoDB Atlas or
from memory:

  * MongoStore   — real MongoDB Atlas, database `aeron_db`
                   (collections: hospitals, doctors, ambulances,
                   blood_banks, emergencies, casualty_events)
  * MemoryStore  — the seed_data.py dataset held in RAM

Section 9 of the master spec ("Emergency Fallback Plan") calls this
out explicitly: "MongoDB unavailable -> switch to local JSON dataset."
That fallback is implemented here, automatically, at startup — the
rest of the app never has to think about it. If MONGO_URI is unset,
unreachable, or the driver isn't installed, AERON silently boots on
MemoryStore instead of crashing.

NOTE: deliberately no generic Mongo-style query matcher for
MemoryStore. Each method below is a named, single-purpose operation
(list_hospitals, get_hospital, update_hospital, ...) — easier for a
hackathon team to read, extend and debug than a mini query engine.
"""
from __future__ import annotations
import logging
from typing import Optional, Protocol

from .config import settings
from .seed_data import fresh_dataset

logger = logging.getLogger("aeron.database")


class Store(Protocol):
    backend_name: str

    def list_hospitals(self) -> list[dict]: ...
    def get_hospital(self, hospital_id: str) -> Optional[dict]: ...
    def update_hospital(self, hospital_id: str, patch: dict) -> Optional[dict]: ...
    def add_incoming_patient(self, hospital_id: str, emergency_id: str) -> None: ...

    def list_doctors(self, hospital_id: Optional[str] = None) -> list[dict]: ...

    def list_ambulances(self, status: Optional[str] = None) -> list[dict]: ...
    def get_ambulance(self, ambulance_id: str) -> Optional[dict]: ...
    def update_ambulance(self, ambulance_id: str, patch: dict) -> Optional[dict]: ...

    def list_blood_banks(self) -> list[dict]: ...

    def save_emergency(self, doc: dict) -> dict: ...
    def get_emergency(self, emergency_id: str) -> Optional[dict]: ...
    def update_emergency(self, emergency_id: str, patch: dict) -> Optional[dict]: ...
    def list_emergencies(self, limit: int = 50) -> list[dict]: ...

    def save_casualty_event(self, doc: dict) -> dict: ...
    def get_casualty_event(self, event_id: str) -> Optional[dict]: ...
    def list_casualty_events(self, limit: int = 20) -> list[dict]: ...


# ---------------------------------------------------------------------------
# In-memory implementation (default / fallback)
# ---------------------------------------------------------------------------
class MemoryStore:
    backend_name = "memory (fallback dataset)"

    def __init__(self) -> None:
        self._data = fresh_dataset()

    # -- hospitals --
    def list_hospitals(self) -> list[dict]:
        return list(self._data["hospitals"])

    def get_hospital(self, hospital_id: str) -> Optional[dict]:
        return next((h for h in self._data["hospitals"] if h["hospital_id"] == hospital_id), None)

    def update_hospital(self, hospital_id: str, patch: dict) -> Optional[dict]:
        hospital = self.get_hospital(hospital_id)
        if hospital is None:
            return None
        hospital.update(patch)
        return hospital

    def add_incoming_patient(self, hospital_id: str, emergency_id: str) -> None:
        hospital = self.get_hospital(hospital_id)
        if hospital is not None:
            hospital.setdefault("incoming_patients", [])
            if emergency_id not in hospital["incoming_patients"]:
                hospital["incoming_patients"].append(emergency_id)

    # -- doctors --
    def list_doctors(self, hospital_id: Optional[str] = None) -> list[dict]:
        docs = self._data["doctors"]
        if hospital_id:
            docs = [d for d in docs if d["hospital_id"] == hospital_id]
        return list(docs)

    # -- ambulances --
    def list_ambulances(self, status: Optional[str] = None) -> list[dict]:
        ambs = self._data["ambulances"]
        if status:
            ambs = [a for a in ambs if a["status"] == status]
        return list(ambs)

    def get_ambulance(self, ambulance_id: str) -> Optional[dict]:
        return next((a for a in self._data["ambulances"] if a["ambulance_id"] == ambulance_id), None)

    def update_ambulance(self, ambulance_id: str, patch: dict) -> Optional[dict]:
        amb = self.get_ambulance(ambulance_id)
        if amb is None:
            return None
        amb.update(patch)
        return amb

    # -- blood banks --
    def list_blood_banks(self) -> list[dict]:
        return list(self._data["blood_banks"])

    # -- emergencies --
    def save_emergency(self, doc: dict) -> dict:
        self._data["emergencies"].insert(0, doc)
        return doc

    def get_emergency(self, emergency_id: str) -> Optional[dict]:
        return next((e for e in self._data["emergencies"] if e["emergency_id"] == emergency_id), None)

    def update_emergency(self, emergency_id: str, patch: dict) -> Optional[dict]:
        e = self.get_emergency(emergency_id)
        if e is None:
            return None
        e.update(patch)
        return e

    def list_emergencies(self, limit: int = 50) -> list[dict]:
        return list(self._data["emergencies"][:limit])

    # -- casualty events --
    def save_casualty_event(self, doc: dict) -> dict:
        self._data["casualty_events"].insert(0, doc)
        return doc

    def get_casualty_event(self, event_id: str) -> Optional[dict]:
        return next((c for c in self._data["casualty_events"] if c["event_id"] == event_id), None)

    def list_casualty_events(self, limit: int = 20) -> list[dict]:
        return list(self._data["casualty_events"][:limit])


# ---------------------------------------------------------------------------
# MongoDB Atlas implementation
# ---------------------------------------------------------------------------
class MongoStore:
    backend_name = "MongoDB Atlas"

    def __init__(self, uri: str, db_name: str) -> None:
        from pymongo import MongoClient  # imported lazily so pymongo is optional at runtime

        self._client = MongoClient(uri, serverSelectionTimeoutMS=4000)
        self._client.admin.command("ping")  # fail fast if unreachable
        self._db = self._client[db_name]

    @staticmethod
    def _clean(doc: Optional[dict]) -> Optional[dict]:
        if doc is not None:
            doc.pop("_id", None)
        return doc

    # -- hospitals --
    def list_hospitals(self) -> list[dict]:
        return [self._clean(d) for d in self._db.hospitals.find({})]

    def get_hospital(self, hospital_id: str) -> Optional[dict]:
        return self._clean(self._db.hospitals.find_one({"hospital_id": hospital_id}))

    def update_hospital(self, hospital_id: str, patch: dict) -> Optional[dict]:
        self._db.hospitals.update_one({"hospital_id": hospital_id}, {"$set": patch})
        return self.get_hospital(hospital_id)

    def add_incoming_patient(self, hospital_id: str, emergency_id: str) -> None:
        self._db.hospitals.update_one(
            {"hospital_id": hospital_id}, {"$addToSet": {"incoming_patients": emergency_id}}
        )

    # -- doctors --
    def list_doctors(self, hospital_id: Optional[str] = None) -> list[dict]:
        query = {"hospital_id": hospital_id} if hospital_id else {}
        return [self._clean(d) for d in self._db.doctors.find(query)]

    # -- ambulances --
    def list_ambulances(self, status: Optional[str] = None) -> list[dict]:
        query = {"status": status} if status else {}
        return [self._clean(d) for d in self._db.ambulances.find(query)]

    def get_ambulance(self, ambulance_id: str) -> Optional[dict]:
        return self._clean(self._db.ambulances.find_one({"ambulance_id": ambulance_id}))

    def update_ambulance(self, ambulance_id: str, patch: dict) -> Optional[dict]:
        self._db.ambulances.update_one({"ambulance_id": ambulance_id}, {"$set": patch})
        return self.get_ambulance(ambulance_id)

    # -- blood banks --
    def list_blood_banks(self) -> list[dict]:
        return [self._clean(d) for d in self._db.blood_banks.find({})]

    # -- emergencies --
    def save_emergency(self, doc: dict) -> dict:
        self._db.emergencies.insert_one(dict(doc))
        return doc

    def get_emergency(self, emergency_id: str) -> Optional[dict]:
        return self._clean(self._db.emergencies.find_one({"emergency_id": emergency_id}))

    def update_emergency(self, emergency_id: str, patch: dict) -> Optional[dict]:
        self._db.emergencies.update_one({"emergency_id": emergency_id}, {"$set": patch})
        return self.get_emergency(emergency_id)

    def list_emergencies(self, limit: int = 50) -> list[dict]:
        cursor = self._db.emergencies.find({}).sort("created_at", -1).limit(limit)
        return [self._clean(d) for d in cursor]

    # -- casualty events --
    def save_casualty_event(self, doc: dict) -> dict:
        self._db.casualty_events.insert_one(dict(doc))
        return doc

    def get_casualty_event(self, event_id: str) -> Optional[dict]:
        return self._clean(self._db.casualty_events.find_one({"event_id": event_id}))

    def list_casualty_events(self, limit: int = 20) -> list[dict]:
        cursor = self._db.casualty_events.find({}).sort("created_at", -1).limit(limit)
        return [self._clean(d) for d in cursor]

    def seed_if_empty(self) -> None:
        """Populate Atlas from seed_data.py the first time it's ever connected."""
        data = fresh_dataset()
        for name in ("hospitals", "doctors", "ambulances", "blood_banks"):
            if self._db[name].count_documents({}) == 0 and data[name]:
                self._db[name].insert_many(data[name])
                logger.info("Seeded %s documents into '%s'", len(data[name]), name)


def _build_store() -> Store:
    if settings.MONGO_URI:
        try:
            store = MongoStore(settings.MONGO_URI, settings.MONGO_DB_NAME)
            store.seed_if_empty()
            logger.info("Connected to MongoDB Atlas ('%s').", settings.MONGO_DB_NAME)
            return store
        except Exception as exc:  # noqa: BLE001 — any failure must not crash the app
            logger.warning(
                "MongoDB unreachable (%s). Falling back to the in-memory dataset — "
                "the app is fully functional, just not persistent.",
                exc,
            )
    else:
        logger.info("MONGO_URI not set — using the in-memory dataset.")
    return MemoryStore()


store: Store = _build_store()


def get_store() -> Store:
    """FastAPI dependency — lets routes be tested with a fake store if needed."""
    return store
