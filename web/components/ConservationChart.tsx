"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { AnalysisData } from "@/lib/types";

export function ConservationChart({ data }: { data: AnalysisData }) {
  const chartData = data.conservation;
  const { conserved, variable } = data.thresholds;

  return (
    <div className="h-[320px] md:h-[380px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#34d399" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#34d399" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
          <XAxis
            dataKey="position"
            tick={{ fill: "#8b9cb8", fontSize: 11 }}
            tickLine={false}
            label={{
              value: "Alignment position",
              position: "insideBottom",
              offset: -4,
              fill: "#8b9cb8",
              fontSize: 12,
            }}
          />
          <YAxis
            domain={[0, 1.05]}
            tick={{ fill: "#8b9cb8", fontSize: 11 }}
            tickLine={false}
            label={{
              value: "Conservation score",
              angle: -90,
              position: "insideLeft",
              fill: "#8b9cb8",
              fontSize: 12,
            }}
          />
          <Tooltip
            contentStyle={{
              background: "#152238",
              border: "1px solid #243049",
              borderRadius: "12px",
              fontSize: "12px",
            }}
            labelFormatter={(p) => `Position ${p}`}
            formatter={(v: number) => [v.toFixed(3), "Score"]}
          />
          <ReferenceLine
            y={conserved}
            stroke="#34d399"
            strokeDasharray="4 4"
            label={{ value: "Conserved ≥0.85", fill: "#34d399", fontSize: 10 }}
          />
          <ReferenceLine
            y={variable}
            stroke="#fb7185"
            strokeDasharray="4 4"
            label={{ value: "Variable ≤0.5", fill: "#fb7185", fontSize: 10 }}
          />
          <Area
            type="monotone"
            dataKey="score"
            stroke="#38bdf8"
            strokeWidth={1.5}
            fill="url(#scoreGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
