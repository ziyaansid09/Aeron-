import { useEffect, useMemo, useState } from "react";
import { Truck, Navigation, Droplet, HeartPulse, Stethoscope } from "lucide-react";
import Panel from "../components/Panel";
import Tag from "../components/Tag";
import EmptyState from "../components/EmptyState";
import AmbulanceMap from "../components/AmbulanceMap";
import { usePoll } from "../lib/usePoll";
import { api } from "../lib/api";
import { titleCase } from "../lib/constants";
import { haversineKm, etaMinutes } from "../lib/geo";

async function loadData() {
  const [hospitals, ambulances] = await Promise.all([api.listHospitals(), api.listAmbulances()]);
  return { hospitals: hospitals.hospitals, ambulances: ambulances.ambulances };
}

export default function AmbulanceDashboard() {
  const { data, loading } = usePoll(loadData, { intervalMs: 5000 });
  const hospitals = data?.hospitals ?? [];
  const ambulances = data?.ambulances ?? [];

  const [selectedId, setSelectedId] = useState(null);
  const [emergency, setEmergency] = useState(null);

  // Default to the first dispatched/en-route unit once data arrives, so the
  // demo has something interesting on screen without a click.
  useEffect(() => {
    if (!selectedId && ambulances.length) {
      const busy = ambulances.find((a) => a.status !== "available");
      setSelectedId((busy ?? ambulances[0]).ambulance_id);
    }
  }, [ambulances, selectedId]);

  const selected = useMemo(() => ambulances.find((a) => a.ambulance_id === selectedId) ?? null, [ambulances, selectedId]);

  useEffect(() => {
    let cancelled = false;
    if (selected?.assigned_emergency_id) {
      api
        .getEmergency(selected.assigned_emergency_id)
        .then((e) => !cancelled && setEmergency(e))
        .catch(() => !cancelled && setEmergency(null));
    } else {
      setEmergency(null);
    }
    return () => {
      cancelled = true;
    };
  }, [selected?.assigned_emergency_id]);

  const destinationHospital = hospitals.find((h) => h.hospital_id === selected?.target_hospital_id);

  return (
    <div className="flex flex-col gap-5">
      <header className="flex items-center gap-2.5">
        <h1 className="font-display text-2xl font-semibold text-console-text">Ambulance Dashboard</h1>
        <Tag variant="simulated">Simulated GPS · straight-line ETA</Tag>
      </header>

      <div className="grid grid-cols-[300px_1fr] gap-5">
        <Panel title="Fleet" action={<Truck size={16} className="text-console-muted" />} className="h-fit">
          {loading && !data ? (
            <p className="text-sm text-console-muted">Loading fleet…</p>
          ) : (
            <div className="flex flex-col gap-1.5">
              {ambulances.map((a) => (
                <button
                  key={a.ambulance_id}
                  onClick={() => setSelectedId(a.ambulance_id)}
                  className={`flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-sm transition-colors ${
                    a.ambulance_id === selectedId
                      ? "border-accent/50 bg-accent-soft/30"
                      : "border-transparent bg-console-raised hover:border-console-border"
                  }`}
                >
                  <span>
                    <span className="font-mono text-xs text-console-muted">{a.ambulance_id}</span>
                    <span className="ml-2 text-console-text">{a.type}</span>
                  </span>
                  <Tag variant={a.status === "available" ? "moderate" : a.status === "dispatched" ? "serious" : "neutral"}>
                    {titleCase(a.status)}
                  </Tag>
                </button>
              ))}
            </div>
          )}
        </Panel>

        <div className="flex flex-col gap-5">
          <Panel title="Live map" className="overflow-hidden">
            <div className="h-[420px]">
              <AmbulanceMap hospitals={hospitals} ambulances={ambulances} selected={selected} emergency={emergency} />
            </div>
          </Panel>

          <Panel title="Selected unit" action={<Navigation size={16} className="text-console-muted" />}>
            {!selected ? (
              <EmptyState icon={Truck} title="Select an ambulance from the fleet list" />
            ) : (
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-display text-lg font-semibold text-console-text">{selected.ambulance_id} · {selected.type}</p>
                    <p className="text-xs text-console-muted">{selected.crew}</p>
                  </div>
                  <Tag variant={selected.status === "available" ? "moderate" : selected.status === "dispatched" ? "serious" : "neutral"}>
                    {titleCase(selected.status)}
                  </Tag>
                </div>

                {emergency ? (
                  <div className="grid grid-cols-2 gap-3 rounded-xl border border-console-border bg-console-raised p-4 text-sm">
                    <Detail icon={HeartPulse} label="Patient" value={`${titleCase(emergency.severity)} — ${emergency.emergency_type}`} />
                    <Detail icon={Stethoscope} label="ICU required" value={emergency.requires_icu ? "Yes" : "No"} />
                    <Detail icon={Stethoscope} label="Specialist" value={emergency.required_specialty ? titleCase(emergency.required_specialty) : "General"} />
                    <Detail icon={Droplet} label="Blood" value={emergency.blood_group ? `${emergency.blood_group} × ${emergency.blood_units}` : "Not required"} />
                    <Detail icon={Navigation} label="Recommended hospital" value={destinationHospital?.name ?? "—"} />
                    <Detail
                      icon={Navigation}
                      label="ETA to hospital"
                      value={
                        destinationHospital
                          ? `${etaMinutes(haversineKm(selected.lat, selected.lng, destinationHospital.lat, destinationHospital.lng))} min`
                          : "—"
                      }
                    />
                  </div>
                ) : (
                  <p className="text-sm text-console-muted">
                    {selected.status === "available"
                      ? "This unit is available and not currently assigned to a case."
                      : "No linked emergency record was found for this unit."}
                  </p>
                )}
              </div>
            )}
          </Panel>
        </div>
      </div>
    </div>
  );
}

function Detail({ icon: Icon, label, value }) {
  return (
    <div>
      <p className="flex items-center gap-1.5 text-[11px] uppercase tracking-wide text-console-muted">
        <Icon size={12} /> {label}
      </p>
      <p className="mt-0.5 font-medium text-console-text">{value}</p>
    </div>
  );
}
