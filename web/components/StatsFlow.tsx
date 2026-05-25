"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import type { AnalysisData } from "@/lib/types";

export function StatsFlow({ data }: { data: AnalysisData }) {
  const s = data.stats;
  const removed =
    s.removedShort + s.removedAmbiguous + s.removedDuplicate;

  const steps = [
    { label: "Fetched", value: s.fetched, color: "#38bdf8" },
    { label: "QC passed", value: s.finalCleaned, color: "#34d399" },
    {
      label: "Aligned",
      value: `${s.alignmentSequences}×${s.alignmentLength}`,
      color: "#a78bfa",
    },
  ];

  return (
    <section className="py-12 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="glass rounded-2xl p-6 md:p-8">
        <p className="text-sm text-muted mb-6 text-center">
          Data flow through the pipeline
          {removed > 0 && (
            <span className="text-coral"> · {removed} sequences removed at QC</span>
          )}
          {removed === 0 && (
            <span className="text-mint"> · all sequences passed quality filters</span>
          )}
        </p>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-2">
          {steps.map((step, i) => (
            <div key={step.label} className="flex items-center gap-4 md:gap-2">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                whileInView={{ scale: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center min-w-[120px]"
              >
                <p
                  className="text-3xl md:text-4xl font-bold"
                  style={{ color: step.color }}
                >
                  {step.value}
                </p>
                <p className="text-sm text-muted mt-1">{step.label}</p>
              </motion.div>
              {i < steps.length - 1 && (
                <ArrowRight className="h-6 w-6 text-border hidden md:block" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
