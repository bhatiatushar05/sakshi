#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi
if ! command -v mafft &>/dev/null && ! command -v clustalo &>/dev/null; then
  echo "Install an aligner: brew install mafft"
  exit 1
fi
exec streamlit run app.py
