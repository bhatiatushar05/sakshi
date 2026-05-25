"use client";

import { motion } from "framer-motion";
import { ArrowDown, Database, Microscope } from "lucide-react";
import type { AnalysisData } from "@/lib/types";

export function Hero({ data }: { data: AnalysisData }) {
  const { stats, meta } = data;
  const audit = data.datasetAudit;
  const indiaShare =
    audit && audit.rawCount ? Math.round((audit.indiaCount / audit.rawCount) * 100) : null;

  return (
    <section
      id="overview"
      className="relative pt-28 pb-20 md:pt-36 md:pb-28 px-4 md:px-6 max-w-6xl mx-auto"
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <span className="inline-flex items-center gap-2 rounded-full border border-mint/25 bg-mint/10 px-3 py-1 text-xs font-medium text-mint mb-6">
          <Microscope className="h-3.5 w-3.5" />
          Life Sciences · Bioinformatics Project
        </span>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-white max-w-3xl leading-[1.1]">
          HIV-1 Evolution in{" "}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-mint to-sky">
            India
          </span>
        </h1>

        <p className="mt-5 text-lg md:text-xl text-muted max-w-2xl leading-relaxed">
          Shareable in-silico report for <strong className="text-white font-medium">HIV-1 subtype C</strong>{" "}
          sequences returned by the India-focused NCBI query — conservation
          landscapes, quality checks, and mutation-hotspot screening across{" "}
          <strong className="text-white font-medium">{stats.finalCleaned}</strong> GenBank
          sequences.
        </p>

        {audit ? (
          <div className="mt-5 max-w-2xl rounded-2xl border border-amber-300/25 bg-amber-300/10 p-4 text-sm leading-relaxed text-amber-50">
            <strong>Dataset audit:</strong> {audit.indiaCount}/{audit.rawCount} records
            visibly mention India{indiaShare !== null ? ` (${indiaShare}%)` : ""}. This
            page is a shareable report; rerun/filter the pipeline in local interactive mode.
          </div>
        ) : null}

        <div className="mt-8 flex flex-wrap gap-3">
          <a
            href="#results"
            className="inline-flex items-center gap-2 rounded-full bg-mint px-6 py-3 text-sm font-semibold text-canvas hover:opacity-90 transition-opacity"
          >
            Explore results
            <ArrowDown className="h-4 w-4" />
          </a>
          <a
            href="#pipeline"
            className="inline-flex items-center gap-2 rounded-full border border-border px-6 py-3 text-sm font-medium text-white hover:border-sky/50 transition-colors"
          >
            How it works
          </a>
          <a
            href="#run"
            className="inline-flex items-center gap-2 rounded-full border border-mint/30 bg-mint/10 px-6 py-3 text-sm font-medium text-mint hover:border-mint/60 transition-colors"
          >
            Run locally
          </a>
        </div>

        <p className="mt-6 font-mono text-xs text-muted/80 break-all max-w-xl">
          NCBI: {meta.query}
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4"
      >
        {[
          {
            label: "Sequences in report",
            value: stats.finalCleaned,
            icon: Database,
            color: "text-mint",
          },
          {
            label: "Alignment size",
            value: `${stats.alignmentSequences}×${stats.alignmentLength}`,
            icon: DnaIcon,
            color: "text-sky",
          },
          {
            label: "Conserved regions",
            value: data.conservedRegions.length + "+",
            icon: ShieldIcon,
            color: "text-violet",
          },
          {
            label: "India-described",
            value: audit ? `${audit.indiaCount}/${audit.rawCount}` : "NCBI",
            icon: GlobeIcon,
            color: "text-coral",
          },
        ].map((card, i) => (
          <div
            key={card.label}
            className="glass rounded-2xl p-4 md:p-5 hover:border-mint/20 transition-colors"
          >
            <card.icon className={`h-5 w-5 ${card.color} mb-2`} />
            <p className="text-2xl md:text-3xl font-bold text-white">{card.value}</p>
            <p className="text-xs text-muted mt-1">{card.label}</p>
          </div>
        ))}
      </motion.div>
    </section>
  );
}

function DnaIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 3v18M8 6c-2 2-2 4 0 6s4 4 4 6-2 4 0 6M16 6c2 2 2 4 0 6s-4 4-4 6 2 4 0 6" />
    </svg>
  );
}
function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2l8 4v6c0 5-3.5 9-8 10C7.5 21 4 17 4 12V6l8-4z" />
    </svg>
  );
}
function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20M12 2a15 15 0 010 20M12 2a15 15 0 000 20" />
    </svg>
  );
}
