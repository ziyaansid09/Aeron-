// Single place that knows how to talk to the AERON backend.
// Dev: Vite proxies /api/* -> http://localhost:8000 (see vite.config.js).
// Prod: set VITE_API_BASE_URL to your deployed backend's URL (see .env.example).
const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(
      "Can't reach the AERON backend. Is it running on port 8000?",
      0
    );
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* response wasn't JSON — keep statusText */
    }
    throw new ApiError(
      typeof detail === "string" ? detail : JSON.stringify(detail),
      res.status
    );
  }
  if (res.status === 204) return null;
  return res.json();
}

const qs = (params = {}) => {
  const clean = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
  const s = new URLSearchParams(clean).toString();
  return s ? `?${s}` : "";
};

export const api = {
  health: () => request("/health"),

  listHospitals: () => request("/hospitals"),
  getHospital: (id) => request(`/hospitals/${id}`),
  updateHospitalStatus: (id, patch) =>
    request(`/hospitals/${id}/status`, { method: "PATCH", body: JSON.stringify(patch) }),

  listDoctors: (hospitalId) => request(`/doctors${qs({ hospital_id: hospitalId })}`),

  listAmbulances: (status) => request(`/ambulances${qs({ status })}`),
  getAmbulance: (id) => request(`/ambulances/${id}`),

  listBloodBanks: () => request("/blood-banks"),
  bloodAvailability: (params) => request(`/blood/availability${qs(params)}`),

  analyzeEmergency: (payload) =>
    request("/emergency/analyze", { method: "POST", body: JSON.stringify(payload) }),
  confirmDestination: (emergencyId, payload = {}) =>
    request(`/emergency/${emergencyId}/confirm`, { method: "POST", body: JSON.stringify(payload) }),
  listEmergencies: (limit) => request(`/emergency${qs({ limit })}`),
  getEmergency: (id) => request(`/emergency/${id}`),

  simulateMassCasualty: (payload) =>
    request("/mass-casualty/simulate", { method: "POST", body: JSON.stringify(payload) }),
  listCasualtyEvents: (limit) => request(`/mass-casualty/events${qs({ limit })}`),
};
