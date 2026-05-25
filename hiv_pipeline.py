"""
HIV-1 subtype C evolution pipeline — Indian isolates.
Modular steps: fetch → clean → align → conserve → plot → report.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from Bio import AlignIO, Entrez, SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENTREZ_EMAIL = "student@example.com"
ENTREZ_QUERY = "HIV-1[Organism] AND subtype C AND India"
MIN_SEQUENCES = 50
MIN_LENGTH = 800
MAX_AMBIGUOUS_FRACTION = 0.05
AMBIGUOUS_BASES = set("NRYSWKMBDHV")

CONSERVED_THRESHOLD = 0.85
VARIABLE_THRESHOLD = 0.50
MIN_REGION_LENGTH = 10

VALID_BASES = set("ATGC")

# Approximate HxB2 coordinates (nucleotide positions in genome)
GENE_REGIONS = {
    "gag": (1, 1503),
    "pol": (1629, 4229),
    "env": (6225, 8795),
}

LOCATION_TERMS = (
    "India",
    "South Africa",
    "Malawi",
    "Zimbabwe",
    "Botswana",
    "Zambia",
    "Uganda",
    "Kenya",
    "Tanzania",
    "Ethiopia",
    "Brazil",
    "China",
)


@dataclass
class PipelineStats:
    fetched: int = 0
    removed_short: int = 0
    removed_ambiguous: int = 0
    removed_duplicate: int = 0
    final_cleaned: int = 0
    num_sequences: int = 0
    alignment_length: int = 0
    conserved_regions: list = field(default_factory=list)
    variable_regions: list = field(default_factory=list)


@dataclass
class PipelinePaths:
    root: Path

    @property
    def raw_fasta(self) -> Path:
        return self.root / "raw_sequences.fasta"

    @property
    def cleaned_fasta(self) -> Path:
        return self.root / "cleaned_sequences.fasta"

    @property
    def aligned_aln(self) -> Path:
        return self.root / "aligned_sequences.aln"

    @property
    def aligned_fasta(self) -> Path:
        return self.root / "aligned_sequences.fasta"

    @property
    def conservation_csv(self) -> Path:
        return self.root / "conservation_scores.csv"

    @property
    def conservation_plot(self) -> Path:
        return self.root / "conservation_plot.png"

    @property
    def length_plot(self) -> Path:
        return self.root / "length_distribution.png"

    @property
    def summary_report(self) -> Path:
        return self.root / "summary_report.md"

    @property
    def dataset_audit_csv(self) -> Path:
        return self.root / "dataset_audit.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _log(msg: str, callback: Optional[Callable[[str], None]] = None) -> None:
    print(msg)
    if callback:
        callback(msg)


def _ambiguous_fraction(seq: str) -> float:
    seq = seq.upper()
    if not seq:
        return 1.0
    amb = sum(1 for b in seq if b in AMBIGUOUS_BASES)
    return amb / len(seq)


def _extract_accession(record_id: str) -> str:
    """Pull GenBank accession from FASTA id / description."""
    token = record_id.split()[0].strip()
    if "|" in token:
        parts = token.split("|")
        if len(parts) >= 2 and parts[1]:
            return parts[1]
    return re.sub(r"[^\w.-]", "", token.split(".")[0])


def _parse_year_region(description: str) -> tuple[str, str]:
    year = "Unknown"
    region = "Unknown"
    desc = description or ""

    ym = re.search(r"\b(19|20)\d{2}\b", desc)
    if ym:
        year = ym.group(0)

    for state in (
        "Maharashtra",
        "Tamil Nadu",
        "Karnataka",
        "Andhra Pradesh",
        "Telangana",
        "Kerala",
        "Gujarat",
        "Rajasthan",
        "West Bengal",
        "Delhi",
        "Uttar Pradesh",
        "Madhya Pradesh",
        "Punjab",
        "Bihar",
        "Odisha",
        "India",
    ):
        if state.lower() in desc.lower():
            region = state
            break

    if region == "Unknown":
        rm = re.search(
            r"isolate\s+[\w.-]+\s+from\s+([A-Za-z\s]+?)(?:\s+patient|\s*,|\s*$)",
            desc,
            re.I,
        )
        if rm:
            region = rm.group(1).strip()[:40]

    return year, region


def _standard_header(record: SeqRecord) -> str:
    acc = _extract_accession(record.id)
    year, region = _parse_year_region(record.description)
    region_slug = re.sub(r"\s+", "_", region)
    return f"{acc}_{year}_{region_slug}"


def _gene_note(position: int) -> str:
    notes = []
    for gene, (start, end) in GENE_REGIONS.items():
        if start <= position <= end:
            notes.append(gene)
    return ", ".join(notes) if notes else "intergenic / approximate map"


def _infer_location(description: str) -> str:
    desc = description or ""
    for term in LOCATION_TERMS:
        if term.lower() in desc.lower():
            return term

    match = re.search(
        r"\bfrom\s+([A-Za-z][A-Za-z\s]+?)(?:\s+pol|\s+gag|\s+env|\s+gene|\s+patient|\s*,|\s*$)",
        desc,
        re.I,
    )
    if match:
        return match.group(1).strip()[:50]
    return "Unknown"


def build_dataset_audit(paths: PipelinePaths, source: str = "raw") -> pd.DataFrame:
    fasta_path = paths.raw_fasta if source == "raw" else paths.cleaned_fasta
    rows = []
    if not fasta_path.exists():
        return pd.DataFrame(
            columns=[
                "accession",
                "length_nt",
                "ambiguous_fraction",
                "year",
                "header_region",
                "inferred_location",
                "is_india_description",
                "description",
            ]
        )

    for record in SeqIO.parse(fasta_path, "fasta"):
        seq = str(record.seq).upper()
        year, region = _parse_year_region(record.description)
        location = _infer_location(record.description)
        rows.append(
            {
                "accession": _extract_accession(record.id),
                "length_nt": len(seq),
                "ambiguous_fraction": round(_ambiguous_fraction(seq), 4),
                "year": year,
                "header_region": region,
                "inferred_location": location,
                "is_india_description": location == "India",
                "description": record.description,
            }
        )
    return pd.DataFrame(rows)


def summarize_dataset(paths: PipelinePaths) -> dict:
    raw_df = build_dataset_audit(paths, "raw")
    cleaned_df = build_dataset_audit(paths, "cleaned")

    location_counts = {}
    if not raw_df.empty:
        location_counts = raw_df["inferred_location"].value_counts().to_dict()

    india_count = int(location_counts.get("India", 0))
    non_india_count = int(len(raw_df) - india_count) if not raw_df.empty else 0
    unknown_year_count = (
        int((raw_df["year"] == "Unknown").sum()) if not raw_df.empty else 0
    )
    mean_ambiguous = (
        float(raw_df["ambiguous_fraction"].mean()) if not raw_df.empty else 0.0
    )

    length_summary = {
        "raw_min": int(raw_df["length_nt"].min()) if not raw_df.empty else 0,
        "raw_max": int(raw_df["length_nt"].max()) if not raw_df.empty else 0,
        "cleaned_min": int(cleaned_df["length_nt"].min()) if not cleaned_df.empty else 0,
        "cleaned_max": int(cleaned_df["length_nt"].max()) if not cleaned_df.empty else 0,
    }

    return {
        "raw_count": int(len(raw_df)),
        "cleaned_count": int(len(cleaned_df)),
        "india_count": india_count,
        "non_india_count": non_india_count,
        "unknown_year_count": unknown_year_count,
        "mean_ambiguous": mean_ambiguous,
        "location_counts": location_counts,
        "length_summary": length_summary,
    }


# ---------------------------------------------------------------------------
# Step 1 — Fetch
# ---------------------------------------------------------------------------


def fetch_sequences(
    paths: PipelinePaths,
    email: str = ENTREZ_EMAIL,
    min_count: int = MIN_SEQUENCES,
    force: bool = False,
    log: Optional[Callable[[str], None]] = None,
) -> int:
    if paths.raw_fasta.exists() and not force:
        records = list(SeqIO.parse(paths.raw_fasta, "fasta"))
        _log(f"[Step 1] Using existing raw file ({len(records)} sequences).", log)
        return len(records)

    Entrez.email = email
    _log(f"[Step 1] Searching NCBI: {ENTREZ_QUERY}", log)

    with Entrez.esearch(
        db="nucleotide", term=ENTREZ_QUERY, retmax=max(min_count, 100)
    ) as handle:
        result = Entrez.read(handle)

    ids = result.get("IdList", [])
    if len(ids) < min_count:
        _log(
            f"[Step 1] Warning: only {len(ids)} IDs found (requested ≥{min_count}).",
            log,
        )

    records: list[SeqRecord] = []
    batch_size = 20
    for i in range(0, len(ids), batch_size):
        batch = ids[i : i + batch_size]
        _log(f"[Step 1] Fetching batch {i // batch_size + 1} ({len(batch)} IDs)...", log)
        with Entrez.efetch(
            db="nucleotide", id=batch, rettype="fasta", retmode="text"
        ) as handle:
            records.extend(SeqIO.parse(handle, "fasta"))
        time.sleep(0.5)

    SeqIO.write(records, paths.raw_fasta, "fasta")
    _log(f"[Step 1] Saved {len(records)} sequences → {paths.raw_fasta}", log)
    return len(records)


# ---------------------------------------------------------------------------
# Step 2 — Clean
# ---------------------------------------------------------------------------


def clean_sequences(
    paths: PipelinePaths,
    log: Optional[Callable[[str], None]] = None,
) -> PipelineStats:
    stats = PipelineStats()
    records = list(SeqIO.parse(paths.raw_fasta, "fasta"))
    stats.fetched = len(records)
    _log(f"[Step 2] Loaded {stats.fetched} raw sequences.", log)

    seen_seqs: set[str] = set()
    seen_acc: set[str] = set()
    cleaned: list[SeqRecord] = []

    for rec in records:
        seq = str(rec.seq).upper()
        acc = _extract_accession(rec.id)

        if len(seq) < MIN_LENGTH:
            stats.removed_short += 1
            continue
        if _ambiguous_fraction(seq) > MAX_AMBIGUOUS_FRACTION:
            stats.removed_ambiguous += 1
            continue
        if acc in seen_acc or seq in seen_seqs:
            stats.removed_duplicate += 1
            continue

        seen_acc.add(acc)
        seen_seqs.add(seq)
        header = _standard_header(rec)
        cleaned.append(SeqRecord(Seq(seq), id=header, description=header))

    stats.final_cleaned = len(cleaned)
    SeqIO.write(cleaned, paths.cleaned_fasta, "fasta")

    _log(
        f"[Step 2] Summary — fetched: {stats.fetched}, "
        f"removed (short/ambig/dup): "
        f"{stats.removed_short + stats.removed_ambiguous + stats.removed_duplicate}, "
        f"final: {stats.final_cleaned}",
        log,
    )
    _log(f"[Step 2] Saved → {paths.cleaned_fasta}", log)
    return stats


# ---------------------------------------------------------------------------
# Step 3 — MSA
# ---------------------------------------------------------------------------


def _run_clustal_omega(infile: Path, outfile: Path) -> bool:
    if not shutil.which("clustalo"):
        return False
    subprocess.run(
        [
            "clustalo",
            "-i",
            str(infile),
            "-o",
            str(outfile),
            "--auto",
            "--outfmt=clu",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return outfile.exists()


def _run_mafft(infile: Path, outfile: Path) -> bool:
    if not shutil.which("mafft"):
        return False
    with open(outfile, "w") as out:
        subprocess.run(
            ["mafft", "--auto", str(infile)],
            check=True,
            stdout=out,
            stderr=subprocess.PIPE,
            text=True,
        )
    return outfile.exists()


def run_msa(
    paths: PipelinePaths,
    log: Optional[Callable[[str], None]] = None,
) -> tuple[int, int]:
    _log("[Step 3] Running multiple sequence alignment...", log)
    aligned = None

    if _run_clustal_omega(paths.cleaned_fasta, paths.aligned_aln):
        _log("[Step 3] Clustal Omega alignment complete.", log)
        aligned = AlignIO.read(paths.aligned_aln, "clustal")
    elif _run_mafft(paths.cleaned_fasta, paths.aligned_fasta):
        _log("[Step 3] MAFFT alignment complete (Clustal Omega not found).", log)
        aligned = AlignIO.read(paths.aligned_fasta, "fasta")
        AlignIO.write(aligned, paths.aligned_aln, "clustal")
    else:
        raise RuntimeError(
            "No aligner found. Install Clustal Omega (`brew install clustalo`) "
            "or MAFFT (`brew install mafft`)."
        )

    AlignIO.write(aligned, paths.aligned_fasta, "fasta")
    n_seq = len(aligned)
    aln_len = aligned.get_alignment_length()
    _log(f"[Step 3] Alignment dimensions: {n_seq} × {aln_len}", log)
    return n_seq, aln_len


# ---------------------------------------------------------------------------
# Step 4 — Conservation
# ---------------------------------------------------------------------------


def _column_conservation(column: str) -> float:
    bases = [b.upper() for b in column if b.upper() in VALID_BASES]
    if not bases:
        return 0.0
    counts = Counter(bases)
    return counts.most_common(1)[0][1] / len(bases)


def _find_regions(
    scores: list[float], threshold: float, min_len: int, mode: str
) -> list[dict]:
    regions = []
    start = None
    for i, s in enumerate(scores):
        ok = s >= threshold if mode == "conserved" else s <= threshold
        if ok and start is None:
            start = i
        elif not ok and start is not None:
            if i - start >= min_len:
                seg = scores[start:i]
                regions.append(
                    {
                        "start": start + 1,
                        "end": i,
                        "length": i - start,
                        "mean_score": sum(seg) / len(seg),
                    }
                )
            start = None
    if start is not None and len(scores) - start >= min_len:
        seg = scores[start:]
        regions.append(
            {
                "start": start + 1,
                "end": len(scores),
                "length": len(scores) - start,
                "mean_score": sum(seg) / len(seg),
            }
        )
    return regions


def analyze_conservation(
    paths: PipelinePaths,
    log: Optional[Callable[[str], None]] = None,
) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    alignment = AlignIO.read(paths.aligned_fasta, "fasta")
    aln_len = alignment.get_alignment_length()

    scores = []
    for col in range(aln_len):
        column = alignment[:, col]
        scores.append(_column_conservation(column))

    df = pd.DataFrame(
        {"position": range(1, aln_len + 1), "conservation_score": scores}
    )
    df["gene_context"] = df["position"].apply(_gene_note)
    df.to_csv(paths.conservation_csv, index=False)

    conserved = _find_regions(
        scores, CONSERVED_THRESHOLD, MIN_REGION_LENGTH, "conserved"
    )
    variable = _find_regions(
        scores, VARIABLE_THRESHOLD, MIN_REGION_LENGTH, "variable"
    )
    conserved.sort(key=lambda r: r["mean_score"], reverse=True)
    variable.sort(key=lambda r: r["mean_score"])

    _log(
        f"[Step 4] Found {len(conserved)} conserved and {len(variable)} variable regions.",
        log,
    )
    _log(f"[Step 4] Saved scores → {paths.conservation_csv}", log)
    return df, conserved, variable


# ---------------------------------------------------------------------------
# Step 5 — Plots
# ---------------------------------------------------------------------------


def create_plots(
    paths: PipelinePaths,
    scores_df: pd.DataFrame,
    conserved: list[dict],
    variable: list[dict],
    log: Optional[Callable[[str], None]] = None,
) -> None:
    sns.set_theme(style="whitegrid")
    positions = scores_df["position"].values
    scores = scores_df["conservation_score"].values

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(positions, scores, color="#2563eb", linewidth=0.8, label="Conservation score")
    ax.axhline(CONSERVED_THRESHOLD, color="#16a34a", linestyle="--", alpha=0.6, label="Conserved threshold")
    ax.axhline(VARIABLE_THRESHOLD, color="#dc2626", linestyle="--", alpha=0.6, label="Variable threshold")

    for r in conserved:
        ax.axvspan(r["start"], r["end"], color="#22c55e", alpha=0.2)
    for r in variable:
        ax.axvspan(r["start"], r["end"], color="#ef4444", alpha=0.2)

    ax.set_xlabel("Alignment position")
    ax.set_ylabel("Conservation score")
    ax.set_ylim(0, 1.05)
    ax.set_title("HIV-1 subtype C (India) — per-column conservation")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(paths.conservation_plot, dpi=150)
    plt.close(fig)

    lengths = [len(rec.seq) for rec in SeqIO.parse(paths.cleaned_fasta, "fasta")]
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.hist(lengths, bins=20, color="#7c3aed", edgecolor="white")
    ax2.set_xlabel("Sequence length (nt)")
    ax2.set_ylabel("Count")
    ax2.set_title("Cleaned sequence length distribution (pre-alignment)")
    fig2.tight_layout()
    fig2.savefig(paths.length_plot, dpi=150)
    plt.close(fig2)

    _log(f"[Step 5] Saved plots → {paths.conservation_plot}, {paths.length_plot}", log)


# ---------------------------------------------------------------------------
# Step 6 — Report
# ---------------------------------------------------------------------------


def generate_report(
    paths: PipelinePaths,
    stats: PipelineStats,
    conserved: list[dict],
    variable: list[dict],
    log: Optional[Callable[[str], None]] = None,
) -> str:
    top_conserved = conserved[:5]
    top_variable = variable[:5]
    audit_df = build_dataset_audit(paths, "raw")
    if not audit_df.empty:
        audit_df.to_csv(paths.dataset_audit_csv, index=False)
    dataset = summarize_dataset(paths)

    def _fmt_regions(regions: list[dict]) -> str:
        if not regions:
            return "_None identified._\n"
        lines = []
        for r in regions:
            mid = (r["start"] + r["end"]) // 2
            lines.append(
                f"- **{r['start']}–{r['end']}** (len {r['length']}, "
                f"mean score {r['mean_score']:.3f}) — {_gene_note(mid)}"
            )
        return "\n".join(lines) + "\n"

    def _fmt_location_counts() -> str:
        counts = dataset["location_counts"]
        if not counts:
            return "_No raw FASTA records available for audit._\n"
        lines = ["| Inferred location from FASTA description | Records |", "|---|---:|"]
        for location, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
            lines.append(f"| {location} | {count} |")
        return "\n".join(lines) + "\n"

    if dataset["raw_count"]:
        india_fraction = dataset["india_count"] / dataset["raw_count"]
    else:
        india_fraction = 0

    if dataset["non_india_count"]:
        dataset_interpretation = (
            "This run should be treated as a **pipeline demonstration**, not a final "
            "India-only biological analysis. Several FASTA descriptions point to "
            "non-Indian samples, so downstream conservation results reflect a mixed "
            "set of HIV-1 subtype C records."
        )
    elif dataset["raw_count"]:
        dataset_interpretation = (
            "All raw FASTA descriptions visibly match India. For publication-quality "
            "work, this should still be verified with full GenBank source metadata."
        )
    else:
        dataset_interpretation = "No raw FASTA records were available when this report was generated."

    report = f"""# HIV-1 Subtype C Evolution — India

