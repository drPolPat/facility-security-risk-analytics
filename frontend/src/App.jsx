import { useCallback, useEffect, useRef, useState } from "react";
import { getFacilities, getShapSummary } from "./api";
import FacilityList from "./components/FacilityList";
import FacilityDetail from "./components/FacilityDetail";
import ArchetypeComparison from "./components/ArchetypeComparison";

const VIEWS = { LIST: "list", DETAIL: "detail", ARCHETYPES: "archetypes" };

export default function App() {
  const [view, setView] = useState(VIEWS.LIST);
  const [selectedId, setSelectedId] = useState(null);

  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [shapSummary, setShapSummary] = useState(null);
  const didInit = useRef(false);

  const loadFacilities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetched once, unfiltered: the dataset is small (300 rows), so both
      // the facility list and the archetype comparison view filter/aggregate
      // this same list client-side rather than round-tripping per filter
      // change. GET /api/facilities?archetype= is still exercised directly
      // if you query it outside the UI (see the README).
      const data = await getFacilities();
      setFacilities(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (didInit.current) return; // survive StrictMode's double-mount in dev
    didInit.current = true;
    loadFacilities();
    getShapSummary()
      .then(setShapSummary)
      .catch(() => {});
  }, [loadFacilities]);

  function openFacility(id) {
    setSelectedId(id);
    setView(VIEWS.DETAIL);
  }

  function backToList() {
    setView(VIEWS.LIST);
    setSelectedId(null);
  }

  return (
    <div className="min-h-screen bg-[#0b0e14] text-[#c7d0dd]">
      <div className="mx-auto max-w-[1200px] px-6 py-5">
        <header className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold tracking-tight text-[#e2e8f0]">
              facility-security-risk-analytics
            </h1>
            <p className="text-xs text-[#7b8798]">
              Weighted physical-security risk model across synthetic facility archetypes. All
              data synthetic.
            </p>
          </div>
          <nav className="flex gap-2 text-xs">
            <TabButton active={view !== VIEWS.ARCHETYPES} onClick={backToList}>
              Facilities
            </TabButton>
            <TabButton
              active={view === VIEWS.ARCHETYPES}
              onClick={() => setView(VIEWS.ARCHETYPES)}
            >
              Archetypes
            </TabButton>
          </nav>
        </header>

        {error && (
          <div className="mb-4 rounded-lg border border-[#5a3030] bg-[#1c1212] p-4 text-sm">
            <div className="mb-1 font-semibold text-[#f87171]">Could not load facilities</div>
            <div className="text-[#c7d0dd]">{error}</div>
            <div className="mt-2 text-xs text-[#7b8798]">
              Is the backend running?{" "}
              <code className="text-[#c7d0dd]">cd backend && uv run uvicorn app.main:app</code>
            </div>
          </div>
        )}

        {!error && view === VIEWS.ARCHETYPES && <ArchetypeComparison facilities={facilities} />}

        {!error && view === VIEWS.LIST && (
          <FacilityList facilities={facilities} loading={loading} onSelect={openFacility} />
        )}

        {!error && view === VIEWS.DETAIL && selectedId && (
          <FacilityDetail facilityId={selectedId} shapSummary={shapSummary} onBack={backToList} />
        )}
      </div>
    </div>
  );
}

function TabButton({ active, onClick, children }) {
  return (
    <button
      onClick={onClick}
      className={`rounded-md border px-3 py-1.5 font-semibold transition-colors ${
        active
          ? "border-[#38bdf8] bg-[#0f1a22] text-[#38bdf8]"
          : "border-[#232b3b] bg-[#141922] text-[#7b8798] hover:text-[#c7d0dd]"
      }`}
    >
      {children}
    </button>
  );
}
