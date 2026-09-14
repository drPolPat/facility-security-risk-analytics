import { C } from "../theme";

/** Secondary panel, deliberately smaller/less prominent than the headline
 * risk_score: both trained models' predicted incident_likelihood, shown
 * side by side rather than picking a "winner". */
export default function ModelComparisonPanel({ result }) {
  const hasResult = Boolean(result);

  return (
    <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
      <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
        Model comparison
      </div>

      {!hasResult && <div className="text-xs text-[#7b8798]">Loading model predictions…</div>}

      {hasResult && (
        <div className="grid grid-cols-2 gap-3">
          <ModelCard
            label="Ridge (linear)"
            color={C.ridge}
            before={result.before.ridge_incident_likelihood}
            after={result.after.ridge_incident_likelihood}
            delta={result.delta.ridge_incident_likelihood}
          />
          <ModelCard
            label="Gradient Boosting"
            color={C.gbm}
            before={result.before.gbm_incident_likelihood}
            after={result.after.gbm_incident_likelihood}
            delta={result.delta.gbm_incident_likelihood}
          />
        </div>
      )}

      <p className="mt-3 border-t border-[#232b3b] pt-3 text-[11px] leading-snug text-[#7b8798]">
        Ridge fits the overall data better (R²=0.56) but is linear, so it can&apos;t represent the
        threat exposure × existing countermeasures interaction. The shallow GBM trades some
        accuracy (R²=0.46) to capture that interaction — confirmed by SHAP in the EDA notebook.
        Both are shown rather than picking one as &quot;correct.&quot;
      </p>
    </div>
  );
}

function ModelCard({ label, color, before, after, delta }) {
  const changed = Math.abs(delta) > 0.005;
  return (
    <div className="rounded-md border border-[#232b3b] bg-[#0b0e14] p-3">
      <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold" style={{ color }}>
        <span className="inline-block h-2 w-2 rounded-full" style={{ background: color }} />
        {label}
      </div>
      {changed ? (
        <div className="flex items-baseline gap-1.5 text-sm">
          <span className="text-[#7b8798] line-through decoration-[#3a4356]">
            {before.toFixed(1)}
          </span>
          <span className="text-[#c7d0dd]">→</span>
          <span className="font-semibold text-[#e2e8f0]">{after.toFixed(1)}</span>
          <span className={delta < 0 ? "text-[#4ade80]" : "text-[#f87171]"}>
            ({delta > 0 ? "+" : ""}
            {delta.toFixed(1)})
          </span>
        </div>
      ) : (
        <div className="text-sm font-semibold text-[#e2e8f0]">{after.toFixed(1)}</div>
      )}
    </div>
  );
}
