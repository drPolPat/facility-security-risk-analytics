import { FACTORS, FACTOR_LABELS, FLAGS, FLAG_LABELS } from "../theme";

export default function WhatIfControls({
  factors,
  flags,
  onFactorChange,
  onFlagChange,
  onRecalculate,
  onReset,
  dirty,
  recalculating,
}) {
  return (
    <div className="rounded-lg border border-[#232b3b] bg-[#141922] p-4">
      <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-[#7b8798]">
        What-if — edit factors &amp; countermeasures
      </div>

      <div className="mb-4 space-y-3">
        {FACTORS.map((factor) => (
          <label key={factor} className="block text-xs">
            <div className="mb-1 flex items-center justify-between text-[#c7d0dd]">
              <span>{FACTOR_LABELS[factor]}</span>
              <span className="font-mono font-semibold text-[#e2e8f0]">
                {factors[factor].toFixed(1)}
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="5"
              step="0.1"
              value={factors[factor]}
              onChange={(e) => onFactorChange(factor, Number(e.target.value))}
              className="w-full accent-[#38bdf8]"
            />
          </label>
        ))}
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        {FLAGS.map((flag) => (
          <label
            key={flag}
            className="flex cursor-pointer items-center gap-1.5 rounded-md border border-[#232b3b] bg-[#0b0e14] px-2 py-1 text-xs text-[#c7d0dd]"
          >
            <input
              type="checkbox"
              checked={flags[flag]}
              onChange={(e) => onFlagChange(flag, e.target.checked)}
              className="accent-[#38bdf8]"
            />
            {FLAG_LABELS[flag]}
          </label>
        ))}
      </div>

      <div className="flex gap-2">
        <button
          onClick={onRecalculate}
          disabled={recalculating}
          className="rounded-md border border-[#38bdf8] bg-[#0f1a22] px-3 py-1.5 text-xs font-semibold text-[#38bdf8] transition-colors hover:bg-[#132330] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {recalculating ? "Recalculating…" : "Recalculate"}
        </button>
        <button
          onClick={onReset}
          disabled={!dirty}
          className="rounded-md border border-[#232b3b] bg-[#0b0e14] px-3 py-1.5 text-xs font-semibold text-[#7b8798] transition-colors hover:text-[#c7d0dd] disabled:cursor-not-allowed disabled:opacity-40"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
