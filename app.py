"""
HIV-1 Evolution India — Streamlit web app.
Run: streamlit run app.py
"""

from __future__ import annotations

import traceback
from pathlib import Path

import pandas as pd
import streamlit as st
from Bio import SeqIO

from hiv_pipeline import (
    ENTREZ_EMAIL,
    ENTREZ_QUERY,
    PipelinePaths,
    analyze_conservation,
    build_dataset_audit,
    clean_sequences,
    create_plots,
    fetch_sequences,
    generate_report,
    run_msa,
    run_pipeline,
    summarize_dataset,
)

APP_DIR = Path(__file__).resolve().parent
paths = PipelinePaths(root=APP_DIR)

st.set_page_config(
    page_title="HIV-1 India Evolution",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        color: #94a3b8;
        margin-bottom: 1.25rem;
        font-size: 1.02rem;
    }
    .status-strip {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        background: rgba(15, 23, 42, 0.52);
        margin: 0.6rem 0 1.2rem;
    }
    .status-strip strong {
        color: #f8fafc;
    }
    .status-strip p {
        margin: 0.35rem 0 0;
        color: #cbd5e1;
        line-height: 1.55;
    }
    .result-card {
        min-height: 132px;
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 8px;
        padding: 1rem 1rem 0.9rem;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.96), rgba(15, 23, 42, 0.96));
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.18);
    }
    .result-card .label {
        color: #94a3b8;
        font-size: 0.84rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 0.45rem;
    }
    .result-card .value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    .result-card .hint {
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.35;
    }
    .quality-card {
        border: 1px solid rgba(250, 204, 21, 0.35);
        border-radius: 8px;
        padding: 1rem 1.1rem;
        background: rgba(113, 63, 18, 0.22);
        margin-top: 1rem;
    }
    .quality-card.good {
        border-color: rgba(34, 197, 94, 0.35);
        background: rgba(20, 83, 45, 0.22);
    }
    .quality-card strong {
        color: #f8fafc;
    }
    .quality-card p {
        margin: 0.35rem 0 0;
        color: #d1d5db;
        line-height: 1.55;
    }
    .next-step-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin-top: 0.6rem;
    }
    .next-step {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        padding: 0.9rem;
        background: rgba(15, 23, 42, 0.38);
    }
    .next-step b {
        color: #f8fafc;
    }
    .next-step span {
        display: block;
        color: #cbd5e1;
        margin-top: 0.35rem;
        line-height: 1.45;
    }
    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 1.35rem 0 0.5rem;
    }
    .explainer {
        color: #cbd5e1;
        line-height: 1.6;
        max-width: 980px;
        margin-bottom: 0.8rem;
    }
    .mini-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.8rem 0 1rem;
    }
    .mini-card {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        background: rgba(15, 23, 42, 0.42);
    }
    .mini-card b {
        color: #f8fafc;
    }
    .mini-card p {
        color: #cbd5e1;
        margin: 0.35rem 0 0;
        line-height: 1.5;
    }
    .small-note {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    @media (max-width: 900px) {
        .next-step-grid { grid-template-columns: 1fr; }
        .mini-grid { grid-template-columns: 1fr; }
        .result-card { min-height: 116px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🧬 HIV-1 Pipeline")
    st.caption("Subtype C · dataset audit · conservation analysis")

    st.divider()
    st.subheader("NCBI settings")
    email = st.text_input("Entrez email", value=ENTREZ_EMAIL)
    force_fetch = st.checkbox("Re-fetch from NCBI (overwrite raw)", value=False)
    st.caption(f"Query: `{ENTREZ_QUERY}`")

    st.divider()
    st.subheader("Run")
    run_full = st.button("▶ Run full pipeline", type="primary", use_container_width=True)
    run_step = st.selectbox(
        "Or run a single step",
        [
            "—",
            "1. Fetch sequences",
            "2. Clean & preprocess",
            "3. Multiple alignment",
            "4. Conservation analysis",
            "5. Generate plots",
            "6. Build report only",
        ],
    )
    run_single = st.button("Run selected step", use_container_width=True)

    st.divider()
    st.subheader("Data status")
    for label, p in [
        ("Raw FASTA", paths.raw_fasta),
        ("Cleaned", paths.cleaned_fasta),
        ("Alignment", paths.aligned_fasta),
        ("Scores CSV", paths.conservation_csv),
        ("Dataset audit", paths.dataset_audit_csv),
        ("Report", paths.summary_report),
    ]:
        st.write(f"{'✅' if p.exists() else '⬜'} {label}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

st.markdown('<p class="main-header">HIV-1 Evolution Analysis — India (Subtype C)</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Fetch GenBank sequences → clean → align → conservation hotspots → report</p>',
    unsafe_allow_html=True,
)

tab_dash, tab_audit, tab_run, tab_results, tab_files = st.tabs(
    ["Dashboard", "Dataset audit", "Pipeline log", "Results", "Download files"]
)

log_box = st.empty()


def ui_log(msg: str) -> None:
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(msg)


def show_logs() -> None:
    logs = st.session_state.get("logs", [])
    with tab_run:
        st.subheader("Pipeline log")
        if logs:
            st.code("\n".join(logs), language=None)
        else:
            st.info("No runs yet. Click **Run full pipeline** in the sidebar.")


def _safe_count_fasta(path: Path) -> int:
    if not path.exists():
        return 0
    return len(list(SeqIO.parse(path, "fasta")))


def _alignment_shape(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    records = list(SeqIO.parse(path, "fasta"))
    if not records:
        return 0, 0
    return len(records), len(records[0].seq)


def _raw_country_counts() -> tuple[int, int, dict[str, int]]:
    dataset = summarize_dataset(paths)
    if not dataset["raw_count"]:
        return 0, 0, {}
    return (
        dataset["india_count"],
        dataset["non_india_count"],
        dataset["location_counts"],
    )


def _result_card(label: str, value: str | int, hint: str) -> None:
    st.markdown(
        f"""
        <div class="result-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _pct(part: int, whole: int) -> str:
    if not whole:
        return "0%"
    return f"{part / whole:.0%}"


def show_dashboard() -> None:
    with tab_dash:
        raw_n = _safe_count_fasta(paths.raw_fasta)
        clean_n = _safe_count_fasta(paths.cleaned_fasta)
        aln_n, aln_len = _alignment_shape(paths.aligned_fasta)
        india_count, non_india_visible, country_counts = _raw_country_counts()
        score_n = 0
        if paths.conservation_csv.exists():
            score_n = len(pd.read_csv(paths.conservation_csv))

        if raw_n and clean_n and aln_n and score_n:
            st.markdown(
                f"""
                <div class="status-strip">
                    <strong>Current result:</strong> outputs exist, but the dataset needs review.
                    <p>
                        It cleaned {clean_n} sequences, aligned {aln_n} of them, and calculated
                        conservation scores across {score_n} alignment positions. Use the
                        <strong>Dataset audit</strong> tab to understand what records were actually used,
                        then use <strong>Results</strong> for plots and report interpretation.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="status-strip">
                    <strong>No complete run yet.</strong>
                    <p>
                        Click <strong>Run full pipeline</strong> in the sidebar. When it finishes,
                        this dashboard will show the sequence counts, alignment size, data-quality
                        warning, plots, and downloadable files.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            _result_card("Raw sequences", raw_n, "Fetched or loaded from NCBI FASTA.")
        with c2:
            _result_card("Cleaned sequences", clean_n, "After length, ambiguity, and duplicate filters.")
        with c3:
            _result_card("Aligned sequences", aln_n, "Sequences included in the multiple sequence alignment.")
        with c4:
            _result_card("Alignment length", aln_len or "—", "Number of columns used for conservation scoring.")

        st.markdown(
            """
            <div class="section-title">What this app gives the user</div>
            <div class="mini-grid">
                <div class="mini-card">
                    <b>Dataset reality check</b>
                    <p>Shows whether the records look like Indian isolates or a mixed-country search result.</p>
                </div>
                <div class="mini-card">
                    <b>Quality control trail</b>
                    <p>Shows how many sequences survived length, ambiguity, and duplicate filters.</p>
                </div>
                <div class="mini-card">
                    <b>Evolution signal</b>
                    <p>Shows which alignment positions are conserved and whether mutation-hotspot regions were detected.</p>
                </div>
                <div class="mini-card">
                    <b>Submission-ready files</b>
                    <p>Exports FASTA, alignment, conservation CSV, dataset audit CSV, figures, and a markdown report.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if raw_n:
            if non_india_visible:
                counts_text = ", ".join(
                    f"{name}: {count}"
                    for name, count in country_counts.items()
                    if count
                )
                st.markdown(
                    f"""
                    <div class="quality-card">
                        <strong>Data-quality warning: this is not an India-only dataset yet.</strong>
                        <p>
                            The raw FASTA has {raw_n} records, but only {india_count}
                            ({_pct(india_count, raw_n)}) are visibly described as India.
                            {non_india_visible} records do not mention India in their FASTA description.
                            Visible country matches: {counts_text}.
                        </p>
                        <p>
                            This is useful as a pipeline demo, but the report now flags the limitation.
                            For a real India-only result, fetch full GenBank records and filter by source metadata.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="quality-card good">
                        <strong>Dataset check passed at the FASTA-description level.</strong>
                        <p>All loaded raw records visibly match the India filter in their descriptions.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.divider()
        st.markdown("### Recommended review order")
        st.markdown(
            """
            <div class="next-step-grid">
                <div class="next-step">
                    <b>1. Dataset audit</b>
                    <span>Confirm whether the input records match the biological question.</span>
                </div>
                <div class="next-step">
                    <b>2. Results</b>
                    <span>Read the plots as conservation evidence, not as final India-specific evidence yet.</span>
                </div>
                <div class="next-step">
                    <b>3. Download report</b>
                    <span>Use the report after reviewing its dataset limitation and interpretation notes.</span>
                </div>
            </div>
            """
            ,
            unsafe_allow_html=True,
        )


def show_dataset_audit() -> None:
    with tab_audit:
        st.subheader("Dataset audit")
        st.markdown(
            """
            <p class="explainer">
                This tab answers the question a developer or reviewer will ask first:
                <strong>what data did the analysis actually use?</strong> The location is inferred
                from FASTA descriptions, so this is a practical audit rather than a perfect
                GenBank-source check.
            </p>
            """,
            unsafe_allow_html=True,
        )

        audit_df = build_dataset_audit(paths, "raw")
        if audit_df.empty:
            st.info("No raw FASTA records found yet. Run the fetch step or full pipeline first.")
            return
        audit_df.to_csv(paths.dataset_audit_csv, index=False)

        dataset = summarize_dataset(paths)
        loc_counts = (
            audit_df["inferred_location"]
            .value_counts()
            .rename_axis("Inferred location")
            .reset_index(name="Records")
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            _result_card("India-described", dataset["india_count"], "Records whose FASTA description visibly says India.")
        with c2:
            _result_card("Other/unknown", dataset["non_india_count"], "Records that do not visibly say India.")
        with c3:
            _result_card("Unknown year", dataset["unknown_year_count"], "Records where year could not be parsed from FASTA text.")
        with c4:
            _result_card(
                "Length range",
                f'{dataset["length_summary"]["raw_min"]}-{dataset["length_summary"]["raw_max"]}',
                "Shortest to longest raw sequence in nucleotides.",
            )

        if dataset["non_india_count"]:
            st.warning(
                "This dataset is mixed by FASTA description. Do not present the conservation output "
                "as a clean India-only analysis until the fetch/filtering step is made stricter."
            )
        else:
            st.success("Every raw FASTA description visibly matches India.")

        left, right = st.columns([0.9, 1.1])
        with left:
            st.markdown("#### Inferred source distribution")
            st.dataframe(loc_counts, hide_index=True, use_container_width=True)
            st.bar_chart(loc_counts.set_index("Inferred location")["Records"])
        with right:
            st.markdown("#### Sequence quality snapshot")
            quality_df = audit_df[
                [
                    "accession",
                    "length_nt",
                    "ambiguous_fraction",
                    "year",
                    "inferred_location",
                    "is_india_description",
                ]
            ].copy()
            st.dataframe(quality_df, hide_index=True, use_container_width=True)

        st.markdown("#### Raw FASTA descriptions")
        st.caption("These descriptions explain why some records were flagged as non-India.")
        st.dataframe(
            audit_df[["accession", "inferred_location", "description"]],
            hide_index=True,
            use_container_width=True,
        )

        st.markdown(
            """
            <p class="small-note">
                Better final filtering should use full GenBank metadata, especially source qualifiers
                such as country, collection date, isolate, and subtype. FASTA headers alone are a useful
                sanity check but not enough for a defensible biological dataset.
            </p>
            """,
            unsafe_allow_html=True,
        )


def show_results() -> None:
    with tab_results:
        st.subheader("How to read the results")
        st.markdown(
            """
            <p class="explainer">
                Conservation is calculated column by column after alignment. A score near 1.0 means
                almost all sequences share the same nucleotide at that position. Lower scores mean more
                variation. Because the current dataset audit flags mixed locations, read these plots as
                pipeline output first and India-specific evidence only after dataset filtering is fixed.
            </p>
            """,
            unsafe_allow_html=True,
        )
        if paths.conservation_plot.exists():
            st.subheader("Conservation across alignment")
            st.image(str(paths.conservation_plot), use_container_width=True)
        if paths.length_plot.exists():
            st.subheader("Sequence length distribution")
            st.image(str(paths.length_plot), use_container_width=True)
        if paths.conservation_csv.exists():
            st.subheader("Conservation scores (preview)")
            df = pd.read_csv(paths.conservation_csv)
            st.dataframe(df.head(100), use_container_width=True)
            st.line_chart(df.set_index("position")["conservation_score"])
        if paths.summary_report.exists():
            st.subheader("Summary report")
            st.markdown(paths.summary_report.read_text())


def show_downloads() -> None:
    with tab_files:
        outputs = [
            paths.raw_fasta,
            paths.cleaned_fasta,
            paths.aligned_aln,
            paths.aligned_fasta,
            paths.conservation_csv,
            paths.dataset_audit_csv,
            paths.conservation_plot,
            paths.length_plot,
            paths.summary_report,
        ]
        for p in outputs:
            if p.exists():
                mime = "application/octet-stream"
                if p.suffix == ".csv":
                    mime = "text/csv"
                elif p.suffix == ".md":
                    mime = "text/markdown"
                elif p.suffix == ".png":
                    mime = "image/png"
                st.download_button(
                    label=f"Download {p.name}",
                    data=p.read_bytes(),
                    file_name=p.name,
                    mime=mime,
                    key=f"dl_{p.name}",
                )
            else:
                st.write(f"⬜ {p.name} — not generated yet")


# ---------------------------------------------------------------------------
# Execute pipeline
# ---------------------------------------------------------------------------


def execute_full() -> None:
    st.session_state.logs = []
    with st.spinner("Running full pipeline…"):
        try:
            stats, report = run_pipeline(
                output_dir=APP_DIR,
                email=email,
                force_fetch=force_fetch,
                skip_fetch_if_exists=not force_fetch,
                log=ui_log,
            )
            st.session_state.last_stats = stats
            st.session_state.last_report = report
            st.success(
                f"Done! {stats.final_cleaned} cleaned sequences, "
                f"alignment {stats.num_sequences}×{stats.alignment_length}"
            )
        except Exception as e:
            st.error(str(e))
            st.code(traceback.format_exc())


def execute_step(step: str) -> None:
    st.session_state.logs = []
    try:
        if step.startswith("1"):
            n = fetch_sequences(paths, email=email, force=force_fetch, log=ui_log)
            st.success(f"Fetched / cached {n} sequences.")
        elif step.startswith("2"):
            stats = clean_sequences(paths, log=ui_log)
            st.success(f"Cleaned: {stats.final_cleaned} sequences retained.")
        elif step.startswith("3"):
            n, L = run_msa(paths, log=ui_log)
            st.success(f"Alignment: {n} × {L}")
        elif step.startswith("4"):
            df, cons, var = analyze_conservation(paths, log=ui_log)
            st.session_state.conserved = cons
            st.session_state.variable = var
            st.success(f"Conservation: {len(cons)} conserved, {len(var)} variable regions.")
        elif step.startswith("5"):
            df = pd.read_csv(paths.conservation_csv)
            _, cons, var = analyze_conservation(paths, log=ui_log)
            create_plots(paths, df, cons, var, log=ui_log)
            st.success("Plots saved.")
        elif step.startswith("6"):
            from hiv_pipeline import PipelineStats

            stats = PipelineStats()
            if paths.raw_fasta.exists():
                stats.fetched = len(list(SeqIO.parse(paths.raw_fasta, "fasta")))
            if paths.cleaned_fasta.exists():
                stats.final_cleaned = len(list(SeqIO.parse(paths.cleaned_fasta, "fasta")))
            if paths.aligned_fasta.exists():
                aln = list(SeqIO.parse(paths.aligned_fasta, "fasta"))
                stats.num_sequences = len(aln)
                stats.alignment_length = len(aln[0].seq) if aln else 0
            _, cons, var = analyze_conservation(paths, log=ui_log)
            generate_report(paths, stats, cons, var, log=ui_log)
            st.success("Report generated.")
    except Exception as e:
        st.error(str(e))
        st.code(traceback.format_exc())


if run_full:
    execute_full()

if run_single and run_step != "—":
    execute_step(run_step)

show_dashboard()
show_dataset_audit()
show_logs()
show_results()
show_downloads()
