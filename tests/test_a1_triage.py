import json
from pathlib import Path
import subprocess
import sys
import pytest
from src.a1_triage import (
    CSV_COLUMNS,
    build_report,
    classify_variant,
    decision_counts,
    gene_summary,
    impact_counts,
    rank_variants,
    results_to_csv,
    triage,
)

G03_PARAMS = {
    "min_depth": 12,
    "min_quality": 75,
    "priority_genes": ["ATM", "PTEN", "EGFR", "APC", "BRCA2"],
    "top_k": 8,
}


def test_classify_variant_g03_boundaries_and_rules():
    """Verify all 6 rules and exact threshold boundary behavior for G03."""
    # Rule 1: depth < 12 -> exclude (11 fails, 12 passes)
    d1, r1 = classify_variant(
        {"gene": "BRCA2", "impact": "high", "depth": 11, "quality": 90},
        G03_PARAMS,
    )
    assert d1 == "exclude"
    assert "depth" in r1.lower()

    # Rule 2: quality < 75 -> exclude (74 fails, 75 passes)
    d2, r2 = classify_variant(
        {"gene": "BRCA2", "impact": "high", "depth": 12, "quality": 74},
        G03_PARAMS,
    )
    assert d2 == "exclude"
    assert "quality" in r2.lower()

    # Rule 3: priority gene + high/moderate at exact thresholds -> prioritize
    d3, _ = classify_variant(
        {"gene": "ATM", "impact": "moderate", "depth": 12, "quality": 75},
        G03_PARAMS,
    )
    assert d3 == "prioritize"

    # Rule 4: priority gene + low/modifier -> review
    d4, _ = classify_variant(
        {"gene": "PTEN", "impact": "low", "depth": 20, "quality": 85},
        G03_PARAMS,
    )
    assert d4 == "review"

    # Rule 5: non-priority gene + high/moderate -> review
    d5, _ = classify_variant(
        {"gene": "TP53", "impact": "high", "depth": 20, "quality": 85},
        G03_PARAMS,
    )
    assert d5 == "review"

    # Rule 6: non-priority gene + low/modifier -> exclude
    d6, _ = classify_variant(
        {"gene": "TP53", "impact": "modifier", "depth": 20, "quality": 85},
        G03_PARAMS,
    )
    assert d6 == "exclude"


def test_triage_messy_inputs_and_immutability():
    """Verify whitespace/case normalization, string numbers, and no input mutation."""
    original_rows = [
        {"gene": "  brca2 ", "impact": " HIGH ", "depth": "15", "quality": "80"},
        {"gene": " egfr", "impact": "Modifier ", "depth": "12", "quality": "75"},
    ]
    snapshot = [dict(row) for row in original_rows]

    triaged = triage(original_rows, G03_PARAMS)

    assert len(triaged) == len(original_rows)
    assert triaged[0]["decision"] == "prioritize"
    assert "reason" in triaged[0]
    assert triaged[1]["decision"] == "review"
    assert "reason" in triaged[1]

    # Ensure original input list and dicts were not mutated
    assert original_rows == snapshot
    assert "decision" not in original_rows[0]


def test_decision_and_impact_counts() -> None:
    """Verify decision_counts includes all keys and impact_counts skips excluded rows."""
    rows = [
        {"decision": "prioritize", "impact": "high"},
        {"decision": "review", "impact": "moderate"},
        {"decision": "exclude", "impact": "high"},
    ]
    assert decision_counts(rows) == {"prioritize": 1, "review": 1, "exclude": 1}
    assert impact_counts(rows) == {"high": 1, "moderate": 1, "low": 0, "modifier": 0}
    assert decision_counts([]) == {"prioritize": 0, "review": 0, "exclude": 0}


def test_gene_summary_alphabetical_and_mean_depth() -> None:
    """Verify per-gene counts, alphabetical key order, and 1-decimal mean depth."""
    rows = [
        {"gene": "TP53", "decision": "review", "depth": 30},
        {"gene": "BRCA2", "decision": "prioritize", "depth": 40},
        {"gene": "BRCA2", "decision": "exclude", "depth": 11},
    ]
    summary = gene_summary(rows)
    assert list(summary.keys()) == ["BRCA2", "TP53"]
    assert summary["BRCA2"] == {
        "total": 2,
        "prioritize": 1,
        "review": 0,
        "exclude": 1,
        "mean_depth": 25.5,
    }
    assert gene_summary([]) == {}