## Plain-language result

This pipeline collected HIV-1 subtype C nucleotide sequences, cleaned low-quality entries,
aligned the remaining sequences, and calculated how conserved each alignment position is.

**Important dataset note:** {dataset_interpretation}

## Pipeline summary

| Stage | Count / value |
|-------|----------------|
| Raw sequences fetched | {stats.fetched} |
| Removed (too short) | {stats.removed_short} |
| Removed (>5% ambiguous) | {stats.removed_ambiguous} |
| Removed (duplicates) | {stats.removed_duplicate} |
| **Final cleaned** | **{stats.final_cleaned}** |
| Alignment dimensions | {stats.num_sequences} sequences × {stats.alignment_length} positions |

## Dataset audit

| Check | Result |
|-------|--------|
| Raw records audited | {dataset["raw_count"]} |
| Records visibly described as India | {dataset["india_count"]} ({india_fraction:.0%}) |
| Records not visibly described as India | {dataset["non_india_count"]} |
| Records with unknown year in FASTA description | {dataset["unknown_year_count"]} |
| Raw length range | {dataset["length_summary"]["raw_min"]}–{dataset["length_summary"]["raw_max"]} nt |
| Cleaned length range | {dataset["length_summary"]["cleaned_min"]}–{dataset["length_summary"]["cleaned_max"]} nt |
| Mean ambiguous-base fraction in raw FASTA | {dataset["mean_ambiguous"]:.3f} |

