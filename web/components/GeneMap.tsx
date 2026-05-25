"use client";

import type { AnalysisData } from "@/lib/types";
import { motion } from "framer-motion";

const COLORS: Record<string, string> = {
  gag: "#34d399",
  pol: "#38bdf8",
  env: "#fb7185",
};

export function GeneMap({ data }: { data: AnalysisData }) {
  const maxCoord = 9000;

  return (
    <section id="genes" className="py-20 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="mb-10">
        <h2 className="section-title">HIV genome context</h2>
        <p className="section-sub mt-2">
          Approximate HxB2 reference coordinates. Partial genomes in this dataset
          align to overlapping segments — use as interpretive guide for your presentation.
        </p>
      </div>

      <div className="glass rounded-2xl p-6 md:p-8">
        <div className="relative h-16 md:h-20 rounded-xl bg-canvas/80 border border-border overflow-hidden mb-8">
          {data.genes.map((g) => {
            const left = (g.start / maxCoord) * 100;
            const width = ((g.end - g.start) / maxCoord) * 100;
            return (
              <motion.div
                key={g.name}
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                className="absolute top-2 bottom-2 rounded-lg flex items-center justify-center text-xs font-bold uppercase tracking-wider origin-left"
                style={{
                  left: `${left}%`,
                  width: `${width}%`,
                  background: `${COLORS[g.name]}33`,
                  border: `1px solid ${COLORS[g.name]}`,
                  color: COLORS[g.name],
                }}
                title={`${g.name}: ${g.start}–${g.end}`}
              >
                {g.name}
              </motion.div>
            );
          })}
          <div className="absolute bottom-1 left-2 right-2 flex justify-between text-[10px] font-mono text-muted">
            <span>1</span>
            <span>4500</span>
            <span>9000 nt (HxB2)</span>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-4">
          {data.genes.map((g) => (
            <div
              key={g.name}
              className="rounded-xl p-4 border border-border/80"
              style={{ borderColor: `${COLORS[g.name]}44` }}
            >
              <p
                className="text-lg font-bold uppercase"
                style={{ color: COLORS[g.name] }}
              >
                {g.name}
              </p>
              <p className="font-mono text-xs text-muted mt-1">
                nt {g.start.toLocaleString()} – {g.end.toLocaleString()}
              </p>
              <p className="text-sm text-muted mt-2">{g.role}</p>
            </div>
          ))}
        </div>

        <div className="mt-8">
          <p className="text-sm text-muted mb-3">Sample cleaned sequences</p>
          <ul className="grid sm:grid-cols-2 gap-2">
            {data.sampleSequences.map((s) => (
              <li
                key={s.id}
                className="font-mono text-xs bg-canvas/60 rounded-lg px-3 py-2 border border-border truncate"
                title={s.id}
              >
                {s.id}{" "}
                <span className="text-mint">({s.length} nt)</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
