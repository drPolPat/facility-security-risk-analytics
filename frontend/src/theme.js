export const C = {
  bg: "#0b0e14",
  panel: "#141922",
  border: "#232b3b",
  text: "#e2e8f0",
  textDim: "#c7d0dd",
  muted: "#7b8798",
  accent: "#38bdf8",
  danger: "#ef4444",
  good: "#4ade80",
  ridge: "#38bdf8",
  gbm: "#f472b6",
};

export const ARCHETYPES = [
  { key: "cultural_heritage_site", label: "Cultural / Heritage Site", color: "#f472b6" },
  { key: "commercial_retail_complex", label: "Commercial Retail Complex", color: "#fb923c" },
  { key: "mixed_use_tower", label: "Mixed-Use Tower", color: "#38bdf8" },
  { key: "critical_infrastructure", label: "Critical Infrastructure", color: "#a78bfa" },
];

export const ARCHETYPE_COLORS = Object.fromEntries(ARCHETYPES.map((a) => [a.key, a.color]));
export const ARCHETYPE_LABELS = Object.fromEntries(ARCHETYPES.map((a) => [a.key, a.label]));

export const FACTOR_LABELS = {
  asset_criticality: "Asset criticality",
  public_accessibility: "Public accessibility",
  perimeter_vulnerability: "Perimeter vulnerability",
  threat_exposure: "Threat exposure",
  existing_countermeasures: "Existing countermeasures",
  site_complexity: "Site complexity",
  response_readiness: "Response readiness",
};

export const FACTORS = Object.keys(FACTOR_LABELS);

export const FLAG_LABELS = {
  cameras: "Cameras",
  access_control: "Access control",
  guards: "Guards",
  lighting: "Lighting",
  fencing: "Fencing",
};

export const FLAGS = Object.keys(FLAG_LABELS);

export function featureLabel(key) {
  return FACTOR_LABELS[key] ?? FLAG_LABELS[key] ?? key;
}
