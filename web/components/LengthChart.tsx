"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { AnalysisData } from "@/lib/types";

export function LengthChart({ data }: { data: AnalysisData }) {
  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data.lengthDistribution}
          margin={{ top: 8, right: 8, left: 0, bottom: 40 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#243049" vertical={false} />
          <XAxis
            dataKey="range"
            tick={{ fill: "#8b9cb8", fontSize: 10 }}
            angle={-35}
            textAnchor="end"
            height={56}
          />
          <YAxis tick={{ fill: "#8b9cb8", fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{
              background: "#152238",
              border: "1px solid #243049",
              borderRadius: "12px",
            }}
          />
          <Bar dataKey="count" fill="#a78bfa" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
      <p className="text-center text-xs text-muted mt-2">
        Range {data.lengthStats.min}–{data.lengthStats.mean}–{data.lengthStats.max} nt
        (mean {data.lengthStats.mean} nt)
      </p>
    </div>
  );
}
