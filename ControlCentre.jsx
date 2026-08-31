import { useState } from "react";
import { Siren, Truck, Gauge, TriangleAlert, ClipboardList, ChevronDown } from "lucide-react";
import Panel from "../components/Panel";
import SummaryCard from "../components/SummaryCard";
import Tag from "../components/Tag";
import EmptyState from "../components/EmptyState";
import EmergencyIntakeForm from "../components/EmergencyIntakeForm";
import RecommendationCard from "../components/RecommendationCard";
import { usePoll } from "../lib/usePoll";
import { api, ApiError } from "../lib/api";
import { STATUS_STYLE, titleCase } from "../lib/constants";

async function loadSummary() {
  const [hospitals, ambulances, emergencies] = await Promise.all([
    api.listHospitals(),
    api.listAmbulances(),
    api.listEmergencies(20),
  ]);
  return { hospitals: hospitals.hospitals, ambulances: ambulances.ambulances, emergencies: emergencies.emergencies };
}

export default function ControlCentre() {
  const { data, loading, refetch } = usePoll(loadSummary, { intervalMs: 6000 });

  const [analysis, setAnalysis] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState(null);
  const [confirmingId, setConfirmingId] = useState(null);
  const [showRejected, setShowRejected] = useState(false);

  async function handleAnalyze(payload) {
    setAnalyzing(true);
    setAnalyzeError(null);
    setShowRejected(false);
    try {
      const result = await api.analyzeEmergency(payload);
      setAnalysis(result);
    } catch (err) {
      setAnalyzeError(err instanceof ApiError ? err.message : "Something went wrong analyzing this case.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleConfirm(hospitalId) {
    if (!analysis) return;
    setConfirmingId(hospitalId);
    try {
      const result = await api.confirmDestination(analysis.emergency_id, { hospital_id: hospitalId });
      setAnalysis((prev) => ({ ...prev, emergency: result.emergency }));
      refetch();
    } catch (err) {
      setAnalyzeError(err instanceof ApiError ? err.message : "Could not confirm this destination.");
    } finally {
      setConfirmingId(null);
    }
  }

  const hospitals = data?.hospitals ?? [];
  const ambulances = data?.ambulances ?? [];
  const emergencies = data?.emergencies ?? [];

  const avgLoad = hospitals.length
    ? Math.round(hospitals.reduce((sum, h) => sum + h.emergency_load_pct, 0) / hospitals.length)
    : 0;
  const ambulancesAvailable = ambulances.filter((a) => a.status === "available").length;
  const activeEmergencies = emergencies.filter((e) => e.status !== "closed").length;
  const alerts = hospitals.filter((h) => h.status !== "active" || h.icu_beds_available === 0).length;

  const confirmedHospitalId = analysis?.emergency?.confirmed_hospital_id;

  return (
    <div className="flex flex-col gap-5">
      <header className="flex items-center justify-between rounded-2xl border border-console-border bg-console-panel px-5 py-4 shadow-[0_10px_18px_rgba(15,23,42,0.03)]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-display text-2xl font-semibold tracking-tight text-console-text">Operations Overview</h1>
            <Tag variant="live" pulse>
              LIVE
            </Tag>
          </div>
          <p className="mt-1 text-sm text-console-muted">
            Regional emergency coordination and hospital readiness status.
          </p>
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={Siren} label="Active emergencies" value={loading ? "—" : activeEmergencies} tone="accent" />
        <SummaryCard icon={Truck} label="Ambulances available" value={loading ? "—" : `${ambulancesAvailable}/${ambulances.length}`} tone="moderate" />
        <SummaryCard icon={Gauge} label="Avg hospital load" value={loading ? "—" : `${avgLoad}%`} tone={avgLoad > 70 ? "critical" : avgLoad > 50 ? "serious" : "moderate"} />
        <SummaryCard icon={TriangleAlert} label="Network alerts" value={loading ? "—" : alerts} tone={alerts > 0 ? "serious" : "default"} sub={alerts > 0 ? "Diversion required" : "Nominal status"} />
      </div>

      <div className="grid grid-cols-[380px_1fr] items-start gap-5">
        <Panel title="Emergency intake">
          <EmergencyIntakeForm onAnalyze={handleAnalyze} analyzing={analyzing} />
        </Panel>

        <Panel
          title="AERON recommendation"
          action={
            analysis && (
              <span className="text-[11px] text-console-muted">
                {analysis.ranked_hospitals.length} eligible · {analysis.rejected_hospitals.length} not suitable
              </span>
            )
          }
        >
          {analyzeError && (
            <div className="mb-4 rounded-lg border border-critical/40 bg-critical-soft px-3.5 py-2.5 text-sm text-critical">
              {analyzeError}
            </div>
          )}

          {!analysis && !analyzeError && (
            <EmptyState
              icon={Siren}
              title="No case analyzed yet"
              hint="Fill in the emergency intake form and select Analyze with AERON to see ranked hospital recommendations."
            />
          )}

          {analysis && (
            <div className="flex flex-col gap-4">
              <p className="rounded-lg bg-console-raised px-3.5 py-2.5 text-sm text-console-text">{analysis.summary}</p>

              <div className="flex flex-col gap-3">
                {analysis.ranked_hospitals.map((h, i) => (
                  <RecommendationCard
                    key={h.hospital_id}
                    hospital={h}
                    rank={i + 1}
                    isTop={i === 0}
                    onConfirm={handleConfirm}
                    confirming={confirmingId === h.hospital_id}
                    isConfirmed={confirmedHospitalId === h.hospital_id}
                  />
                ))}
                {analysis.ranked_hospitals.length === 0 && (
                  <EmptyState
                    icon={TriangleAlert}
                    title="No suitable hospital found"
                    hint="Every hospital in the network was rejected for this case. Check the requirements or see the reasons below."
                  />
                )}
              </div>

              {analysis.rejected_hospitals.length > 0 && (
                <div>
                  <button
                    onClick={() => setShowRejected((v) => !v)}
                    className="flex items-center gap-1.5 text-xs font-medium text-console-muted hover:text-console-text"
                  >
                    <ChevronDown size={14} className={`transition-transform ${showRejected ? "rotate-180" : ""}`} />
                    {showRejected ? "Hide" : "Show"} {analysis.rejected_hospitals.length} not-suitable hospital(s)
                  </button>
                  {showRejected && (
                    <ul className="mt-2 flex flex-col gap-1.5">
                      {analysis.rejected_hospitals.map((r) => (
                        <li key={r.hospital_id} className="rounded-lg bg-console-raised px-3 py-2 text-xs text-console-muted">
                          <span className="font-medium text-console-text">{r.name}</span> — {r.reason}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <p className="border-t border-console-border pt-3 text-[11px] text-console-muted">
                Prototype decision weights — Clinical capability 30% · Capacity 25% · ETA 20% · Doctor availability 15% · Resource availability 10%. Not clinically validated; see the Implemented / Simulated / Future notes.
              </p>
            </div>
          )}
        </Panel>
      </div>

      <Panel
        title="Active emergencies"
        action={<ClipboardList size={16} className="text-console-muted" />}
      >
        {emergencies.length === 0 ? (
          <EmptyState icon={ClipboardList} title="No emergencies logged yet this session" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-[11px] uppercase tracking-wide text-console-muted">
                  <th className="pb-2 pr-4 font-medium">ID</th>
                  <th className="pb-2 pr-4 font-medium">Type</th>
                  <th className="pb-2 pr-4 font-medium">Severity</th>
                  <th className="pb-2 pr-4 font-medium">Location</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium">Destination</th>
                </tr>
              </thead>
              <tbody>
                {emergencies.map((e) => (
                  <tr key={e.emergency_id} className="border-t border-console-border">
                    <td className="py-2 pr-4 font-mono text-xs text-console-muted">{e.emergency_id}</td>
                    <td className="py-2 pr-4">{e.emergency_type}</td>
                    <td className="py-2 pr-4">
                      <Tag variant={e.severity}>{titleCase(e.severity)}</Tag>
                    </td>
                    <td className="py-2 pr-4 text-console-muted">{e.location_label}</td>
                    <td className={`py-2 pr-4 ${STATUS_STYLE[e.status]?.text ?? ""}`}>{STATUS_STYLE[e.status]?.label ?? e.status}</td>
                    <td className="py-2 pr-4 text-console-muted">{e.confirmed_hospital_id ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </div>
  );
}
