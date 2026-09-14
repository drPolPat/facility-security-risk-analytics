import { useEffect, useMemo, useRef } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ARCHETYPES, C } from "../theme";

/** Mean risk_score per archetype, computed client-side from the already-
 * fetched facility list (same aggregation as the EDA notebook's archetype
 * table). Always over the full unfiltered dataset. */
export default function ArchetypeComparison({ facilities }) {
  const data = useMemo(() => {
    return ARCHETYPES.map(({ key, label, color }) => {
      const rows = facilities.filter((f) => f.archetype === key);
      const mean = rows.length
        ? rows.reduce((sum, f) => sum + f.risk_score, 0) / rows.length
        : 0;
      return { key, label, color, mean_risk_score: mean, n: rows.length };
    });
  }, [facilities]);

  // This view mounts synchronously on a tab click (unlike the facility-detail
  // charts, which mount only after an async fetch resolves and layout has
  // long settled). Recharts' ResponsiveContainer measures its container via
  // ResizeObserver on mount, and that first callback can land before layout
  // has actually settled, leaving the chart at a stale/zero size forever --
  // nothing re-triggers ResizeObserver afterwards since the container's size
  // never subsequently changes. Toggling the width by a fraction of a pixel
  // forces one genuine layout change, which reliably re-fires it with a
  // correct measurement. A synthetic `window resize` event does NOT work
  // here: ResizeObserver only reacts to the observed element's box actually
  // changing, not to a resize event with no real dimension change behind it.
  const containerRef = useRef(null);
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return undefined;
    el.style.width = "99.9%";
    const id = setTimeout(() => {
      el.style.width = "100%";
    }, 50);
    return () => clearTimeout(id);
  }, []);

  if (facilities.length === 0) {
    return (
      <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4 text-xs text-[#7b8798]">
        Loading facilities…
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
        Mean risk score by archetype
      </div>
      <p className="mb-2 text-[11px] text-[#7b8798]">
        Aggregated over all {facilities.length} synthetic facilities currently loaded.
      </p>
      <div ref={containerRef} style={{ width: "100%", height: 280 }}>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data} layout="vertical" margin={{ left: 24, right: 12 }}>
            <CartesianGrid stroke={C.border} horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: C.muted, fontSize: 10 }} />
            <YAxis
              type="category"
              dataKey="label"
              width={140}
              tick={{ fill: C.textDim, fontSize: 10 }}
            />
            <Tooltip
              contentStyle={{ background: C.panel, border: `1px solid ${C.border}`, fontSize: 11 }}
              labelStyle={{ color: C.text }}
              formatter={(value) => value.toFixed(1)}
            />
            <Bar dataKey="mean_risk_score" radius={[0, 3, 3, 0]}>
              {data.map((d) => (
                <Cell key={d.key} fill={d.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
