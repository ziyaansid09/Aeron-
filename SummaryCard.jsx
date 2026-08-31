export default function SummaryCard({ icon: Icon, label, value, tone = "default", sub }) {
  const toneClass =
    {
      default: "text-console-text",
      accent: "text-accent",
      critical: "text-critical",
      serious: "text-serious",
      moderate: "text-moderate",
    }[tone] || "text-console-text";

  return (
    <div className="flex items-center gap-3.5 rounded-2xl border border-console-border bg-console-panel px-4 py-4 shadow-[0_10px_18px_rgba(15,23,42,0.03)]">
      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-console-raised text-console-muted ring-1 ring-console-border">
        <Icon size={18} strokeWidth={2} />
      </span>
      <div className="min-w-0">
        <p className="text-[10px] uppercase tracking-[0.18em] text-console-muted">{label}</p>
        <p className={`mt-1 font-display text-[1.6rem] font-semibold leading-none ${toneClass}`}>{value}</p>
        {sub && <p className="mt-1 truncate text-[11px] text-console-muted">{sub}</p>}
      </div>
    </div>
  );
}
