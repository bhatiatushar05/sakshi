import type { Region } from "@/lib/types";
import { TrendingDown, TrendingUp } from "lucide-react";

export function RegionsTable({
  title,
  regions,
  variant,
  note,
}: {
  title: string;
  regions: Region[];
  variant: "conserved" | "variable";
  note?: string;
}) {
  const accent = variant === "conserved" ? "mint" : "coral";
  const Icon = variant === "conserved" ? TrendingUp : TrendingDown;

  return (
    <div className="glass rounded-2xl p-5 md:p-6 h-full">
      <div className="flex items-center gap-2 mb-4">
        <Icon className={`h-5 w-5 text-${accent}`} style={{ color: variant === "conserved" ? "#34d399" : "#fb7185" }} />
        <h3 className="font-semibold text-white">{title}</h3>
      </div>
      {note && (
        <p className="text-xs text-muted mb-4 leading-relaxed border-l-2 border-sky/40 pl-3">
          {note}
        </p>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-muted border-b border-border">
              <th className="pb-2 pr-4 font-medium">Position</th>
              <th className="pb-2 pr-4 font-medium">Length</th>
              <th className="pb-2 pr-4 font-medium">Score</th>
              <th className="pb-2 font-medium">Gene</th>
            </tr>
          </thead>
          <tbody>
            {regions.map((r) => (
              <tr key={`${r.start}-${r.end}`} className="border-b border-border/50">
                <td className="py-3 pr-4 font-mono text-white">
                  {r.start}–{r.end}
                </td>
                <td className="py-3 pr-4 text-muted">{r.length} nt</td>
                <td className="py-3 pr-4">
                  <span
                    className="font-mono px-2 py-0.5 rounded text-xs"
                    style={{
                      background:
                        variant === "conserved"
                          ? "rgba(52,211,153,0.15)"
                          : "rgba(251,113,133,0.15)",
                      color: variant === "conserved" ? "#34d399" : "#fb7185",
                    }}
                  >
                    {r.mean_score.toFixed(3)}
                  </span>
                </td>
                <td className="py-3 text-sky capitalize">{r.gene}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
