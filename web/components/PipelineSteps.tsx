"use client";

import { motion } from "framer-motion";
import {
  Download,
  Filter,
  AlignHorizontalJustifyCenter,
  BarChart3,
  Image,
  FileText,
  CheckCircle2,
} from "lucide-react";
import type { AnalysisData } from "@/lib/types";

const STEPS = [
  {
    id: 1,
    title: "Sequence fetching",
    desc: "Biopython Entrez — HIV-1 subtype C from India via NCBI GenBank",
    icon: Download,
    stat: (d: AnalysisData) => `${d.stats.fetched} raw sequences`,
  },
  {
    id: 2,
    title: "Cleaning & QC",
    desc: "Remove short, ambiguous (>5% N/R/Y), and duplicate records; standardize headers",
    icon: Filter,
    stat: (d: AnalysisData) =>
      `${d.stats.finalCleaned} passed (${d.stats.fetched - d.stats.finalCleaned} removed)`,
  },
  {
    id: 3,
    title: "Multiple alignment",
    desc: "MAFFT global alignment on cleaned FASTA",
    icon: AlignHorizontalJustifyCenter,
    stat: (d: AnalysisData) =>
      `${d.stats.alignmentSequences} seq × ${d.stats.alignmentLength} columns`,
  },
  {
    id: 4,
    title: "Conservation analysis",
    desc: "Per-column conservation score; conserved (≥0.85) vs variable (≤0.5) regions",
    icon: BarChart3,
    stat: (d: AnalysisData) =>
      `${d.conservedRegions.length} top conserved blocks identified`,
  },
  {
    id: 5,
    title: "Visualisation",
    desc: "Conservation plot with shaded regions + length distribution histogram",
    icon: Image,
    stat: () => "PNG exports ready",
  },
  {
    id: 6,
    title: "Report",
    desc: "Markdown summary with gene context (gag, pol, env)",
    icon: FileText,
    stat: () => "Presentation-ready summary",
  },
];

export function PipelineSteps({ data }: { data: AnalysisData }) {
  return (
    <section id="pipeline" className="py-20 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="mb-12">
        <h2 className="section-title">Analysis pipeline</h2>
        <p className="section-sub mt-2">
          Six modular steps — from GenBank download to publication-style figures. The
          exported run is shown here; rerun these steps in local Streamlit mode.
        </p>
      </div>

      <div className="relative">
        <div className="absolute left-6 md:left-8 top-8 bottom-8 w-px bg-gradient-to-b from-mint/50 via-sky/30 to-transparent hidden md:block" />

        <div className="space-y-4">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -12 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: i * 0.06 }}
              className="glass rounded-2xl p-5 md:p-6 flex gap-4 md:gap-6 items-start md:ml-0"
            >
              <div className="flex-shrink-0 flex flex-col items-center gap-2">
                <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-mint/15 text-mint ring-1 ring-mint/25">
                  <step.icon className="h-5 w-5" />
                </span>
                <CheckCircle2 className="h-4 w-4 text-mint" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <span className="font-mono text-xs text-sky">Step {step.id}</span>
                  <h3 className="font-semibold text-white text-lg">{step.title}</h3>
                </div>
                <p className="text-sm text-muted leading-relaxed">{step.desc}</p>
                <p className="mt-2 font-mono text-xs text-mint/90 bg-mint/5 inline-block px-2 py-1 rounded">
                  {step.stat(data)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
