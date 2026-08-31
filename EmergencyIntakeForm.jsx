import { useState } from "react";
import { Siren, Loader2 } from "lucide-react";
import { SPECIALTIES, BLOOD_GROUPS, SEVERITIES, LOCATIONS, titleCase } from "../lib/constants";

const EMERGENCY_TYPES = [
  "Road Traffic Accident",
  "Cardiac Arrest",
  "Stroke",
  "Fall from Height",
  "Burns",
  "Obstetric Emergency",
  "Penetrating Trauma",
  "Respiratory Distress",
];

const initialForm = {
  emergency_type: EMERGENCY_TYPES[0],
  severity: "critical",
  locationIndex: 0,
  lat: LOCATIONS[0].lat,
  lng: LOCATIONS[0].lng,
  required_specialty: "",
  requires_icu: true,
  blood_group: "",
  blood_units: 2,
};

export default function EmergencyIntakeForm({ onAnalyze, analyzing }) {
  const [form, setForm] = useState(initialForm);

  function updateLocation(index) {
    const loc = LOCATIONS[index];
    setForm((f) => ({
      ...f,
      locationIndex: index,
      lat: loc.lat ?? f.lat,
      lng: loc.lng ?? f.lng,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onAnalyze({
      emergency_type: form.emergency_type,
      severity: form.severity,
      lat: Number(form.lat),
      lng: Number(form.lng),
      location_label: LOCATIONS[form.locationIndex].label,
      required_specialty: form.required_specialty || null,
      requires_icu: form.requires_icu,
      blood_group: form.blood_group || null,
      blood_units: form.blood_group ? Number(form.blood_units) : null,
    });
  }

  const isCustomLocation = LOCATIONS[form.locationIndex].lat === null;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4">
        <Field label="Emergency type">
          <select
            className="input"
            value={form.emergency_type}
            onChange={(e) => setForm((f) => ({ ...f, emergency_type: e.target.value }))}
          >
            {EMERGENCY_TYPES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </Field>

        <Field label="Severity">
          <div className="flex gap-1.5">
            {SEVERITIES.map((s) => (
              <button
                type="button"
                key={s.value}
                onClick={() => setForm((f) => ({ ...f, severity: s.value }))}
                className={`flex-1 rounded-lg border px-2 py-2 text-xs font-semibold transition-colors ${
                  form.severity === s.value
                    ? s.value === "critical"
                      ? "border-critical/50 bg-critical-soft text-critical"
                      : s.value === "serious"
                      ? "border-serious/50 bg-serious-soft text-serious"
                      : "border-moderate/50 bg-moderate-soft text-moderate"
                    : "border-console-border bg-console-raised text-console-muted hover:text-console-text"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </Field>
      </div>

      <Field label="Incident location">
        <select
          className="input"
          value={form.locationIndex}
          onChange={(e) => updateLocation(Number(e.target.value))}
        >
          {LOCATIONS.map((loc, i) => (
            <option key={loc.label} value={i}>
              {loc.label}
            </option>
          ))}
        </select>
        {isCustomLocation && (
          <div className="mt-2 grid grid-cols-2 gap-2">
            <input
              type="number"
              step="0.0001"
              className="input"
              placeholder="Latitude"
              value={form.lat ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, lat: e.target.value }))}
              required
            />
            <input
              type="number"
              step="0.0001"
              className="input"
              placeholder="Longitude"
              value={form.lng ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, lng: e.target.value }))}
              required
            />
          </div>
        )}
      </Field>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Required specialty">
          <select
            className="input"
            value={form.required_specialty}
            onChange={(e) => setForm((f) => ({ ...f, required_specialty: e.target.value }))}
          >
            <option value="">General / none specific</option>
            {SPECIALTIES.map((s) => (
              <option key={s} value={s}>
                {titleCase(s)}
              </option>
            ))}
          </select>
        </Field>

        <Field label="ICU required">
          <label className="input flex cursor-pointer items-center justify-between">
            <span className="text-sm">Patient needs an ICU bed</span>
            <input
              type="checkbox"
              className="h-4 w-4 accent-[color:var(--color-accent)]"
              checked={form.requires_icu}
              onChange={(e) => setForm((f) => ({ ...f, requires_icu: e.target.checked }))}
            />
          </label>
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Field label="Blood group needed">
          <select
            className="input"
            value={form.blood_group}
            onChange={(e) => setForm((f) => ({ ...f, blood_group: e.target.value }))}
          >
            <option value="">Not required</option>
            {BLOOD_GROUPS.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </Field>
        <Field label="Units needed">
          <input
            type="number"
            min={1}
            max={20}
            className="input disabled:opacity-40"
            disabled={!form.blood_group}
            value={form.blood_units}
            onChange={(e) => setForm((f) => ({ ...f, blood_units: e.target.value }))}
          />
        </Field>
      </div>

      <button
        type="submit"
        disabled={analyzing}
        className="mt-1 flex items-center justify-center gap-2 rounded-xl bg-accent px-4 py-3 font-display text-sm font-semibold text-console-bg transition-opacity hover:opacity-90 disabled:opacity-60"
      >
        {analyzing ? <Loader2 size={16} className="animate-spin" /> : <Siren size={16} />}
        {analyzing ? "Analyzing…" : "Analyze with AERON"}
      </button>
    </form>
  );
}

function Field({ label, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-console-muted">{label}</span>
      {children}
    </label>
  );
}
