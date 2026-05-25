# HIV-1 Evolution Analysis — India (Subtype C)

Complete in-silico bioinformatics project with a **presentation-ready web dashboard** (Next.js) and a **Python analysis pipeline**.

## What’s included

| Part | Description |
|------|-------------|
| `hiv_pipeline.py` | Full pipeline: NCBI fetch → QC → MAFFT → conservation → plots → report |
| `web/` | Beautiful Next.js dashboard for presentations & Vercel |
| `app.py` | Optional Streamlit UI for local interactive runs |

## Real results (already run)

- **100** sequences fetched from NCBI  
- **100** passed QC → aligned **100 × 1977**  
- Conservation plots, CSV, and markdown report generated  

---

## Deploy to Vercel (shareable link)

### 1. Push to GitHub

```bash
cd hiv_evolution_india
git init
git add .
git commit -m "HIV-1 India evolution analysis — presentation ready"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Import on Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Set **Root Directory** to `web` ← important
4. Framework: **Next.js** (auto-detected)
5. Click **Deploy**

Your live URL will look like: `https://your-project.vercel.app`

### 3. After re-running the pipeline

```bash
python hiv_pipeline.py          # auto-exports to web/public/data
# or
python scripts/export_for_web.py
cd web && git add public/data && git commit -m "Update results" && git push
```

Vercel redeploys automatically on push.

---

## Run web app locally

```bash
cd web
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Run Python pipeline locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install mafft    # required for alignment
python hiv_pipeline.py
python scripts/export_for_web.py
```

## Output files

```
hiv_evolution_india/
├── raw_sequences.fasta
├── cleaned_sequences.fasta
├── aligned_sequences.aln / .fasta
├── conservation_scores.csv
├── conservation_plot.png
├── length_distribution.png
├── summary_report.md
└── web/public/data/     ← bundled for Vercel
```

## Presentation flow (recommended)

1. **Overview** — project goal & key metrics  
2. **Pipeline** — six steps you implemented  
3. **Key findings** — conservation chart & top regions  
4. **Gene map** — gag / pol / env context  
5. **Downloads** — figures for slides  

---

*Life Sciences · HIV-1 subtype C · Indian isolates · NCBI GenBank*
