import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { C, featureLabel } from "../theme";

/** Precomputed SHAP feature importance from the EDA notebook (GET
 * /api/shap-summary) — not recomputed live. */
export default function FeatureImportancePanel({ shapSummary }) {
  if (!shapSummary) {
    return (
      <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4 text-xs text-[#7b8798]">
        Loading feature importance…
      </div>
    );
  }

  const data = [...shapSummary.features]
    .sort((a, b) => a.mean_abs_shap - b.mean_abs_shap)
    .map((f) => ({ feature: featureLabel(f.feature), value: f.mean_abs_shap }));

  return (
    <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
        Top risk-driving factors (SHAP)
      </div>
      <p className="mb-2 text-[11px] text-[#7b8798]">
        Mean |SHAP value| from the {shapSummary.model.toUpperCase()} model, n={shapSummary.n_samples}.
        Precomputed in the EDA notebook.
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical" margin={{ left: 24, right: 12 }}>
          <CartesianGrid stroke={C.border} horizontal={false} />
          <XAxis type="number" tick={{ fill: C.muted, fontSize: 10 }} />
          <YAxis
            type="category"
            dataKey="feature"
            width={140}
            tick={{ fill: C.textDim, fontSize: 10 }}
          />
          <Tooltip
            contentStyle={{ background: C.panel, border: `1px solid ${C.border}`, fontSize: 11 }}
            labelStyle={{ color: C.text }}
            formatter={(value) => value.toFixed(3)}
          />
          <Bar dataKey="value" radius={[0, 3, 3, 0]}>
            {data.map((d) => (
              <Cell key={d.feature} fill={C.accent} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
