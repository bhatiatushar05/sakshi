#!/usr/bin/env bash
# Refresh web data and verify production build before Vercel deploy.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

if [[ -f raw_sequences.fasta ]]; then
  python scripts/export_for_web.py
else
  echo "Run python hiv_pipeline.py first to generate data."
  exit 1
fi

cd web
npm install
npm run build
echo ""
echo "✓ Build OK. Push to GitHub and deploy with Vercel Root Directory = web"
