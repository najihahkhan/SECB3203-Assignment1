# Design - Variant Triage Service

Write this BEFORE you write the code, then keep it up to date. It is marked by the lecturer.
Use your own words, your own thresholds and your own data. Delete the guidance in italics.

Group ID: <G03>      Thresholds from data/params.json: min_depth = <...>, min_quality = <...>, top_k = <...>
Group ID: <METAFOUR>      Thresholds from data/params.json: min_depth = <...>, min_quality = <...>, top_k = <...>

## 1. Decomposition

| Question | Our answer |
|---|---|
| Input | |
| Output | |
| Constraints (named thresholds, what happens at exactly the threshold) | |
| Rule order and why the order matters | |
| Out of scope | |

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

## 5. Work plan

*Who builds which function, in which order, and how you will review each other's code.*
