# AERON — Round 1 Test Cases (D2)

20 test cases covering normal, edge, and failure conditions per Section 42
of the master spec. Each one is directly runnable against
`http://localhost:8000` — via curl, Postman, or the `/docs` Swagger UI.
Someone who did not write the code should be able to follow this file.

Legend: 🟢 normal flow · 🟡 edge case · 🔴 failure/invalid input

| # | Scenario | How to trigger it | Expected result |
|---|---|---|---|
| 1 🟢 | Canonical critical trauma case | `POST /emergency/analyze` — severity `critical`, `required_specialty=neurosurgery`, `requires_icu=true`, `blood_group=O-`, `blood_units=4`, at Sion Circle (19.033, 72.857) | Returns a ranked list; top hospital has trauma level 1, neurosurgery on call, ICU beds free, and a score in the 80–95% range |
| 2 🟢 | Recommendation is explainable | Same as #1 | Every hospital in the response has a non-empty `checklist` array and the top-level `summary` names concrete reasons — never a bare number |
| 3 🟢 | Confirm destination | `POST /emergency/{id}/confirm` right after #1, no body | Returns an `available` ambulance now `dispatched`, and the destination hospital's `incoming_patients` includes the emergency ID |
| 4 🟡 | ICU capacity forces a re-rank | `PATCH /hospitals/H12/status {"icu_beds_available": 0}`, then repeat #1 | H12's score drops and its checklist shows "ICU bed available: ✗"; a different hospital becomes the top pick |
| 5 🟡 | Required specialist unavailable, not rejected | `PATCH /hospitals/H06/status {"specialist_on_call": {"neurosurgery": false}}`, then #1 with H06 in range | H06 stays in the **ranked** list (it does offer neurosurgery) but is down-ranked, with "Neurosurgery on call: ✗" |
| 6 🔴 | Specialty not offered at all → hard reject | `POST /emergency/analyze` with `required_specialty=obstetrics` | Hospitals that don't list obstetrics (e.g. H01, H02) appear in `rejected_hospitals`, not `ranked_hospitals`, each with a stated reason |
| 7 🔴 | Hospital marked diverting → hard reject | Use `required_specialty=general_surgery` (H11 offers it but is seeded as `diverting`) | H11 appears in `rejected_hospitals` with reason mentioning "diverting" |
| 8 🟡 | Blood shortfall, network has enough | `GET /blood/availability?blood_group=O-&units=4&hospital_id=H01` | `hospital.shortfall > 0` (H01 is seeded with 1 unit), `recommended_sources` includes at least one bank with `sufficient: true` |
| 9 🔴 | Blood shortfall network-wide | `GET /blood/availability?blood_group=AB-&units=15` | No source has enough; every entry in `recommended_sources` shows `sufficient: false` |
| 10 🔴 | No suitable hospital at all | `POST /emergency/analyze` with an implausible combination (e.g. `required_specialty=obstetrics` **and** manually set every obstetrics hospital to `diverting` first) | `ranked_hospitals` is empty, `top_recommendation` is `null`, and `summary` reads "No suitable hospital was found..." — UI shows the empty state, not a crash |
| 11 🟡 | No ambulance available | `PATCH` every ambulance's status away from `available` (or just note current status), then `POST /emergency/{id}/confirm` | Returns HTTP 409 with a clear detail message; UI surfaces it as a banner, not a blank screen |
| 12 🟡 | Ambulance already busy, explicit ID | `POST /emergency/{id}/confirm {"ambulance_id": "A04"}` (A04 is seeded `dispatched`) | HTTP 409 — "not available" |
| 13 🟢 | Doctor availability changes the ranking | Toggle a hospital's on-call specialist off via the Hospital Dashboard UI, watch the Control Centre re-analyze | Score for that hospital drops specifically in the "Doctor" channel of its `ScoreBar`, nowhere else |
| 14 🟢 | Mass-casualty, canonical 20 | `POST /mass-casualty/simulate` with default counts (5/8/7) | `total_casualties == 20`, `distribution` spans **more than one** hospital (network-level spread, not a single dump) |
| 15 🟡 | Mass-casualty exceeds network capacity | Set `critical_count=200, serious_count=0, moderate_count=0` | Some casualties come back with `assigned_hospital_id: null` and a stated `reason`; `unassigned > 0`; app doesn't crash |
| 16 🔴 | Invalid severity | `POST /emergency/analyze` with `"severity": "urgent"` (not a real value) | HTTP 422 with a Pydantic validation message naming the allowed values |
| 17 🔴 | Invalid blood group | `GET /blood/availability?blood_group=X+&units=1` | HTTP 422 |
| 18 🟡 | Missing/zero blood_units with a blood_group set | `POST /emergency/analyze` with `blood_group="O-"`, `blood_units=0` | Backend treats "0 units requested" as no blood requirement (falsy) — resource score is not penalized for blood |
| 19 🟢 | Health / data-backend visibility | `GET /health` | 200 OK; `data_backend` field says `"memory (fallback dataset)"` or `"MongoDB Atlas"` depending on `.env` — useful to confirm which mode you're demoing on |
| 20 🟡 | Backend unreachable, frontend still usable | Stop the backend, reload any frontend page | Every panel shows its empty/error state (e.g. "Can't reach the AERON backend...") instead of a white screen or unhandled exception |

## Regression checklist before every rehearsal

Run these three, in order, after any code change — they cover the whole
critical path end to end:

1. Case #1 (canonical analyze) → top pick looks sane
2. Case #3 (confirm) → ambulance + hospital update together
3. Case #14 (mass casualty) → distribution spans multiple hospitals

If any of these three breaks, **stop and fix it before touching anything
else** — per the action plan's "if the core recommendation flow is broken,
do not add new features" rule.
