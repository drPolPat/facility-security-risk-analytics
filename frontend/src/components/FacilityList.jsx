import { useMemo, useState } from "react";
import { ARCHETYPES, ARCHETYPE_COLORS } from "../theme";

const ARCHETYPE_OPTIONS = [{ key: "", label: "All archetypes" }, ...ARCHETYPES];

export default function FacilityList({ facilities, loading, onSelect }) {
  const [archetype, setArchetype] = useState("");
  const [sortKey, setSortKey] = useState("risk_score");
  const [sortDir, setSortDir] = useState("desc");

  const rows = useMemo(() => {
    const filtered = archetype ? facilities.filter((f) => f.archetype === archetype) : facilities;
    const sign = sortDir === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) => sign * (a[sortKey] - b[sortKey]));
  }, [facilities, archetype, sortKey, sortDir]);

  function toggleSort(key) {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  }

  return (
    <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
          Facilities {loading ? "· loading…" : `· ${rows.length}`}
        </div>
        <select
          value={archetype}
          onChange={(e) => setArchetype(e.target.value)}
          className="rounded-md border border-[#232b3b] bg-[#0b0e14] px-2 py-1 text-xs text-[#c7d0dd]"
        >
          {ARCHETYPE_OPTIONS.map((a) => (
            <option key={a.key} value={a.key}>
              {a.label}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-[#7b8798]">
              <th className="pb-2 font-medium">Facility</th>
              <th className="pb-2 font-medium">Archetype</th>
              <SortableTh
                label="Risk score"
                sortKey="risk_score"
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
              />
              <SortableTh
                label="Incident likelihood"
                sortKey="incident_likelihood"
                activeKey={sortKey}
                dir={sortDir}
                onSort={toggleSort}
              />
            </tr>
          </thead>
          <tbody>
            {rows.map((f) => (
              <tr
                key={f.facility_id}
                onClick={() => onSelect(f.facility_id)}
                className="cursor-pointer border-t border-[#232b3b] hover:bg-[#1a2030]"
              >
                <td className="py-1.5 font-mono">{f.facility_id}</td>
                <td className="py-1.5">
                  <span
                    className="mr-1.5 inline-block h-2 w-2 rounded-full align-middle"
                    style={{ background: ARCHETYPE_COLORS[f.archetype] }}
                  />
                  {f.archetype_label}
                </td>
                <td className="py-1.5 font-semibold text-[#e2e8f0]">{f.risk_score.toFixed(1)}</td>
                <td className="py-1.5">{f.incident_likelihood.toFixed(1)}</td>
              </tr>
            ))}
            {rows.length === 0 && !loading && (
              <tr>
                <td colSpan={4} className="py-4 text-center text-[#7b8798]">
                  No facilities match this filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SortableTh({ label, sortKey, activeKey, dir, onSort }) {
  const active = sortKey === activeKey;
  return (
    <th className="cursor-pointer select-none pb-2 font-medium" onClick={() => onSort(sortKey)}>
      {label} {active ? (dir === "asc" ? "▲" : "▼") : ""}
    </th>
  );
}
