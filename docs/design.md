# Design - Variant Triage Service

Write this BEFORE you write the code, then keep it up to date. It is marked by the lecturer.
Use your own words, your own thresholds and your own data. Delete the guidance in italics.

Group ID: <G03>      Thresholds from data/params.json: min_depth = <...>, min_quality = <...>, top_k = <...>

## 1. Decomposition

| Question | Our answer |
|---|---|
| Input |variants.csv: A ccsv file containing the variant call records here all values are read as strings initially.|
| Output |results/triage.csv: Output CSV file keeping all original variant columns and adding 'decision', 'reason' columns in the same row order.|
| Constraints (named thresholds, what happens at exactly the threshold) |Dynamic Parameter: All threshold values must be taken from 'params.json' rather than hardcoded.|
| Rule order and why the order matters |Rules 1 to 6 are checked one by one from top to bottom. Once a rule matches, its decision and reason are returned immediately and the remaining rules are skipped.|
| Out of scope |Clinical diagnosis: This prgram uses synthetic teaching data only and is not meant for real medical or clinical advice.|

## 2. Pseudocode or flowchart of classify_variant

*Give either structured pseudocode (indentation, IF / ELSE, RETURN) or a flowchart (a picture file
committed in docs/ and linked here, or a Mermaid block). Show all six rules.*
FUNCTION classify_variant(row, params):
# Extract and clean input 
depth <- INTEGER (row["depth])
quality <- INTEGER (row["quality"])
gene <- UPPERCASE(STRIP(row["gene"]))
impact <- LOWERCASE(STRIP(row["impact"]))

# Extract thresholds and priority gene set from params 
min_depth <- INTEGER(params["min_depth"])
min_quality <- INTEGER(params["min_quality"])
priority_genes <- SET of UPPERCASE(STRIP(g)) for g in params["priority_genes"]

# Apply rules in strict priority order (first match wins)
IF depth < min_depth
    THEN 
        RETURN ("exclude", "Rule 1: low depth " + depth + " < min_depth " + min_depth)
ELSE IF quality < min_quality
    THEN 
        RETURN ("exclude", "Rule 2: low quality " + quality + " < min_quality " + min_quality)
ELSE IF gene IN priority_genes AND impact IN {"high", "moderate"}
    THEN 
        RETURN ("prioritize", "Rule 3: priority gene " + gene + " with " + impact + " impact") 
ELSE IF gene IN priority_genes AND impact IN {"low", "modifier"}
    THEN 
        RETURN ("review", "Rule 4: priority gene " + gene + " with " + impact + " impact")
ELSE IF gene NOT IN priority_genes AND impact IN {"high", "moderate"}
    THEN 
        RETURN ("review", "Rule 5: non-priority gene " + gene + " with " + impact + " impact")
ELSE 
    RETURN ("exclude", "Rule 6: non-priority gene " + gene + " with " + impact + " impact")

    END IF 
END FUNCTION 


## 3. Hand trace

*Trace the first six rows of YOUR data/variants.csv (v1 to v6) with YOUR thresholds, then two more rows of
your choice that reach rules 3 to 6. Do it by hand BEFORE you run your code, then compare with your code.*

| Variant | Gene | Depth | Quality | Impact | Rule that fires | Decision | Reason |
|---|---|---|---|---|---|---|---|
| v1 | | | | | | | |

## 4. Test plan

*List the cases you will test: normal, boundary (exactly at YOUR thresholds, one below, one above), invalid or
awkward input (empty list, k = 0, k larger than the data, messy text). One line per case.*

| Case ID | Category | Test Scenario / Input Description | Expected Output / Behaviour | 
| --- | --- | --- | --- |
| T01 | Normal | Valid priority gene with 'high' impact,depth and quality well above thresholds. | Classified as '"prioritize"' (Rule 3) and included in top-k output. |
| T02 | Normal | Valid priority gene with 'low' impact,depth and quality well above thresholds. | Classified as '"review"' (Rule 4) |
| T03 | Normal | Valid priority gene with 'moderate' impact,depth and quality well above thresholds. | Classified as '"exclude"' (Rule 5) |
| T04 | Normal | Valid priority gene with 'modifier' impact,depth and quality well above thresholds. | Classified as '"exclude"' (Rule 6) |
| T05 | Boundary | Depth equals `<min_depth>` (exact threshold) and quality equals `<min_quality>` (exact threshold). | Passes Rules 1 and 2; proceeds to gene/impact evaluation (Rules 3–6). |
| T06 | Boundary | Depth equals `<min_depth - 1>` (one below threshold) with high quality and priority gene. | Immediately classified as `"exclude"` (Rule 1). |
| T07 | Boundary | Depth equals `<min_depth + 1>` (one above threshold), quality equals `<min_quality - 1>` (one below). | Passes Rule 1, immediately classified as `"exclude"` (Rule 2). |
| T08 | Boundary | Quality equals `<min_quality + 1>` (one above threshold) with valid depth. | Passes Rules 1 and 2; proceeds to Rules 3–6. |
| T09 | Boundary | `top_k = 0` passed in parameters with valid prioritized variants present. | Report renders normally with an empty prioritized/top-k list (`0` items shown). |
| T10 | Boundary | `top_k` is larger than the total number of prioritized variants (e.g., `top_k = 100` for 5 variants). | Returns all available prioritized variants without raising an `IndexError`. |
| T11 | Awkward | Empty input list (`[]` / CSV with header row only and zero variant rows). | Completes cleanly without crashing; counts are all `0` and report displays empty sections. |
| T12 | Awkward | Messy text formatting in CSV fields (e.g., `"  brca1 "`, `" HIGH\n"`, `"MoDeRaTe"`). | Whitespace stripped and case normalized; matches priority genes and impacts accurately. |
| T13 | Awkward | Tie-breaking on sorting/ranking when two variants share identical priority/scores. | Deterministic ordering applied consistently across repeated runs. |
| T14 | Invalid | Missing required dictionary key or non-numeric string in `depth`/`quality` (e.g., `"N/A"`). | Raises `ValueError` or `KeyError` cleanly as expected by input validation. |
| T15 | Report/CLI | Full end-to-end execution of `build_report(results, params)` and CLI invocation. | Output matches exact required text layout, headers, summary counts, and exit code `0`. |
## 5. Work plan

*Who builds which function, in which order, and how you will review each other's code.*

1. **Stage 1 - Data Loading & Validation (Najihah) :**Implement input parsing and normalization helpers so raw CSV rows and 'params.json' thresholds are cleanly typed before triage logic begins.
2. **Stage 2 - Core triage classification (Anisah) :**Implement 'clasify_variant(rows,params)', following the 6-rule hierarchy in Part 2, along with unit tests for normal and boundary rule conditions.
3. **Stage 3 -Aggregation, ranking & pipeline integration (allisya):**Implement batch processing, summary counts and 'top_k' selection/sorting, plus unit tests for sorting and awkard/edge-case inputs.
4. **Stage 4 -Report formatting, Final polish & QA (humayraa):**Implement 'build_report(results,params)', write CLI/report unit tests in 'tests/test_a1_triage.py', add hints, docstrings and named constant across 'src/a1_trige.py' to pass 'ruff check src' with zero warnings and finalize 'README.md'.

###workflow
* **Peer review checklist:** Before finalizing main, at least one other team member review the code and run pytest and ruff to verify.
* **Final integration & QA prep:** once all modules are merged the whole team conducts a walkthrough of 'src/a1_triage.py' and 'docs/design.md' together so every member can explain any part of the codebase during QA.
