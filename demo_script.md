# AERON — Demo Script & Judge Q&A (D2)

Target: **4–5 minutes.** Rehearse this exact sequence three times without
changing it (Section 6 of the action plan). One presenter drives the
screen; a second narrates.

## Before you start

- [ ] Backend running, `/health` shows a data backend (memory or Atlas)
- [ ] Frontend running, Control Centre loads with the summary cards populated
- [ ] Optional: reset demo data to a clean state (`python -m scripts.seed_mongo` if on Atlas; restart the backend process if on the in-memory store)
- [ ] Backup video recorded and playable offline (Section 43, Level 3 fallback)

## The sequence

**1. Open on the Control Centre. (15s)**
> "This is AERON's Emergency Control Centre — where a dispatcher logs an
> incoming emergency. Right now the network has [N] hospitals, [N]
> ambulances available, and an average load of [N]%."
*(Point at the summary cards — they're live, not static.)*

**2. Fill the intake form. (30s)**
Emergency type **Road Traffic Accident**, severity **Critical**, location
**Sion Circle, Mumbai**, specialty **Neurosurgery**, **ICU required**
checked, blood **O−, 4 units**.
> "We're not just asking which hospital is nearest — we're asking which
> hospital is actually *suitable* right now."

**3. Click "Analyze with AERON." (20s)**
> "AERON just scored every hospital in the network on five weighted
> factors — clinical capability, capacity, ETA, doctor availability, and
> resource availability — and ranked them."
*(Point at the top card's score and the checklist — every ✓/✗ is a real
reason, not a black box.)*

**4. Click "Confirm destination" on the top card. (15s)**
> "Confirming assigns the nearest available ambulance and reserves a bed
> at the destination automatically."

**5. Switch to the Ambulance Dashboard. (25s)**
> "Here's that ambulance en route, with the recommended hospital, the
> patient's requirements, and a live ETA — and the map."
*(Point at the dashed route line and the patient-requirement panel.)*

**6. Switch to the Hospital Dashboard. (25s)**
> "And on the hospital side, that same case shows up as an incoming
> patient — the coordinator can see it and update readiness."

**7. The signature beat — live re-ranking. (40s)**
On the Hospital Dashboard, open **Update live status** on the
top-recommended hospital and set **ICU beds available to 0**. Save.
Go back to the Control Centre and click **Analyze with AERON** again with
the same case.
> "Watch the recommendation change in real time — this isn't a canned
> demo path, it's actually re-running the decision engine against live
> hospital state."

**8. Blood module. (20s)**
Open Blood, check **O−, 4 units** against the hospital you just picked.
> "If there's a shortfall, AERON identifies the nearest blood bank that
> actually has enough stock — it never makes the clinical transfusion
> decision itself, just surfaces availability."

**9. Mass-Casualty Mode — the closer. (40s)**
Open Mass-Casualty, keep the default 5 critical / 8 serious / 7 moderate,
click **Activate Mass-Casualty Mode**.
> "This is AERON's strongest capability: instead of every ambulance
> independently choosing the nearest hospital and overloading it, AERON
> distributes all 20 patients across the network at once."
*(Point at the bar chart — multiple hospitals, not one.)*

**10. Close on the honesty slide. (20s)**
> "Everything you just saw runs on real code against synthetic data —
> here's exactly what's implemented, what's simulated, and what's future
> scope." *(Show `docs/implemented_simulated_future.md` / the matching PPT slide.)*

## If something breaks live (Section 43)

1. **Level 1 (full stack breaks):** switch to the backend's in-memory
   fallback — it's already the default if Mongo was the failure point.
   Just restart `uvicorn`.
2. **Level 2 (backend itself won't come up):** narrate from the
   Implemented/Simulated/Future page and screenshots while someone
   restarts it in the background.
3. **Level 3 (nothing recovers in time):** play the recorded backup video,
   then explain the architecture from the PPT. Never apologize at length —
   move straight to the explanation.

## Judge Q&A cheat sheet (Section 53)

**"Why not just send the patient to the nearest hospital?"**
> Proximity alone doesn't capture whether the hospital currently has the
> capability and resources required — AERON considers operational
> suitability alongside ETA.

**"Doesn't hospital software already do this?"**
> Existing hospital systems already handle a lot of capacity and
> operational functionality. AERON is a cross-hospital emergency
> coordination layer, not another single-hospital dashboard.

**"Where is your AI?"**
> The current prototype validates the decision workflow with a
> transparent, rule-based engine. Production adds demand/capacity
> prediction models and formal optimization after data validation.

**"Where do you get your data?"**
> Synthetic operational data for the prototype, so we can validate the
> workflow without needing real patient information. A pilot would use
> governed, anonymized hospital data.

**"What happens if the recommended hospital suddenly becomes unavailable?"**
> AERON re-evaluates continuously — if state changes, the recommendation
> recalculates and another suitable facility is surfaced. *(This is
> literally step 7 of the demo — you've already shown it.)*

**"Are you making medical decisions?"**
> No. AERON is operational decision support. Clinical decisions stay with
> qualified medical professionals — including transfusion and treatment
> calls the blood module deliberately never makes.

**"What are those score weights based on?"**
> They're stated prototype assumptions (30/25/20/15/10), not clinically
> validated weights — that's said explicitly in the UI. Next phase is
> validating them with real healthcare stakeholders.
