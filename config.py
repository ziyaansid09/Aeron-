"""
AERON backend configuration.

Everything the app needs from the environment is read once, here,
so no other module ever calls os.getenv() directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # loads backend/.env if present; safe no-op otherwise


class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "").strip()
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "aeron_db").strip()

    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

    # Prototype decision-engine weights (Section 33 of the master spec).
    # These are stated in the demo as "prototype assumptions, not
    # clinically validated weights" — keep them visible & easy to tune.
    WEIGHT_CLINICAL_CAPABILITY: float = 0.30
    WEIGHT_CAPACITY: float = 0.25
    WEIGHT_ETA: float = 0.20
    WEIGHT_DOCTOR_AVAILABILITY: float = 0.15
    WEIGHT_RESOURCE_AVAILABILITY: float = 0.10

    # Simple straight-line ETA model (prototype only — NOT real routing).
    AVG_AMBULANCE_SPEED_KMPH: float = 35.0
    DISPATCH_DELAY_MIN: float = 3.0


settings = Settings()
