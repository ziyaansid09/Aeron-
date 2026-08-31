# AERON — Six-Slide PPT Outline (D1)

Official SIH structure: Title → Idea/Proposed Solution → Technical Approach
→ Feasibility & Viability → Impact & Benefits → Research & References.
This is content, not layout — D1 owns turning this into the actual slides.

---

## Slide 1 — Title

- **AERON** — AI Emergency Response & Resource Orchestration Network
- Tagline: *Right Patient. Right Hospital. Right Resources. Right Time.*
- Team **Chirons Cure** · SIH 2026

---

## Slide 2 — Idea / Proposed Solution

- The real problem isn't transport, it's suitability: a patient can reach
  the nearest hospital fast and still hit an unavailable ICU, an
  unavailable specialist, or an empty blood bank.
- AERON changes the question from **"nearest hospital"** to **"most
  suitable available hospital, right now."**
- Connects: Control Centre → Ambulance → Hospital → Doctors → Blood banks →
  Critical resources, into one coordination layer.
- Second capability: **Mass-Casualty Mode** — distributes many patients
  across a hospital network instead of overloading the nearest one.
- Explicit boundary: AERON recommends; qualified medical professionals
  decide. Not an autonomous doctor, not an EHR replacement, not a
  transfusion or organ-allocation authority.

---

## Slide 3 — Technical Approach

- **Architecture (5 layers):** Data/Integration → Prediction & Decision →
  AERON Core Engine → Resource Allocation → Coordination/Action.
- **Decision engine (Round 1):** transparent, rule-based scoring —
  Clinical capability 30% · Capacity 25% · ETA 20% · Doctor availability
  15% · Resource availability 10%. Every recommendation ships with a
  checklist of *why*, not just a number.
- **Stack:** React + Vite + Tailwind (frontend) · FastAPI (backend) ·
  MongoDB Atlas (data, with an automatic in-memory fallback so the demo
  never depends on connectivity) · Leaflet + OpenStreetMap (map).
- **Mass-casualty allocation:** greedy, severity-first, network-aware
  heuristic — formal OR-Tools optimization is the planned future upgrade.
- Live demo: emergency intake → ranked recommendation → ambulance + map →
  hospital readiness → blood check → 20-patient mass-casualty allocation.

---

## Slide 4 — Feasibility & Viability

- **Round 1 scope is intentionally narrow:** one working, explainable
  slice — not the full system. Everything unfinished is explicitly future
  scope, never overclaimed.
- **Cost:** built entirely on free/open-source tooling for the prototype
  (React, FastAPI, MongoDB Atlas free tier, Leaflet/OSM, OR-Tools is
  Apache-2.0). No metered APIs required to demonstrate the concept.
- **Risks & mitigations:** MongoDB unavailable → local JSON fallback ·
  routing API unavailable → Leaflet with stored coordinates · live demo
  failure → recorded backup video. Three fallback levels, always.
- **6-month roadmap:** validation → core platform → intelligence
  (forecasting) → optimization (OR-Tools) → integration (real HIS/GPS/
  blood-bank APIs) → validation/pilot.

---

## Slide 5 — Impact & Benefits

- Reduces avoidable secondary transfers caused by sending patients to a
  hospital that turns out to lack ICU capacity, the right specialist, or
  blood stock.
- Makes doctor and resource availability part of the routing decision,
  not something discovered after arrival.
- Mass-casualty allocation prevents single-hospital overload during major
  incidents — a genuine network-level capability existing single-hospital
  systems don't provide.
- Every recommendation is explainable (a judge, a coordinator, or a
  clinician can see exactly why a hospital was or wasn't chosen) —
  operational trust by design, not a black box.
- Long-term potential: hospital networks, ambulance providers, and
  government emergency-command platforms (B2B/GovTech), sold as *"better
  emergency resource decisions before bottlenecks become critical,"* not
  as *"we have AI."*

---

## Slide 6 — Research & References

- **Core research question:** does network-level decision support
  (capacity + specialist + resource + severity considered together)
  outperform a simple nearest-hospital approach? Measured via average
  travel time, hospital-overload events, specialist mismatch, resource
  mismatch, unnecessary transfers, and network capacity utilization —
  benchmarked experimentally in the next phase, not asserted here.
- **Positioning vs. existing systems:** existing hospital software already
  handles single-hospital operations, capacity management, and patient
  flow well. AERON's gap is the layer *above* that — cross-hospital
  emergency coordination — not a replacement for hospital-level tools.
- **Tooling references:** Google OR-Tools (Apache 2.0, optimization) ·
  Leaflet/OpenStreetMap (mapping) · FastAPI, MongoDB Atlas, React
  (implementation stack) — see `docs/implemented_simulated_future.md` for
  the full implemented/simulated/future breakdown backing every claim
  above.