def test_rank_variants_order_tie_breakers_and_k_cases() -> None:
    """Cover ranking tie-breakers, exclusion filtering, k=0, k > total, and negative k."""
    rows = [
        {
            "variant": "v_excl",
            "gene": "G1",
            "chrom": "chr1",
            "pos": 50,
            "depth": 90,
            "quality": 95,
            "impact": "high",
            "decision": "exclude",
            "reason": "Rule 1 depth below threshold",
        },
        {
            "variant": "v_pos_later",
            "gene": "G1",
            "chrom": "chr1",
            "pos": 300,
            "depth": 60,
            "quality": 90,
            "impact": "high",
            "decision": "prioritize",
            "reason": "Rule 3 priority gene G1 with high impact",
        },
        {
            "variant": "v_pos_earlier",
            "gene": "G1",
            "chrom": "chr1",
            "pos": 150,
            "depth": 60,
            "quality": 90,
            "impact": "high",
            "decision": "prioritize",
            "reason": "Rule 3 priority gene G1 with high impact",
        },
        {
            "variant": "v_review",
            "gene": "G2",
            "chrom": "chr1",
            "pos": 100,
            "depth": 80,
            "quality": 99,
            "impact": "high",
            "decision": "review",
            "reason": "Rule 5 non-priority gene G2 with high impact",
        },
    ]

    ranked = rank_variants(rows, k=10)
    assert [r["variant"] for r in ranked] == [
        "v_pos_earlier",
        "v_pos_later",
        "v_review",
    ]
    assert rank_variants(rows, k=0) == []

    with pytest.raises(ValueError):
        rank_variants(rows, k=-1)


def test_results_to_csv_header_and_rows() -> None:
    """Cover exact CSV header and newline-terminated lines."""
    rows = [
        {
            "variant": "v1",
            "gene": "G1",
            "chrom": "chr1",
            "pos": 100,
            "depth": 50,
            "quality": 85,
            "impact": "high",
            "decision": "prioritize",
            "reason": "Rule 3 priority gene G1 with high impact",
        },
    ]

    csv_text = results_to_csv(rows)
    lines = csv_text.splitlines(keepends=True)

    assert lines[0] == ",".join(CSV_COLUMNS) + "\n"
    assert lines[1] == (
        "v1,G1,chr1,100,50,85,high,prioritize,"
        "Rule 3 priority gene G1 with high impact\n"
    )


def test_format_report_structure_and_content() -> None:
    """Cover report structure, header, and content for a small example."""
    rows = [
        {
            "variant": "rs101",
            "gene": "BRCA2",
            "chrom": "chr13",
            "pos": 32315474,
            "depth": 45,
            "quality": 92,
            "impact": "high",
            "decision": "prioritize",
            "reason": "Rule 3 priority gene BRCA2 with high impact",
        },
        {
            "variant": "rs202",
            "gene": "TP53",
            "chrom": "chr17",
            "pos": 7675088,
            "depth": 30,
            "quality": 88,
            "impact": "moderate",
            "decision": "review",
            "reason": "Rule 5 non-priority gene TP53 with moderate impact",
        },
        {
            "variant": "rs303",
            "gene": "EGFR",
            "chrom": "chr7",
            "pos": 5524231,
            "depth": 50,
            "quality": 67,
            "impact": "low",
            "decision": "exclude",
            "reason": "Rule 2 quality below threshold",
        },
    ]

    report = build_report(rows, G03_PARAMS)
    assert isinstance(report, str)
    assert report.startswith("Clinical Variant Triage Report")
    assert report.count("\n") > 5


def test_cli_execution_and_output(tmp_path: Path) -> None:
    """Verify CLI creates triage.csv and report.txt and exits 0."""
    input_csv = tmp_path / "variants.csv"
    input_csv.write_text(
        "variant,gene,chrom,pos,depth,quality,impact\n"
        "rs101,BRCA2,chr13,32315474,45,92,high\n"
        "rs202,TP53,chr17,7675088,30,88,moderate\n"
        "rs303,EGFR,chr7,5524231,50,67,low\n",
        encoding="utf-8",
    )
    params_json = tmp_path / "params.json"
    params_json.write_text(json.dumps(G03_PARAMS), encoding="utf-8")
    out_dir = tmp_path / "results"

    result = subprocess.run(
        [sys.executable, "src/a1_triage.py", str(input_csv), str(params_json), str(out_dir)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.returncode == 0
    assert (out_dir / "triage.csv").exists()
    assert (out_dir / "report.txt").exists()