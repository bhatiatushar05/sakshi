# HIV-1 Evolution Analysis — India (Subtype C)

Complete in-silico bioinformatics project with a **runnable Streamlit pipeline app**,
a Python analysis pipeline, and an optional presentation-only Next.js dashboard.

## What’s included

| Part | Description |
|------|-------------|
| `hiv_pipeline.py` | Full pipeline: NCBI fetch → QC → MAFFT → conservation → plots → report |
| `app.py` | Main interactive app: run full pipeline, run single steps, inspect logs, view/download outputs |
| `web/` | Optional static Next.js dashboard for Vercel report sharing only |
| `packages.txt` | Installs MAFFT on Streamlit Community Cloud |
| `Dockerfile` | Runs the full Streamlit app on Docker hosts such as Render or Railway |

## Real results (already run)

- **100** sequences fetched from NCBI  
- **100** passed QC → aligned **100 × 1977**  
- Conservation plots, CSV, and markdown report generated  

---

## Recommended: deploy the full runnable app

Use this when you want someone else to click a public link and actually run the
pipeline from the browser.

### Option A — Streamlit Community Cloud

1. Push this folder to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Create a new app from the GitHub repo.
4. Set the main file path:
   - `app.py` if the repository root is this `hiv_evolution_india` folder
   - `hiv_evolution_india/app.py` if the repository root is the parent `Sakshi` folder
5. Deploy.

Streamlit Cloud reads:

- `requirements.txt` for Python packages
- `packages.txt` for system packages, including `mafft`
- `.streamlit/config.toml` for app theme/server settings

The deployed app keeps the interactive controls:

- Run full pipeline
- Run one step at a time
- Re-fetch from NCBI
- View pipeline logs
- Inspect dataset audit
- Download FASTA, alignment, CSV, plots, and report

### Option B — Render / Railway with Docker

This repo includes a `Dockerfile` and `render.yaml`.

On Render:

1. Create a new **Web Service**.
2. Connect the GitHub repo.
3. Choose Docker environment.
4. Deploy.

The container installs MAFFT and starts:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

---

## Optional: deploy static Vercel report

Use this only when you want a polished read-only dashboard. Vercel does not run
the Python + MAFFT pipeline from the browser.

### 1. Refresh exported web data

```bash
cd hiv_evolution_india
python scripts/export_for_web.py
```

### 2. Deploy the Next.js dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Set **Root Directory** to `web` ← important
4. Framework: **Next.js** (auto-detected)
5. Click **Deploy**

Your live URL will look like: `https://your-project.vercel.app`

### 3. After re-running the pipeline

```bash
python scripts/export_for_web.py
cd web && git add public/data && git commit -m "Update results" && git push
```

Vercel redeploys automatically on push.

---

## Run static web dashboard locally

```bash
cd web
npm install
npm run dev
```

Open **http://localhost:3000**

---

## Run full interactive pipeline locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install mafft    # required for alignment
streamlit run app.py
```

Or run the script without UI:

```bash
python hiv_pipeline.py
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
├── dataset_audit.csv
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
