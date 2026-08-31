import { CircleCheck, CircleX } from "lucide-react";

export default function Checklist({ items }) {
  if (!items?.length) return null;
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1.5">
      {items.map((item) => (
        <li key={item.label} className="flex items-center gap-1.5 text-xs" title={item.detail}>
          {item.ok ? (
            <CircleCheck size={14} className="shrink-0 text-moderate" />
          ) : (
            <CircleX size={14} className="shrink-0 text-critical" />
          )}
          <span className={item.ok ? "text-console-text" : "text-console-muted"}>{item.label}</span>
        </li>
      ))}
    </ul>
  );
}
