import { BookOpen, GraduationCap, Globe2 } from "lucide-react";

export function About() {
  return (
    <section id="about" className="py-20 px-4 md:px-6 max-w-6xl mx-auto pb-32">
      <div className="glass rounded-2xl p-6 md:p-10">
        <h2 className="section-title mb-4">About this project</h2>
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          <div className="flex gap-3">
            <GraduationCap className="h-6 w-6 text-mint shrink-0" />
            <div>
              <p className="font-medium text-white">Academic focus</p>
              <p className="text-sm text-muted mt-1 leading-relaxed">
                Life Sciences in-silico project studying HIV-1 subtype C evolution
                among Indian isolates — mutation hotspots and phylogenetic patterns.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <Globe2 className="h-6 w-6 text-sky shrink-0" />
            <div>
              <p className="font-medium text-white">Data sources</p>
              <p className="text-sm text-muted mt-1 leading-relaxed">
                NCBI GenBank via Biopython Entrez; sequences filtered and aligned
                with MAFFT. Conservation metrics computed in Python.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <BookOpen className="h-6 w-6 text-violet shrink-0" />
            <div>
              <p className="font-medium text-white">How to cite</p>
              <p className="text-sm text-muted mt-1 leading-relaxed">
                Reference NCBI accessions from cleaned FASTA headers. Mention
                HxB2 coordinates when discussing gag / pol / env regions.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-10 p-4 rounded-xl bg-canvas/60 border border-border font-mono text-xs text-muted leading-relaxed">
          <p className="text-white text-sm font-sans font-medium mb-2">
            Reproduce locally
          </p>
          <code className="block whitespace-pre-wrap">
            {`cd hiv_evolution_india
pip install -r requirements.txt
brew install mafft
python hiv_pipeline.py
python scripts/export_for_web.py
cd web && npm install && npm run build`}
          </code>
        </div>
      </div>
    </section>
  );
}
