import { Download, FileCode, FileImage, FileText } from "lucide-react";
import { ASSET_BASE } from "@/lib/data";

const FILES = [
  {
    name: "results.json",
    desc: "All stats & scores for this dashboard",
    icon: FileCode,
    href: `${ASSET_BASE}/results.json`,
  },
  {
    name: "conservation_scores.csv",
    desc: "Per-position conservation scores",
    icon: FileCode,
    href: `${ASSET_BASE}/conservation_scores.csv`,
  },
  {
    name: "conservation_plot.png",
    desc: "Publication-quality conservation figure",
    icon: FileImage,
    href: `${ASSET_BASE}/conservation_plot.png`,
  },
  {
    name: "length_distribution.png",
    desc: "Pre-alignment length histogram",
    icon: FileImage,
    href: `${ASSET_BASE}/length_distribution.png`,
  },
  {
    name: "summary_report.md",
    desc: "Full markdown analysis report",
    icon: FileText,
    href: `${ASSET_BASE}/summary_report.md`,
  },
];

export function Downloads() {
  return (
    <section id="downloads" className="py-20 px-4 md:px-6 max-w-6xl mx-auto">
      <div className="mb-10">
        <h2 className="section-title">Downloads</h2>
        <p className="section-sub mt-2">
          Export figures and data for your report, slides, or supplementary materials.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        {FILES.map((f) => (
          <a
            key={f.name}
            href={f.href}
            download
            target="_blank"
            rel="noopener noreferrer"
            className="glass rounded-2xl p-5 flex gap-4 items-start group transition-all hover:border-mint/30 hover:shadow-glow"
          >
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-sky/10 text-sky group-hover:bg-mint/10 group-hover:text-mint transition-colors">
              <f.icon className="h-5 w-5" />
            </span>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-white flex items-center gap-2">
                {f.name}
                <Download className="h-3.5 w-3.5 text-muted" />
              </p>
              <p className="text-sm text-muted mt-1">{f.desc}</p>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
}
