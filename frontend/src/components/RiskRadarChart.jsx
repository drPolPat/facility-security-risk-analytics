import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { FACTORS, FACTOR_LABELS, C } from "../theme";

/** Two overlaid series: the facility's stored profile and the live-edited
 * what-if profile, both on the raw 1-5 scale (as-scored, not risk-inverted —
 * same convention as the EDA notebook's radar charts). */
export default function RiskRadarChart({ original, edited }) {
  const data = FACTORS.map((factor) => ({
    factor: FACTOR_LABELS[factor],
    original: original[factor],
    edited: edited[factor],
  }));

  return (
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data} outerRadius="70%">
        <PolarGrid stroke={C.border} />
        <PolarAngleAxis dataKey="factor" tick={{ fill: C.muted, fontSize: 10 }} />
        <PolarRadiusAxis angle={90} domain={[0, 5]} tick={{ fill: C.muted, fontSize: 9 }} />
        <Radar
          name="Original"
          dataKey="original"
          stroke={C.muted}
          fill={C.muted}
          fillOpacity={0.12}
          strokeDasharray="4 3"
        />
        <Radar name="Current (edited)" dataKey="edited" stroke={C.accent} fill={C.accent} fillOpacity={0.25} />
        <Legend wrapperStyle={{ fontSize: 11, color: C.muted }} />
        <Tooltip
          contentStyle={{ background: C.panel, border: `1px solid ${C.border}`, fontSize: 11 }}
          labelStyle={{ color: C.text }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
