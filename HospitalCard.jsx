import { useState } from "react";
import { BedDouble, HeartPulse, Users, Droplet, Phone, ChevronDown, Save, Loader2 } from "lucide-react";
import Tag from "./Tag";
import { titleCase } from "../lib/constants";

function loadTone(pct) {
  if (pct >= 75) return "text-critical";
  if (pct >= 50) return "text-serious";
  return "text-moderate";
}

export default function HospitalCard({ hospital, doctors, onUpdate }) {
  const [expanded, setExpanded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState(() => ({
    icu_beds_available: hospital.icu_beds_available,
    general_beds_available: hospital.general_beds_available,
    status: hospital.status,
    specialist_on_call: { ...hospital.specialist_on_call },
  }));

  function openEditor() {
    setDraft({
      icu_beds_available: hospital.icu_beds_available,
      general_beds_available: hospital.general_beds_available,
      status: hospital.status,
      specialist_on_call: { ...hospital.specialist_on_call },
    });
    setExpanded((v) => !v);
  }

  async function save() {
    setSaving(true);
    try {
      await onUpdate(hospital.hospital_id, draft);
      setExpanded(false);
    } finally {
      setSaving(false);
    }
  }

  const bloodLow = Object.entries(hospital.blood_inventory).filter(([, units]) => units <= 1);
  const hospitalDoctors = doctors.filter((d) => d.hospital_id === hospital.hospital_id);

  return (
    <div className="rounded-2xl border border-console-border bg-console-panel">
      <div className="flex items-start justify-between gap-3 p-4">
        <div>
          <div className="flex items-center gap-2">
            <p className="font-display text-base font-semibold text-console-text">{hospital.name}</p>
            <Tag variant={hospital.status === "active" ? "moderate" : hospital.status === "diverting" ? "serious" : "critical"}>
              {titleCase(hospital.status)}
            </Tag>
          </div>
          <p className="mt-0.5 flex items-center gap-1 text-xs text-console-muted">
            <Phone size={11} /> {hospital.phone} · Level {hospital.trauma_level} trauma centre · {hospital.hospital_id}
          </p>
        </div>
        {hospital.incoming_patients.length > 0 && (
          <Tag variant="live" pulse>
            {hospital.incoming_patients.length} incoming
          </Tag>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 border-t border-console-border px-4 py-3.5">
        <Stat icon={HeartPulse} label="ICU beds" value={`${hospital.icu_beds_available}/${hospital.icu_beds_total}`} />
        <Stat icon={BedDouble} label="General beds" value={`${hospital.general_beds_available}/${hospital.general_beds_total}`} />
        <Stat icon={Users} label="ED load" value={`${hospital.emergency_load_pct}%`} tone={loadTone(hospital.emergency_load_pct)} />
      </div>

      <div className="flex flex-wrap gap-1.5 border-t border-console-border px-4 py-3">
        {hospital.specialties.map((s) => (
          <span
            key={s}
            className={`rounded-full border px-2 py-0.5 text-[11px] ${
              hospital.specialist_on_call[s]
                ? "border-moderate/40 bg-moderate-soft text-moderate"
                : "border-console-border text-console-muted"
            }`}
            title={hospital.specialist_on_call[s] ? "On call now" : "Not on shift"}
          >
            {titleCase(s)}
          </span>
        ))}
      </div>

      <div className="flex items-center justify-between gap-2 border-t border-console-border px-4 py-3 text-xs text-console-muted">
        <span className="flex items-center gap-1.5">
          <Droplet size={13} />
          {bloodLow.length > 0 ? (
            <span className="text-serious">Low stock: {bloodLow.map(([g]) => g).join(", ")}</span>
          ) : (
            "Blood stock nominal"
          )}
        </span>
        <span>{hospitalDoctors.filter((d) => d.available).length}/{hospitalDoctors.length} doctors on shift</span>
      </div>

      <button
        onClick={openEditor}
        className="flex w-full items-center justify-center gap-1.5 border-t border-console-border py-2.5 text-xs font-medium text-console-muted hover:text-console-text"
      >
        <ChevronDown size={14} className={`transition-transform ${expanded ? "rotate-180" : ""}`} />
        {expanded ? "Close" : "Update live status"}
      </button>

      {expanded && (
        <div className="flex flex-col gap-3 border-t border-console-border bg-console-raised p-4">
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1 text-xs text-console-muted">
              ICU beds available (of {hospital.icu_beds_total})
              <input
                type="number"
                min={0}
                max={hospital.icu_beds_total}
                className="input"
                value={draft.icu_beds_available}
                onChange={(e) => setDraft((d) => ({ ...d, icu_beds_available: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1 text-xs text-console-muted">
              General beds available (of {hospital.general_beds_total})
              <input
                type="number"
                min={0}
                max={hospital.general_beds_total}
                className="input"
                value={draft.general_beds_available}
                onChange={(e) => setDraft((d) => ({ ...d, general_beds_available: Number(e.target.value) }))}
              />
            </label>
          </div>

          <label className="flex flex-col gap-1 text-xs text-console-muted">
            Facility status
            <select className="input" value={draft.status} onChange={(e) => setDraft((d) => ({ ...d, status: e.target.value }))}>
              <option value="active">Active — accepting emergencies</option>
              <option value="diverting">Diverting — not accepting new cases</option>
              <option value="full">Full</option>
            </select>
          </label>

          <div>
            <p className="mb-1.5 text-xs text-console-muted">Specialist on call</p>
            <div className="flex flex-wrap gap-1.5">
              {hospital.specialties.map((s) => (
                <button
                  type="button"
                  key={s}
                  onClick={() =>
                    setDraft((d) => ({
                      ...d,
                      specialist_on_call: { ...d.specialist_on_call, [s]: !d.specialist_on_call[s] },
                    }))
                  }
                  className={`rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
                    draft.specialist_on_call[s]
                      ? "border-moderate/50 bg-moderate-soft text-moderate"
                      : "border-console-border text-console-muted"
                  }`}
                >
                  {titleCase(s)}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={save}
            disabled={saving}
            className="flex items-center justify-center gap-2 self-start rounded-lg bg-accent px-3.5 py-2 text-xs font-semibold text-console-bg hover:opacity-90 disabled:opacity-60"
          >
            {saving ? <Loader2 size={13} className="animate-spin" /> : <Save size={13} />}
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value, tone }) {
  return (
    <div>
      <p className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-console-muted">
        <Icon size={11} /> {label}
      </p>
      <p className={`font-display text-sm font-semibold ${tone ?? "text-console-text"}`}>{value}</p>
    </div>
  );
}