{_fmt_location_counts()}

The audit above is based on FASTA descriptions. A stricter final project should fetch full
GenBank records and filter by `/country`, `/collection_date`, and subtype/source qualifiers.

## Top 5 conserved regions (score ≥ {CONSERVED_THRESHOLD}, ≥ {MIN_REGION_LENGTH} nt)

{_fmt_regions(top_conserved)}

## Top 5 variable regions / mutation hotspots (score ≤ {VARIABLE_THRESHOLD})

{_fmt_regions(top_variable)}

## HIV functional gene map (approximate HxB2 coordinates)

| Gene | Approx. nucleotide range | Notes |
|------|--------------------------|-------|
| gag | 1 – 1503 | Core structural proteins |
| pol | 1629 – 4229 | Reverse transcriptase, integrase, protease |
| env | 6225 – 8795 | Envelope glycoproteins — high diversity |

Alignment positions are relative to the MSA columns; mapping to HxB2 is approximate when partial genomes are included.

## How to interpret this report

- A conservation score near **1.0** means almost every sequence has the same nucleotide at that alignment column.
- A lower score means more variation among sequences at that position.
- Conserved regions may point to functionally constrained parts of the virus.
- Variable regions may point to mutation hotspots, but this run identified none under the strict cutoff of score ≤ {VARIABLE_THRESHOLD} for ≥ {MIN_REGION_LENGTH} consecutive positions.
- Because this dataset currently includes non-India descriptions, do not make India-specific claims until the dataset is filtered more strictly.

