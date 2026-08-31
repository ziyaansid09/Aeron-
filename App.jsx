import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ControlCentre from "./pages/ControlCentre";
import HospitalDashboard from "./pages/HospitalDashboard";
import AmbulanceDashboard from "./pages/AmbulanceDashboard";
import BloodModule from "./pages/BloodModule";
import MassCasualty from "./pages/MassCasualty";

export default function App() {
  return (
    <div className="flex min-h-screen bg-console-bg text-console-text">
      <Navbar />
      <main className="flex-1 overflow-y-auto px-5 py-6 lg:px-7">
        <div className="mx-auto max-w-[1500px]">
          <Routes>
            <Route path="/" element={<ControlCentre />} />
            <Route path="/hospitals" element={<HospitalDashboard />} />
            <Route path="/ambulances" element={<AmbulanceDashboard />} />
            <Route path="/blood" element={<BloodModule />} />
            <Route path="/mass-casualty" element={<MassCasualty />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
