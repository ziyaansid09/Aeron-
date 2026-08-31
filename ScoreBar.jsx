// The signature visual element of the whole app: every hospital's score
// is shown as five weighted channels rather than a single bar, echoing a
// multi-channel vitals-monitor readout. This exists so the recommendation
// never reads as a mystery output — you can see exactly which factor
// helped or hurt a given hospital (Section 44: "explainable, not a
// mysterious AI output").
const CHANNELS = [
  { key: "clinical_capability", label: "Clinical", weight: "30%" },
  { key: "capacity", label: "Capacity", weight: "25%" },
  { key: "eta", label: "ETA", weight: "20%" },
  { key: "doctor_availability", label: "Doctor", weight: "15%" },
  { key: "resource_availability", label: "Resource", weight: "10%" },
];

function channelColor(value) {
  if (value >= 70) return "bg-moderate";
  if (value >= 40) return "bg-serious";
  return "bg-critical";
}

export default function ScoreBar({ breakdown, compact = false }) {
  if (!breakdown) return null;
  return (
    <div className={`grid grid-cols-5 gap-1.5 ${compact ? "" : "min-w-[180px]"}`}>
      {CHANNELS.map(({ key, label, weight }) => {
        const value = breakdown[key] ?? 0;
        return (
          <div key={key} className="flex flex-col items-center gap-1" title={`${label} (${weight} weight): ${value}`}>
            <div className="h-14 w-2 overflow-hidden rounded-full bg-console-border/70">
              <div
                className={`w-full rounded-full ${channelColor(value)} transition-[height]`}
                style={{ height: `${Math.max(4, value)}%`, marginTop: `${100 - Math.max(4, value)}%` }}
              />
            </div>
            {!compact && <span className="text-[9px] uppercase tracking-wide text-console-muted">{label}</span>}
          </div>
        );
      })}
    </div>
  );
}