## Output files

- `{paths.raw_fasta.name}`
- `{paths.cleaned_fasta.name}`
- `{paths.aligned_aln.name}` / `{paths.aligned_fasta.name}`
- `{paths.conservation_csv.name}`
- `{paths.dataset_audit_csv.name}`
- `{paths.conservation_plot.name}` / `{paths.length_plot.name}`

---
*Generated by HIV-1 India Evolution Pipeline*
"""
    paths.summary_report.write_text(report)
    _log(f"[Step 6] Report saved → {paths.summary_report}", log)
    return report


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------


def run_pipeline(
    output_dir: Optional[Path] = None,
    email: str = ENTREZ_EMAIL,
    force_fetch: bool = False,
    skip_fetch_if_exists: bool = True,
    log: Optional[Callable[[str], None]] = None,
) -> tuple[PipelineStats, str]:
    root = output_dir or Path(__file__).resolve().parent
    root.mkdir(parents=True, exist_ok=True)
    paths = PipelinePaths(root=root)
    stats = PipelineStats()

    if not (skip_fetch_if_exists and paths.raw_fasta.exists()):
        stats.fetched = fetch_sequences(
            paths, email=email, force=force_fetch, log=log
        )
    else:
        stats.fetched = len(list(SeqIO.parse(paths.raw_fasta, "fasta")))
        _log(f"[Step 1] Skipped fetch — using {stats.fetched} cached sequences.", log)

    clean_stats = clean_sequences(paths, log=log)
    stats.removed_short = clean_stats.removed_short
    stats.removed_ambiguous = clean_stats.removed_ambiguous
    stats.removed_duplicate = clean_stats.removed_duplicate
    stats.final_cleaned = clean_stats.final_cleaned

    if stats.final_cleaned < 2:
        raise ValueError("Need at least 2 cleaned sequences for alignment.")

    stats.num_sequences, stats.alignment_length = run_msa(paths, log=log)
    scores_df, conserved, variable = analyze_conservation(paths, log=log)
    stats.conserved_regions = conserved
    stats.variable_regions = variable

    create_plots(paths, scores_df, conserved, variable, log=log)
    report = generate_report(paths, stats, conserved, variable, log=log)

    try:
        import sys

        export_script = root / "scripts" / "export_for_web.py"
        if export_script.exists():
            _log("[Export] Syncing results for web dashboard...", log)
            subprocess.run(
                [sys.executable, str(export_script)],
                check=True,
                cwd=str(root),
            )
    except Exception as exc:
        _log(f"[Export] Web sync skipped: {exc}", log)

    return stats, report


if __name__ == "__main__":
    run_pipeline()
