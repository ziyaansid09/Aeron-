import { Navigation, Phone, Loader2, CircleCheck } from "lucide-react";
import ScoreBar from "./ScoreBar";
import Checklist from "./Checklist";

export default function RecommendationCard({ hospital, rank, isTop, onConfirm, confirming, isConfirmed }) {
  return (
    <div
      className={`flex flex-col gap-3 rounded-xl border p-4 transition-colors ${
        isTop ? "border-accent/50 bg-accent-soft/30" : "border-console-border bg-console-raised"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span
            className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg font-display text-sm font-semibold ${
              isTop ? "bg-accent text-console-bg" : "bg-console-panel text-console-muted"
            }`}
          >
            {rank}
          </span>
          <div>
            <p className="font-display text-base font-semibold text-console-text">{hospital.name}</p>
            <p className="flex items-center gap-1 text-xs text-console-muted">
              <Phone size={11} /> {hospital.phone} · {hospital.hospital_id}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className={`font-display text-2xl font-bold leading-none ${isTop ? "text-accent" : "text-console-text"}`}>
            {hospital.score}%
          </p>
          <p className="mt-1 flex items-center justify-end gap-1 text-xs text-console-muted">
            <Navigation size={11} /> {hospital.eta_min} min · {hospital.distance_km} km
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <ScoreBar breakdown={hospital.breakdown} compact />
        <Checklist items={hospital.checklist} />
      </div>

      {onConfirm && (
        <button
          onClick={() => onConfirm(hospital.hospital_id)}
          disabled={confirming || isConfirmed}
          className={`mt-1 flex items-center justify-center gap-2 self-start rounded-lg px-3.5 py-2 text-xs font-semibold transition-colors ${
            isConfirmed
              ? "cursor-default bg-moderate-soft text-moderate"
              : "bg-accent text-console-bg hover:opacity-90 disabled:opacity-60"
          }`}
        >
          {confirming ? (
            <Loader2 size={13} className="animate-spin" />
          ) : isConfirmed ? (
            <CircleCheck size={13} />
          ) : null}
          {isConfirmed ? "Destination confirmed" : confirming ? "Confirming…" : "Confirm destination"}
        </button>
      )}
    </div>
  );
}
