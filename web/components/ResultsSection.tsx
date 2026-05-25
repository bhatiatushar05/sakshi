"use client";

import Image from "next/image";
import { ConservationChart } from "./ConservationChart";
import { LengthChart } from "./LengthChart";
import { RegionsTable } from "./RegionsTable";
import { ASSET_BASE } from "@/lib/data";
import type { AnalysisData } from "@/lib/types";
import { motion } from "framer-motion";

export function ResultsSection({ data }: { data: AnalysisData }) {
  return (
    <section id="results" className="py-20 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="mb-12">
        <h2 className="section-title">Key findings</h2>
        <p className="section-sub mt-2">
          Conservation landscape across {data.stats.alignmentLength} aligned columns.
          Green shading marks highly conserved segments; explore lowest-score windows
          for variability.
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="glass rounded-2xl p-4 md:p-6 mb-8"
      >
        <h3 className="text-white font-medium mb-4">Interactive conservation profile</h3>
        <ConservationChart data={data} />
      </motion.div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="glass rounded-2xl p-4 overflow-hidden">
          <p className="text-sm text-muted mb-3">Pipeline figure — conservation</p>
          <Image
            src={`${ASSET_BASE}/conservation_plot.png`}
            alt="Conservation plot"
            width={800}
            height={320}
            className="rounded-xl w-full h-auto"
          />
        </div>
        <div className="glass rounded-2xl p-4 overflow-hidden">
          <p className="text-sm text-muted mb-3">Sequence length distribution</p>
          <LengthChart data={data} />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <RegionsTable
          title="Top conserved regions"
          regions={data.conservedRegions}
          variant="conserved"
        />
        <RegionsTable
          title="Lowest-variability windows"
          regions={data.variableRegions}
          variant="variable"
          note={data.variableRegionsNote}
        />
      </div>
    </section>
  );
}
