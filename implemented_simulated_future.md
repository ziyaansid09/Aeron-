# AERON — Implemented / Simulated / Future

One page, memorize the top row. This is the honesty contract for the demo
(Sections 44, 45, 54 of the master spec) — never say or imply anything
outside these columns.

## ✅ Implemented (Round 1, working code)

| Component | What actually runs |
|---|---|
| Emergency Control Centre | Real intake form → real API call → real ranked results |
| AERON decision engine | Transparent, rule-based scoring (5 weighted factors), running against live in-app hospital state |
| Hospital suitability ranking | Real scoring + hard-reject logic (missing specialty, diverting status) |
| Doctor availability | Real on-call flags per hospital, factored into the score and editable live |
| Hospital dashboard | Real read + live-edit of ICU/beds/status/specialist availability |
| Ambulance dashboard + map | Real fleet data, real nearest-ambulance assignment, real straight-line route rendering |
| Blood module | Real shortfall detection + nearest sufficient source lookup |
| Mass-casualty allocation | Real greedy allocation algorithm distributing patients across the network |

## 🟡 Simulated (real code, fake underlying data/infrastructure)

| Component | What's simulated |
|---|---|
| Hospital / doctor / ambulance / blood-bank records | Synthetic data, not a real hospital's data (`app/seed_data.py`) |
| GPS / ambulance position | Fixed demo coordinates, not a live device feed |
| ETA | Straight-line (haversine) distance ÷ average speed — not real routing, traffic, or road network |
| Blood-bank network | A local dataset standing in for a real blood-bank API |
| Severity assessment | Manually selected by the operator (a valid Round-1 approach per the spec), not a clinical model |

## 🔵 Future (explicitly out of scope for Tuesday)

ML demand/capacity prediction · formal OR-Tools optimization · real
hospital HIS/EHR integration · real blood-bank API integration · real
ambulance GPS · government emergency-network integration · offline mode ·
production security/auth hardening · transplant logistics (NOTTO/ROTTO/SOTTO)

## The one line to say if asked "where's the AI?"

> "Our current prototype uses a transparent rule-based decision engine and
> simulated operational data to validate the workflow. The next phase adds
> trained models and formal optimization after data validation."

## The one line to say if asked about the data

> "The prototype uses synthetic hospital, ambulance, doctor and blood-bank
> data so we can validate the full workflow without needing real patient
> information. A pilot would use governed, anonymized hospital data."
