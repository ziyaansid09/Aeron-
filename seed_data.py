"""
Synthetic operational data for the AERON prototype.

Every name, coordinate and inventory number below is FICTIONAL and
generated for demo purposes only (see Section 45 of the master spec:
"Never imply that simulated data is real hospital data"). Coordinates
are loosely scattered around Mumbai so distance/ETA scoring behaves
realistically, but no record corresponds to a real facility.

This module is the SINGLE SOURCE OF TRUTH for demo data. Both the
in-memory fallback store and scripts/seed_mongo.py (which populates a
real MongoDB Atlas cluster) import from here, so the two can never
drift out of sync.
"""
from __future__ import annotations
import copy

# ---------------------------------------------------------------------------
# Hospitals
# ---------------------------------------------------------------------------
# trauma_level: 1 = Level-I trauma centre (highest capability) ... 3 = lowest
# specialist_on_call: True = that specialty currently has a doctor on shift
HOSPITALS: list[dict] = [
    {
        "hospital_id": "H01",
        "name": "Kirti Multispecialty Hospital",
        "lat": 19.0176, "lng": 72.8438,  # Dadar
        "trauma_level": 1,
        "icu_beds_total": 20, "icu_beds_available": 6,
        "general_beds_total": 90, "general_beds_available": 21,
        "emergency_load_pct": 55,
        "specialties": ["neurosurgery", "cardiology", "orthopedics", "general_surgery", "burns"],
        "specialist_on_call": {"neurosurgery": True, "cardiology": True, "orthopedics": False, "general_surgery": True, "burns": False},
        "blood_inventory": {"O-": 1, "O+": 9, "A+": 6, "A-": 2, "B+": 5, "B-": 1, "AB+": 3, "AB-": 1},
        "resources": {"ventilators_available": 5, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0101",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H02",
        "name": "Sanjeevani Trauma Center",
        "lat": 19.0728, "lng": 72.8826,  # Kurla
        "trauma_level": 1,
        "icu_beds_total": 15, "icu_beds_available": 2,
        "general_beds_total": 60, "general_beds_available": 14,
        "emergency_load_pct": 70,
        "specialties": ["neurosurgery", "orthopedics", "general_surgery"],
        "specialist_on_call": {"neurosurgery": True, "orthopedics": True, "general_surgery": True},
        "blood_inventory": {"O-": 5, "O+": 4, "A+": 3, "A-": 1, "B+": 2, "B-": 0, "AB+": 1, "AB-": 0},
        "resources": {"ventilators_available": 2, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0102",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H03",
        "name": "Lakeview General Hospital",
        "lat": 19.1176, "lng": 72.9060,  # Powai
        "trauma_level": 2,
        "icu_beds_total": 10, "icu_beds_available": 4,
        "general_beds_total": 70, "general_beds_available": 30,
        "emergency_load_pct": 40,
        "specialties": ["cardiology", "general_surgery", "pediatrics"],
        "specialist_on_call": {"cardiology": True, "general_surgery": True, "pediatrics": True},
        "blood_inventory": {"O-": 2, "O+": 8, "A+": 5, "A-": 2, "B+": 4, "B-": 1, "AB+": 2, "AB-": 0},
        "resources": {"ventilators_available": 3, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0103",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H04",
        "name": "Horizon City Hospital",
        "lat": 19.0596, "lng": 72.8295,  # Bandra
        "trauma_level": 1,
        "icu_beds_total": 25, "icu_beds_available": 9,
        "general_beds_total": 110, "general_beds_available": 40,
        "emergency_load_pct": 30,
        "specialties": ["neurosurgery", "cardiology", "orthopedics", "general_surgery", "burns", "obstetrics"],
        "specialist_on_call": {"neurosurgery": True, "cardiology": True, "orthopedics": True, "general_surgery": True, "burns": True, "obstetrics": True},
        "blood_inventory": {"O-": 6, "O+": 12, "A+": 9, "A-": 3, "B+": 7, "B-": 2, "AB+": 4, "AB-": 2},
        "resources": {"ventilators_available": 8, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0104",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H05",
        "name": "Sunrise Community Hospital",
        "lat": 19.2307, "lng": 72.8567,  # Borivali
        "trauma_level": 3,
        "icu_beds_total": 8, "icu_beds_available": 3,
        "general_beds_total": 50, "general_beds_available": 22,
        "emergency_load_pct": 45,
        "specialties": ["general_surgery", "pediatrics", "obstetrics"],
        "specialist_on_call": {"general_surgery": True, "pediatrics": False, "obstetrics": True},
        "blood_inventory": {"O-": 0, "O+": 5, "A+": 3, "A-": 0, "B+": 2, "B-": 0, "AB+": 1, "AB-": 0},
        "resources": {"ventilators_available": 1, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0105",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H06",
        "name": "Metro Central Hospital",
        "lat": 19.1197, "lng": 72.8468,  # Andheri
        "trauma_level": 1,
        "icu_beds_total": 18, "icu_beds_available": 0,
        "general_beds_total": 80, "general_beds_available": 6,
        "emergency_load_pct": 88,
        "specialties": ["neurosurgery", "cardiology", "general_surgery"],
        "specialist_on_call": {"neurosurgery": False, "cardiology": True, "general_surgery": True},
        "blood_inventory": {"O-": 3, "O+": 6, "A+": 4, "A-": 1, "B+": 3, "B-": 1, "AB+": 2, "AB-": 0},
        "resources": {"ventilators_available": 0, "oxygen_ok": False},
        "status": "active",
        "phone": "+91-22-5550-0106",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H07",
        "name": "Green Valley Hospital",
        "lat": 19.0855, "lng": 72.9081,  # Ghatkopar
        "trauma_level": 2,
        "icu_beds_total": 12, "icu_beds_available": 5,
        "general_beds_total": 65, "general_beds_available": 26,
        "emergency_load_pct": 50,
        "specialties": ["orthopedics", "general_surgery", "burns"],
        "specialist_on_call": {"orthopedics": True, "general_surgery": True, "burns": True},
        "blood_inventory": {"O-": 1, "O+": 5, "A+": 3, "A-": 1, "B+": 2, "B-": 0, "AB+": 1, "AB-": 0},
        "resources": {"ventilators_available": 2, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0107",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H08",
        "name": "Unity Multispecialty Hospital",
        "lat": 19.0522, "lng": 72.9005,  # Chembur
        "trauma_level": 1,
        "icu_beds_total": 16, "icu_beds_available": 7,
        "general_beds_total": 75, "general_beds_available": 25,
        "emergency_load_pct": 35,
        "specialties": ["neurosurgery", "cardiology", "orthopedics", "general_surgery", "pediatrics"],
        "specialist_on_call": {"neurosurgery": True, "cardiology": False, "orthopedics": True, "general_surgery": True, "pediatrics": True},
        "blood_inventory": {"O-": 4, "O+": 7, "A+": 5, "A-": 2, "B+": 3, "B-": 1, "AB+": 2, "AB-": 1},
        "resources": {"ventilators_available": 4, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0108",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H09",
        "name": "Coastal Care Hospital",
        "lat": 18.9067, "lng": 72.8147,  # Colaba
        "trauma_level": 2,
        "icu_beds_total": 9, "icu_beds_available": 1,
        "general_beds_total": 55, "general_beds_available": 12,
        "emergency_load_pct": 60,
        "specialties": ["cardiology", "general_surgery", "obstetrics"],
        "specialist_on_call": {"cardiology": True, "general_surgery": False, "obstetrics": True},
        "blood_inventory": {"O-": 2, "O+": 4, "A+": 2, "A-": 1, "B+": 2, "B-": 0, "AB+": 1, "AB-": 0},
        "resources": {"ventilators_available": 1, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0109",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H10",
        "name": "Riverside Trauma & Emergency Institute",
        "lat": 19.0448, "lng": 72.8619,  # Sion
        "trauma_level": 1,
        "icu_beds_total": 22, "icu_beds_available": 10,
        "general_beds_total": 95, "general_beds_available": 38,
        "emergency_load_pct": 25,
        "specialties": ["neurosurgery", "orthopedics", "general_surgery", "burns"],
        "specialist_on_call": {"neurosurgery": True, "orthopedics": True, "general_surgery": True, "burns": False},
        "blood_inventory": {"O-": 2, "O+": 9, "A+": 6, "A-": 2, "B+": 4, "B-": 1, "AB+": 2, "AB-": 1},
        "resources": {"ventilators_available": 6, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0110",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H11",
        "name": "Eastside District Hospital",
        "lat": 19.0771, "lng": 72.9986,  # Vashi
        "trauma_level": 3,
        "icu_beds_total": 6, "icu_beds_available": 2,
        "general_beds_total": 40, "general_beds_available": 15,
        "emergency_load_pct": 65,
        "specialties": ["general_surgery", "pediatrics"],
        "specialist_on_call": {"general_surgery": True, "pediatrics": True},
        "blood_inventory": {"O-": 0, "O+": 3, "A+": 2, "A-": 0, "B+": 1, "B-": 0, "AB+": 0, "AB-": 0},
        "resources": {"ventilators_available": 1, "oxygen_ok": True},
        "status": "diverting",  # currently NOT accepting new emergencies
        "phone": "+91-22-5550-0111",
        "incoming_patients": [],
    },
    {
        "hospital_id": "H12",
        "name": "Grand Central Medical College Hospital",
        "lat": 19.0072, "lng": 72.8410,  # Parel
        "trauma_level": 1,
        "icu_beds_total": 30, "icu_beds_available": 12,
        "general_beds_total": 140, "general_beds_available": 55,
        "emergency_load_pct": 20,
        "specialties": ["neurosurgery", "cardiology", "orthopedics", "general_surgery", "burns", "obstetrics", "pediatrics"],
        "specialist_on_call": {"neurosurgery": True, "cardiology": True, "orthopedics": True, "general_surgery": True, "burns": True, "obstetrics": False, "pediatrics": True},
        "blood_inventory": {"O-": 8, "O+": 14, "A+": 10, "A-": 4, "B+": 8, "B-": 2, "AB+": 5, "AB-": 2},
        "resources": {"ventilators_available": 9, "oxygen_ok": True},
        "status": "active",
        "phone": "+91-22-5550-0112",
        "incoming_patients": [],
    },
]

# ---------------------------------------------------------------------------
# Doctors — derived from each hospital's specialties / specialist_on_call so
# the "doctors" collection can never contradict the decision engine's view
# of who is on call. Two doctors per specialty per hospital (one on shift
# matching specialist_on_call, one off shift) comfortably clears the
# "20-30 doctors" target from the action plan.
# ---------------------------------------------------------------------------
_SURNAMES = [
    "Rao", "Mehta", "Iyer", "Shah", "Khan", "Fernandes", "Kulkarni", "Nair",
    "Gupta", "Reddy", "Bose", "Chatterjee", "Pillai", "Desai", "Verma",
    "Kapoor", "Menon", "Joshi", "Sharma", "D'Souza", "Patil", "Bhatt",
    "Chawla", "Rana",
]


def _build_doctors() -> list[dict]:
    doctors: list[dict] = []
    name_idx = 0
    doc_seq = 1
    for hospital in HOSPITALS:
        for specialty in hospital["specialties"]:
            on_shift = hospital["specialist_on_call"].get(specialty, False)
            for slot in range(2):  # primary + backup doctor
                surname = _SURNAMES[name_idx % len(_SURNAMES)]
                name_idx += 1
                available = on_shift if slot == 0 else False
                doctors.append({
                    "doctor_id": f"D{doc_seq:03d}",
                    "name": f"Dr. {surname}",
                    "specialty": specialty,
                    "hospital_id": hospital["hospital_id"],
                    "available": available,
                    "on_call": slot == 0,
                })
                doc_seq += 1
    return doctors


DOCTORS: list[dict] = _build_doctors()

# ---------------------------------------------------------------------------
# Ambulances
# ---------------------------------------------------------------------------
AMBULANCES: list[dict] = [
    {"ambulance_id": "A01", "type": "ALS", "lat": 19.0330, "lng": 72.8570, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 1"},
    {"ambulance_id": "A02", "type": "ALS", "lat": 19.0400, "lng": 72.8700, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 2"},
    {"ambulance_id": "A03", "type": "BLS", "lat": 19.0700, "lng": 72.8800, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 3"},
    {"ambulance_id": "A04", "type": "ALS", "lat": 19.1100, "lng": 72.8500, "status": "dispatched", "assigned_emergency_id": None, "target_hospital_id": "H06", "crew": "Paramedic Team 4"},
    {"ambulance_id": "A05", "type": "BLS", "lat": 19.2200, "lng": 72.8600, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 5"},
    {"ambulance_id": "A06", "type": "ALS", "lat": 19.0550, "lng": 72.8300, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 6"},
    {"ambulance_id": "A07", "type": "BLS", "lat": 19.0850, "lng": 72.9050, "status": "enroute", "assigned_emergency_id": None, "target_hospital_id": "H07", "crew": "Paramedic Team 7"},
    {"ambulance_id": "A08", "type": "ALS", "lat": 19.0100, "lng": 72.8400, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 8"},
    {"ambulance_id": "A09", "type": "ALS", "lat": 19.0450, "lng": 72.8600, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 9"},
    {"ambulance_id": "A10", "type": "BLS", "lat": 19.1000, "lng": 72.9900, "status": "available", "assigned_emergency_id": None, "target_hospital_id": None, "crew": "Paramedic Team 10"},
]

# ---------------------------------------------------------------------------
# Blood banks
# ---------------------------------------------------------------------------
BLOOD_BANKS: list[dict] = [
    {"blood_bank_id": "B01", "name": "Mumbai Central Blood Bank", "lat": 19.0330, "lng": 72.8570,
     "inventory": {"O-": 6, "O+": 20, "A+": 15, "A-": 5, "B+": 12, "B-": 3, "AB+": 6, "AB-": 2}},
    {"blood_bank_id": "B02", "name": "Suburban Regional Blood Centre", "lat": 19.1197, "lng": 72.8468,
     "inventory": {"O-": 4, "O+": 14, "A+": 10, "A-": 3, "B+": 9, "B-": 2, "AB+": 4, "AB-": 1}},
    {"blood_bank_id": "B03", "name": "Harbour View Blood Bank", "lat": 18.9067, "lng": 72.8147,
     "inventory": {"O-": 2, "O+": 10, "A+": 7, "A-": 2, "B+": 6, "B-": 1, "AB+": 3, "AB-": 1}},
    {"blood_bank_id": "B04", "name": "Eastern Belt Blood Bank", "lat": 19.0855, "lng": 72.9081,
     "inventory": {"O-": 3, "O+": 11, "A+": 8, "A-": 2, "B+": 7, "B-": 1, "AB+": 2, "AB-": 0}},
    {"blood_bank_id": "B05", "name": "Navi Mumbai Blood Bank", "lat": 19.0771, "lng": 72.9986,
     "inventory": {"O-": 5, "O+": 9, "A+": 6, "A-": 1, "B+": 5, "B-": 1, "AB+": 2, "AB-": 1}},
]


def fresh_dataset() -> dict[str, list[dict]]:
    """
    Returns a brand-new, independent deep copy of the full seed dataset.
    Used to (re)initialise the in-memory store so mutations made during a
    demo (confirming an emergency, running a mass-casualty simulation)
    never bleed into the untouched HOSPITALS/DOCTORS/... constants above.
    """
    return {
        "hospitals": copy.deepcopy(HOSPITALS),
        "doctors": copy.deepcopy(DOCTORS),
        "ambulances": copy.deepcopy(AMBULANCES),
        "blood_banks": copy.deepcopy(BLOOD_BANKS),
        "emergencies": [],
        "casualty_events": [],
    }
