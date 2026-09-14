import { useCallback, useEffect, useState } from "react";
import { getFacility, whatIf } from "../api";
import { ARCHETYPE_COLORS, FACTORS, FLAGS } from "../theme";
import RiskRadarChart from "./RiskRadarChart";
import WhatIfControls from "./WhatIfControls";
import ModelComparisonPanel from "./ModelComparisonPanel";
import FeatureImportancePanel from "./FeatureImportancePanel";

const EPS = 0.05; // slider step is 0.1; guards against float-compare noise

function pickFactors(source) {
  return Object.fromEntries(FACTORS.map((f) => [f, source[f]]));
}

function pickFlags(source) {
  return Object.fromEntries(FLAGS.map((f) => [f, source[f]]));
}

function diffOverrides(edited, original, keys, eps = 0) {
  const out = {};
  for (const key of keys) {
    const changed = eps ? Math.abs(edited[key] - original[key]) > eps : edited[key] !== original[key];
    if (changed) out[key] = edited[key];
  }
  return out;
}

export default function FacilityDetail({ facilityId, shapSummary, onBack }) {
  const [facility, setFacility] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [editedFactors, setEditedFactors] = useState(null);
  const [editedFlags, setEditedFlags] = useState(null);

  const [whatIfResult, setWhatIfResult] = useState(null);
  const [recalculating, setRecalculating] = useState(false);
  const [recalcError, setRecalcError] = useState(null);

  const runWhatIf = useCallback(
    async (factorOverrides, flagOverrides) => {
      setRecalculating(true);
      setRecalcError(null);
      try {
        const result = await whatIf(facilityId, { factors: factorOverrides, flags: flagOverrides });
        setWhatIfResult(result);
      } catch (e) {
        setRecalcError(e.message);
      } finally {
        setRecalculating(false);
      }
    },
    [facilityId],
  );

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setFacility(null);
    setWhatIfResult(null);

    getFacility(facilityId)
      .then((f) => {
        if (cancelled) return;
        setFacility(f);
        setEditedFactors(pickFactors(f));
        setEditedFlags(pickFlags(f));
        // Seed the headline/model-comparison panels with the original
        // facility's model predictions (empty override -> before === after)
        // so they show real numbers before any edit is made.
        runWhatIf({}, {});
      })
      .catch((e) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [facilityId, runWhatIf]);

  if (loading || !facility || !editedFactors || !editedFlags) {
    return (
      <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4 text-sm text-[#7b8798]">
        {error ? <span className="text-[#f87171]">{error}</span> : "Loading facility…"}
      </div>
    );
  }

  const dirty =
    FACTORS.some((f) => Math.abs(editedFactors[f] - facility[f]) > EPS) ||
    FLAGS.some((f) => editedFlags[f] !== facility[f]);

  function handleRecalculate() {
    runWhatIf(
      diffOverrides(editedFactors, pickFactors(facility), FACTORS, EPS),
      diffOverrides(editedFlags, pickFlags(facility), FLAGS),
    );
  }

  function handleReset() {
    setEditedFactors(pickFactors(facility));
    setEditedFlags(pickFlags(facility));
    runWhatIf({}, {});
  }

  const headlineChanged = whatIfResult && Math.abs(whatIfResult.delta.risk_score) > 0.005;
  const headlineScore = whatIfResult ? whatIfResult.after.risk_score : facility.risk_score;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="text-xs text-[#7b8798] hover:text-[#c7d0dd]">
          ← Back to facilities
        </button>
      </div>

      <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-5">
        <div className="mb-2 flex items-center gap-2 text-xs text-[#7b8798]">
          <span
            className="inline-block h-2 w-2 rounded-full"
            style={{ background: ARCHETYPE_COLORS[facility.archetype] }}
          />
          {facility.archetype_label}
          <span className="font-mono">{facility.facility_id}</span>
        </div>

        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold text-[#e2e8f0]">{headlineScore.toFixed(1)}</span>
          <span className="text-sm text-[#7b8798]">risk score / 100</span>
          {headlineChanged && (
            <span className="text-sm">
              <span className="text-[#7b8798] line-through decoration-[#3a4356]">
                {whatIfResult.before.risk_score.toFixed(1)}
              </span>{" "}
              <span
                className={whatIfResult.delta.risk_score < 0 ? "text-[#4ade80]" : "text-[#f87171]"}
              >
                ({whatIfResult.delta.risk_score > 0 ? "+" : ""}
                {whatIfResult.delta.risk_score.toFixed(1)})
              </span>
            </span>
          )}
        </div>

        {recalcError && <div className="mt-2 text-xs text-[#f87171]">{recalcError}</div>}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
            <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
              Factor profile
            </div>
            <p className="mb-2 text-[11px] text-[#7b8798]">
              Raw 1-5 scores, as-scored (existing countermeasures: higher = stronger, not
              risk-inverted here — same convention as the EDA notebook&apos;s radar charts).
            </p>
            <RiskRadarChart original={pickFactors(facility)} edited={editedFactors} />
          </div>

          <WhatIfControls
            factors={editedFactors}
            flags={editedFlags}
            onFactorChange={(factor, value) =>
              setEditedFactors((prev) => ({ ...prev, [factor]: value }))
            }
            onFlagChange={(flag, value) => setEditedFlags((prev) => ({ ...prev, [flag]: value }))}
            onRecalculate={handleRecalculate}
            onReset={handleReset}
            dirty={dirty}
            recalculating={recalculating}
          />
        </div>

        <div className="space-y-4">
          <ModelComparisonPanel result={whatIfResult} />
          <FeatureImportancePanel shapSummary={shapSummary} />
        </div>
      </div>
    </div>
  );
}
