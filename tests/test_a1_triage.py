from src.a1_triage import classify_variant, triage

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
