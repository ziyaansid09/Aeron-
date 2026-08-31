import { Building2 } from "lucide-react";
import Panel from "../components/Panel";
import HospitalCard from "../components/HospitalCard";
import Tag from "../components/Tag";
import { usePoll } from "../lib/usePoll";
import { api } from "../lib/api";

async function loadData() {
  const [hospitals, doctors] = await Promise.all([api.listHospitals(), api.listDoctors()]);
  return { hospitals: hospitals.hospitals, doctors: doctors.doctors };
}

export default function HospitalDashboard() {
  const { data, loading, refetch } = usePoll(loadData, { intervalMs: 8000 });

  async function handleUpdate(hospitalId, draft) {
    await api.updateHospitalStatus(hospitalId, draft);
    refetch();
  }

  const hospitals = data?.hospitals ?? [];
  const doctors = data?.doctors ?? [];

  return (
    <div className="flex flex-col gap-5">
      <header className="flex items-center gap-2.5">
        <h1 className="font-display text-2xl font-semibold text-console-text">Hospital Network</h1>
        <Tag variant="simulated">Simulated operational data</Tag>
      </header>

      <Panel
        title={`${hospitals.length} hospitals in network`}
        action={<Building2 size={16} className="text-console-muted" />}
      >
        {loading && !data ? (
          <p className="text-sm text-console-muted">Loading hospital network…</p>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            {hospitals.map((h) => (
              <HospitalCard key={h.hospital_id} hospital={h} doctors={doctors} onUpdate={handleUpdate} />
            ))}
          </div>
        )}
      </Panel>
    </div>
  );
}
