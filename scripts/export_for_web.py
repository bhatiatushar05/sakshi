#!/usr/bin/env python3
"""Export pipeline outputs to JSON + copy assets for the Next.js / Vercel app."""

import json
import re
import shutil
import sys
from pathlib import Path

import pandas as pd
from Bio import SeqIO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hiv_pipeline import PipelinePaths, build_dataset_audit, summarize_dataset

WEB_DATA = ROOT / "web" / "public" / "data"
GENE_REGIONS = {"gag": (1, 1503), "pol": (1629, 4229), "env": (6225, 8795)}


def gene_note(position: int) -> str:
    notes = [g for g, (s, e) in GENE_REGIONS.items() if s <= position <= e]
    return ", ".join(notes) if notes else "intergenic"


def sliding_low_windows(scores: list[float], window: int = 10, top_n: int = 5):
    if len(scores) < window:
        return []
    windows = []
    for i in range(len(scores) - window + 1):
        seg = scores[i : i + window]
        windows.append(
            {
                "start": i + 1,
                "end": i + window,
                "length": window,
                "mean_score": sum(seg) / len(seg),
                "gene": gene_note(i + window // 2),
            }
        )
    windows.sort(key=lambda w: w["mean_score"])
    return windows[:top_n]


def parse_regions_from_report(text: str, section: str) -> list[dict]:
    regions = []
    in_section = False
    for line in text.splitlines():
        if section in line:
            in_section = True
            continue
        if in_section and line.startswith("##"):
            break
        m = re.match(
            r"- \*\*(\d+)–(\d+)\*\* \(len (\d+), mean score ([\d.]+)\)",
            line.strip(),
        )
        if m:
            start, end, length, score = m.groups()
            mid = (int(start) + int(end)) // 2
            regions.append(
                {
                    "start": int(start),
                    "end": int(end),
                    "length": int(length),
                    "mean_score": float(score),
                    "gene": gene_note(mid),
                }
            )
    return regions


def main() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)

    raw_n = len(list(SeqIO.parse(ROOT / "raw_sequences.fasta", "fasta")))
    cleaned = list(SeqIO.parse(ROOT / "cleaned_sequences.fasta", "fasta"))
    lengths = [len(r.seq) for r in cleaned]

    df = pd.read_csv(ROOT / "conservation_scores.csv")
    scores = df["conservation_score"].tolist()

    report = (ROOT / "summary_report.md").read_text()
    conserved = parse_regions_from_report(report, "Top 5 conserved")
    variable_strict = parse_regions_from_report(report, "Top 5 variable")
    variable_display = variable_strict or sliding_low_windows(scores)
    paths = PipelinePaths(root=ROOT)
    audit_df = build_dataset_audit(paths, "raw")
    if not audit_df.empty:
        audit_df.to_csv(paths.dataset_audit_csv, index=False)
    dataset_summary = summarize_dataset(paths)

    # Length histogram bins
    lo, hi = min(lengths), max(lengths)
    step = max(1, (hi - lo) // 12)
    length_bins = []
    for i in range(12):
        a = lo + i * step
        b = lo + (i + 1) * step if i < 11 else hi + 1
        count = sum(1 for L in lengths if a <= L < b or (i == 11 and L == hi))
        length_bins.append({"range": f"{a}–{b}", "count": count})

    aln = list(SeqIO.parse(ROOT / "aligned_sequences.fasta", "fasta"))

    payload = {
        "meta": {
            "title": "HIV-1 Subtype C Evolution — India",
            "query": "HIV-1[Organism] AND subtype C AND India",
            "generated": pd.Timestamp.now().isoformat(),
        },
        "stats": {
            "fetched": raw_n,
            "removedShort": 0,
            "removedAmbiguous": 0,
            "removedDuplicate": 0,
            "finalCleaned": len(cleaned),
            "alignmentSequences": len(aln),
            "alignmentLength": len(aln[0].seq) if aln else 0,
        },
        "datasetAudit": {
            "rawCount": dataset_summary["raw_count"],
            "cleanedCount": dataset_summary["cleaned_count"],
            "indiaCount": dataset_summary["india_count"],
            "nonIndiaCount": dataset_summary["non_india_count"],
            "unknownYearCount": dataset_summary["unknown_year_count"],
            "meanAmbiguousFraction": dataset_summary["mean_ambiguous"],
            "locationCounts": dataset_summary["location_counts"],
            "lengthSummary": dataset_summary["length_summary"],
            "note": (
                "Audit is inferred from FASTA descriptions. Use full GenBank source "
                "metadata for final India-only filtering."
            ),
        },
        "conservation": [
            {"position": int(r.position), "score": float(r.conservation_score)}
            for r in df.itertuples()
        ],
        "conservedRegions": conserved[:5],
        "variableRegions": variable_display[:5],
        "variableRegionsNote": (
            "Strict hotspots (score ≤ 0.5 for ≥10 nt): none in this alignment. "
            "Showing lowest-variability windows (10 nt) for comparison."
            if not variable_strict
            else "Regions with conservation score ≤ 0.5 for ≥10 consecutive positions."
        ),
        "lengthDistribution": length_bins,
        "lengthStats": {
            "min": min(lengths),
            "max": max(lengths),
            "mean": round(sum(lengths) / len(lengths)),
        },
        "sampleSequences": [
            {"id": r.id, "length": len(r.seq)} for r in cleaned[:8]
        ],
        "genes": [
            {"name": "gag", "start": 1, "end": 1503, "role": "Core structural proteins"},
            {"name": "pol", "start": 1629, "end": 4229, "role": "RT, integrase, protease"},
            {"name": "env", "start": 6225, "end": 8795, "role": "Envelope — high diversity"},
        ],
        "thresholds": {
            "conserved": 0.85,
            "variable": 0.5,
            "minRegionLength": 10,
        },
    }

    (WEB_DATA / "results.json").write_text(json.dumps(payload, indent=2))

    for name in (
        "conservation_plot.png",
        "length_distribution.png",
        "summary_report.md",
        "conservation_scores.csv",
        "dataset_audit.csv",
    ):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, WEB_DATA / name)

    print(f"Exported → {WEB_DATA}")


if __name__ == "__main__":
    main()
