import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import { hospitalIcon, ambulanceIcon, emergencyIcon } from "../lib/mapIcons";

const MUMBAI_CENTER = [19.076, 72.8777];

function FitBounds({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length > 1) {
      map.fitBounds(points, { padding: [40, 40] });
    }
  }, [map, points]);
  return null;
}

export default function AmbulanceMap({ hospitals, ambulances, selected, emergency }) {
  const routePoints =
    selected?.target_hospital_id && emergency
      ? [
          [selected.lat, selected.lng],
          [emergency.lat, emergency.lng],
        ]
      : selected?.target_hospital_id
      ? (() => {
          const dest = hospitals.find((h) => h.hospital_id === selected.target_hospital_id);
          return dest ? [[selected.lat, selected.lng], [dest.lat, dest.lng]] : [];
        })()
      : [];

  const fitPoints = routePoints.length ? routePoints : null;

  return (
    <MapContainer center={MUMBAI_CENTER} zoom={11} scrollWheelZoom className="h-full w-full rounded-xl">
      <TileLayer
        className="aeron-map-tiles"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {fitPoints && <FitBounds points={fitPoints} />}

      {hospitals.map((h) => (
        <Marker key={h.hospital_id} position={[h.lat, h.lng]} icon={hospitalIcon(h.hospital_id === selected?.target_hospital_id)}>
          <Popup>
            <b>{h.name}</b>
            <br />
            ICU {h.icu_beds_available}/{h.icu_beds_total} · Load {h.emergency_load_pct}%
          </Popup>
        </Marker>
      ))}

      {ambulances.map((a) => (
        <Marker key={a.ambulance_id} position={[a.lat, a.lng]} icon={ambulanceIcon(a.status)}>
          <Popup>
            <b>{a.ambulance_id}</b> · {a.type}
            <br />
            {a.crew}
            <br />
            Status: {a.status}
          </Popup>
        </Marker>
      ))}

      {emergency && (
        <Marker position={[emergency.lat, emergency.lng]} icon={emergencyIcon()}>
          <Popup>
            <b>Emergency {emergency.emergency_id}</b>
            <br />
            {emergency.location_label}
          </Popup>
        </Marker>
      )}

      {routePoints.length === 2 && (
        <Polyline
          positions={routePoints}
          pathOptions={{ color: "var(--color-accent)", weight: 3, dashArray: "6 8" }}
        />
      )}
    </MapContainer>
  );
}
