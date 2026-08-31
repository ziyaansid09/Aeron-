// Mirrors backend/app/utils.py so the frontend can show a live "ambulance
// current position -> destination hospital" ETA without an extra API call.
// Same disclaimer as the backend: straight-line distance, not real routing.
const AVG_SPEED_KMPH = 35;
const DISPATCH_DELAY_MIN = 3;

export function haversineKm(lat1, lng1, lat2, lng2) {
  const r = 6371.0088;
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLng = toRad(lng2 - lng1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
  return 2 * r * Math.asin(Math.sqrt(a));
}

export function etaMinutes(distanceKm) {
  return Math.round((DISPATCH_DELAY_MIN + (distanceKm / AVG_SPEED_KMPH) * 60) * 10) / 10;
}
