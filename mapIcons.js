import L from "leaflet";

// Leaflet's default marker icons reference image paths that break under
// Vite's bundler unless you re-wire them by hand. We sidestep that whole
// class of bug by never using L.Icon.Default — every marker here is a
// small styled div (emoji badge), which also happens to match the emoji
// vocabulary the master spec itself uses for this exact map (📍 🚑 🏥).
function badge(emoji, { ring = "var(--color-console-border)", size = 30 } = {}) {
  return L.divIcon({
    className: "",
    html: `<div style="
        width:${size}px;height:${size}px;border-radius:9999px;
        background:var(--color-console-panel);
        border:2px solid ${ring};
        display:flex;align-items:center;justify-content:center;
        font-size:${Math.round(size * 0.55)}px;
        box-shadow:0 2px 8px rgba(0,0,0,0.45);
      ">${emoji}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

export const hospitalIcon = (highlighted = false) =>
  badge("🏥", { ring: highlighted ? "var(--color-accent)" : "var(--color-console-border)", size: highlighted ? 34 : 28 });

export const ambulanceIcon = (status) => {
  const ring =
    status === "available" ? "var(--color-moderate)" : status === "dispatched" ? "var(--color-serious)" : "var(--color-info)";
  return badge("🚑", { ring, size: 28 });
};

export const emergencyIcon = () => badge("📍", { ring: "var(--color-critical)", size: 30 });
