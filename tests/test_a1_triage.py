import pytest
from src.a1_triage import classify_variant, triage, decision_counts, gene_summary, CSV_COLUMNS, rank_variants, results_to_csv

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


EXCLUDED_DECISION ="exclude"
DECISION_KEYS = ("prioritize", "review", "exclude")
IMPACT_KEYS = ("high", "moderate", "low", "modifier")
MEAN_DEPTH_PRECISION = 1

def decision_counts(results: list[dict]) -> dict[str, int]:
    counts = {key: 0 for key in DECISION_KEYS}
    for row in results:
        decision = str(row["decision"]).strip().lower()
        if decision == EXCLUDED_DECISION:
            continue
        impact = str(row["impact"]).strip().lower()
        if impact in counts:
            counts[impact] += 1
    return counts

def gene_summary(results: list[dict]) -> dict[str, dict[str, int | float]]:
    if not results:
        return {}

    grouped: dict[str, dict[str, int]] = {}
    for row in results:
        gene = str(row["gene"]).strip().upper()
        decision = str(row["decision"]).strip().lower()
        depth = int(row["depth"])

        if gene not in grouped:
            grouped[gene] = {
                "total": 0,
                "prioritize": 0,
                "review": 0,
                "exclude": 0,
                "depth_sum": 0,
            }

        grouped[gene]["total"] += 1
        grouped[gene]["depth_sum"] += depth
        if decision in ("prioritize", "review", "exclude"):
            grouped[gene][decision] += 1

    summary: dict[str, dict[str, int | float]] = {}
    for gene in sorted(grouped.keys()):
        stats = grouped[gene]
        mean_depth = round(stats["depth_sum"] / stats["total"], MEAN_DEPTH_PRECISION)
        summary[gene] = {
            "total": stats["total"],
            "prioritize": stats["prioritize"],
            "review": stats["review"],
            "exclude": stats["exclude"],
            "mean_depth": mean_depth,
        }
    return summary


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