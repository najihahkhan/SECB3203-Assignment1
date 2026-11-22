
"""Assignment 1 - clinical variant triage service (synthetic teaching data only).

Reads variant calls, applies ordered triage rules with named thresholds, records a
reason for every decision and produces summaries, a ranked top-k list, a CSV text
and a short text report. Nothing here is clinical advice.
"""
import csv
import json
import sys
from pathlib import Path

DECISIONS = ("prioritize", "review", "exclude")
IMPACT_ORDER = ("high", "moderate", "low", "modifier")
PRIORITY_IMPACTS = frozenset({"high", "moderate"})
CSV_COLUMNS = [
    "variant", "gene", "chrom", "pos", "depth", "quality", "impact", "decision", "reason",
]
CLI_ARGUMENTS = 3

HIGH_IMPACTS = {"high", "moderate"}
LOW_IMPACTS = {"low", "modifier"}

DECISION_PRIORITIZE = "prioritize"
DECISION_REVIEW = "review"
DECISION_EXCLUDE = "exclude"


def load_variants(path) -> list[dict]:
    """Read variants.csv into a list of dicts. Every value stays text (Week 6 explains how)."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_params(path) -> dict:
    """Read the group parameters (data/params.json) into a dict."""
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def classify_variant(row: dict, params: dict) -> tuple[str, str]:

    """Classify a single variant row against the six ordered triage rules."""

    depth = int(row["depth"])
    quality = int(row["quality"])
    gene = str(row["gene"]).strip().upper()
    impact = str(row["impact"]).strip().lower()

    min_depth = int(params["min_depth"])
    min_quality = int(params["min_quality"])
    priority_genes = {str(g).strip().upper() for g in params["priority_genes"]}

    if depth < min_depth:
        return (
            DECISION_EXCLUDE,
            f"Rule 1: depth {depth} below min_depth {min_depth}",
        )
    if quality < min_quality:
        return (
            DECISION_EXCLUDE,
            f"Rule 2: quality {quality} below min_quality {min_quality}",
        )
    if gene in priority_genes and impact in HIGH_IMPACTS:
        return (
            DECISION_PRIORITIZE,
            f"Rule 3: priority gene {gene} with {impact} impact",
        )
    if gene in priority_genes and impact in LOW_IMPACTS:
        return (
            DECISION_REVIEW,
            f"Rule 4: priority gene {gene} with {impact} impact",
        )
    if impact in HIGH_IMPACTS:
        return (
            DECISION_REVIEW,
            f"Rule 5: non-priority gene {gene} with {impact} impact",
        )
    return (
        DECISION_EXCLUDE,
        f"Rule 6: non-priority gene {gene} with {impact} impact",
    )

def triage(rows: list[dict], params: dict) -> list[dict]:
    """Classify all rows and return a new list of new dicts without mutating inputs."""
    results = []
    for row in rows:
        decision, reason = classify_variant(row, params)
        new_row = dict(row)
        new_row["decision"] = decision
        new_row["reason"] = reason
        results.append(new_row)
    return results


EXCLUDED_DECISION= "exclude"
DECISION_KEYS= ("prioritize", "review", "exclude")
IMPACT_KEYS= ("high", "moderate", "low", "modifier")

def decision_counts(results: list[dict]) -> dict[str, int]:
    """Number of results per decision; keys are always prioritize, review, exclude (in order)."""
    counts= {key: 0 for key in DECISION_KEYS}
    for row in results:
        decision= str(row["decision"].strip().lower())
        if decision in counts:
            counts[decision] += 1
    return counts



def impact_counts(results: list[dict]) -> dict[str, int]:
    """Impact counts over variants that were NOT excluded.

    Keys are always high, moderate, low, modifier (in that order), zeros included.
    """
    counts = {key: 0 for key in IMPACT_KEYS}
    for row in results:
        decision = str(row["decision"].strip().lower())
        if decision != EXCLUDED_DECISION:
            impact = str(row["impact"].strip().lower())
            if impact in counts:
                counts[impact] += 1
    return counts


def gene_summary(results: list[dict]) -> dict[str, dict]:
    """Per-gene summary, genes in alphabetical order.

    Each value is {"total": n, "prioritize": a, "review": b, "exclude": c, "mean_depth": d}
    where mean_depth is the mean depth of ALL the gene's variants, rounded to 1 decimal.
    """
    if not results:
        return {}

    grouped: dict[str, dict[str, int]] = {}
    for row in results:
        gene = str(row["gene"]).strip().upper()
        decision= str(row["decision"]).strip().lower()
        depth= int(row["depth"])

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
        mean_depth = round(stats["depth_sum"] / stats["total"], 1)
        summary[gene] = {
            "total": stats["total"],
            "prioritize": stats["prioritize"],
            "review": stats["review"],
            "exclude": stats["exclude"],
            "mean_depth": mean_depth,
        }
    return summary

MIN_K: int = 0

DECISION_PRIORITY_ORDER: dict[str, int] = {
    "prioritize": 0,
    "review": 1,
}

IMPACT_PRIORITY_ORDER: dict[str, int] = {
    "high": 0,
    "moderate": 1,
    "low": 2,
    "modifier": 3,
}


def rank_variants(results: list[dict], k: int) -> list[dict]:
    """Top k variants that were not excluded, best first.

    Sort by: prioritize before review, then impact (high first), then higher quality,
    then higher depth, then smaller pos. Fewer than k are returned if fewer qualify.

    Raises:
        ValueError: if k is negative.
    """
    if k < 0 :
        raise ValueError("k must be a non-negative integer")
    if k == 0 :
        return []

    candidates = [
        item
        for item in results
        if str(item["decision"]).strip().casefold()!= "exclude"]

    def sort_key(item: dict[str, str]) -> tuple[int, int, int, int, int]:
        return(
            DECISION_PRIORITY_ORDER[str(item["decision"]).strip().casefold()],
            IMPACT_PRIORITY_ORDER[str(item["impact"]).strip().casefold()],
            -int(str(item["quality"]).strip()),
            -int(str(item["depth"]).strip()),
            int(str(item["pos"]).strip())
        )

    return sorted(candidates, key=sort_key)[:k]


def results_to_csv(results: list[dict]) -> str:
    """CSV text: a header line (CSV_COLUMNS) and one line per result in the given order.

    Every line ends with a newline. Reason text contains no commas, so no quoting is needed.
    """
    header = ",".join(CSV_COLUMNS) + "\n"
    if not results:
        return header

    lines = [header]
    for row in results:
        values = [str(row[col]) for col in CSV_COLUMNS]
        lines.append(",".join(values) + "\n")

    return "".join(lines)


def build_report(results: list[dict], params: dict) -> str:
    """Short text report; the line formats are fixed so the report can be checked.

    Lines: title, 'Thresholds: min_depth=D min_quality=Q', 'Priority genes: A, B, ...',
    'Variants: N', one 'decision: count' line per decision, a blank line,
    'Top K variants' and then 'rank. variant | gene | impact | decision' lines.
    """
    min_depth = int(params["min_depth"])
    min_quality = int(params["min_quality"])
    top_k = int(params["top_k"])
    priority_genes = sorted({str(g).strip().upper() for g in params["priority_genes"]})
    decision_counts_dict = decision_counts(results)
    top_variants = rank_variants(results, top_k)

    lines = [
        "Clinical Variant Triage Report",
        f"Thresholds: min_depth={min_depth} min_quality={min_quality}",
        f"Priority genes: {', '.join(priority_genes)}",
        f"Variants: {len(results)}",
    ]

    for decision, count in decision_counts_dict.items():
        lines.append(f"{decision}: {count}")

    lines.append("")
    lines.append("Top K variants")
    for rank, variant in enumerate(top_variants, start=1):
        lines.append(
            f"{rank}. {variant['variant']} | {variant['gene']} | "
            f"{variant['impact']} | {variant['decision']}"
        )

    return "\n".join(lines) + "\n"



def main(argv: list[str] | None = None) -> int:
    """Command line: python src/a1_triage.py VARIANTS_CSV PARAMS_JSON OUT_DIR."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != CLI_ARGUMENTS:
        print("usage: python src/a1_triage.py data/variants.csv data/params.json results")
        return 2
    variants_path, params_path, out_dir = args
    rows = load_variants(variants_path)
    params = load_params(params_path)
    results = triage(rows, params)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "triage.csv").write_text(results_to_csv(results), encoding="utf-8")
    report = build_report(results, params)
    (out / "report.txt").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
