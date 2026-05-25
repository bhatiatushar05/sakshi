"use client";

import { motion } from "framer-motion";
import { ExternalLink, Globe2, MonitorPlay, TerminalSquare } from "lucide-react";
import type { AnalysisData } from "@/lib/types";

export function RunMode({ data }: { data: AnalysisData }) {
  const audit = data.datasetAudit;

  return (
    <section id="run" className="py-16 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="mb-10">
        <h2 className="section-title">Run modes</h2>
        <p className="section-sub mt-2">
          This public Vercel page is the shareable report. The full pipeline runner is
          the local Streamlit app because it needs Python, Biopython, MAFFT or Clustal
          Omega, and NCBI network calls.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-start gap-4">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-sky/10 text-sky ring-1 ring-sky/20">
              <Globe2 className="h-5 w-5" />
            </span>
            <div>
              <p className="text-xs font-mono uppercase tracking-wide text-sky">
                Vercel share link
              </p>
              <h3 className="mt-1 text-xl font-semibold text-white">Report mode</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted">
                Best for sharing with someone else. It shows the latest exported
                figures, results, report, and dataset audit. It does not rerun Python
                from the browser.
              </p>
            </div>
          </div>

          {audit ? (
            <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl border border-border bg-canvas/30 p-3">
                <p className="text-muted">Raw records</p>
                <p className="mt-1 text-2xl font-bold text-white">{audit.rawCount}</p>
              </div>
              <div className="rounded-xl border border-amber-300/25 bg-amber-300/10 p-3">
                <p className="text-amber-100">India-described</p>
                <p className="mt-1 text-2xl font-bold text-white">
                  {audit.indiaCount}/{audit.rawCount}
                </p>
              </div>
            </div>
          ) : null}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-40px" }}
          transition={{ delay: 0.06 }}
          className="glass rounded-2xl p-6 border-mint/25"
        >
          <div className="flex items-start gap-4">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-mint/10 text-mint ring-1 ring-mint/20">
              <MonitorPlay className="h-5 w-5" />
            </span>
            <div>
              <p className="text-xs font-mono uppercase tracking-wide text-mint">
                Local interactive app
              </p>
              <h3 className="mt-1 text-xl font-semibold text-white">Pipeline runner mode</h3>
              <p className="mt-3 text-sm leading-relaxed text-muted">
                Use this when you want the old controls: run full pipeline, run one
                step at a time, edit Entrez email, re-fetch NCBI data, and regenerate
                plots/reports.
              </p>
            </div>
          </div>

          <div className="mt-5 rounded-xl border border-border bg-[#050a12] p-4">
            <div className="flex items-center gap-2 text-xs font-mono text-muted">
              <TerminalSquare className="h-4 w-4 text-mint" />
              from the project folder
            </div>
            <pre className="mt-3 overflow-x-auto text-sm leading-relaxed text-mint">
{`cd hiv_evolution_india
source .venv/bin/activate
streamlit run app.py`}
            </pre>
          </div>

          <a
            href="/data/summary_report.md"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-5 inline-flex items-center gap-2 rounded-full bg-mint px-5 py-2.5 text-sm font-semibold text-canvas hover:opacity-90 transition-opacity"
          >
            Open exported report
            <ExternalLink className="h-4 w-4" />
          </a>
        </motion.div>
      </div>
    </section>
  );
}
