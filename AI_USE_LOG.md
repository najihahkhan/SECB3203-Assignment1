# AI USE LOG

<!-- SECB3203 prompt log. Policy: PROPOSED - for approval by the SECB3203 course team before circulation to students. Fill in, then run: python tools/check_ai_log.py AI_USE_LOG.md --assessment <key> -->

- Course: SECB3203
- Assessment: <Assignment 1 >
- Student name: <NUR ANISAH SOLEHAH BINTI MOHD HAMIM>
- Matric no: <A24CS0157>
- Group ID: <G03>
- AI level: <1>
- Tools cited: <UTM format, e.g. OpenAI (2026). ChatGPT (GPT-5). Retrieved 12 October 2026 from https://chat.openai.com>

## Declaration (tick exactly one)

- [ ] NIL RETURN: I did not use any generative AI tool for this assessment.
- [x] I used AI. Every interaction that influenced my work is logged below. The log is true and complete.

## Entry 1

- Date: 21 November 2026, 4:00 PM
- Tool: Google (2026). Gemini. Retrieved 21 November 2026 from https://gemini.google.com
- Purpose: explain
- Prompt: "Guide me step-by-step on what to do for my Member 1 tasks in SECB3203 Assignment 1 and explain the key concepts I need to understand by the end of the assignment."
- Output: Provided a step-by-step walkthrough covering the 6-rule ordered variant classification logic, input normalization (`strip()`, case folding, integer casting), avoiding input mutation in `triage`, writing boundary/immutability unit tests with Group 3 parameters (`min_depth=12`, `min_quality=75`, `priority_genes`), passing `ruff` linting, and maintaining clean atomic Git commits.
- Verified by: ran pytest, ran ruff check, and compared logic against the docstrings in `src/a1_triage.py` and values in `data/params.json`
- My change: Used the guidance to understand the rule ordering, edge cases, and Git/linting workflow, then wrote and formatted my pseudocode in `docs/design.md`, implemented `classify_variant` and `triage` in `src/a1_triage.py`, and created unit tests in `tests/test_a1_triage.py` using Group 3's exact parameters.

## Entry 2(mayraa testing)

- Date: 21 November 2026, 4:00 PM
- Tool: Google (2026). Gemini. Retrieved 21 November 2026 from https://gemini.google.com
- Purpose: explain
- Prompt: "Guide me step-by-step on what to do for my Member 1 tasks in SECB3203 Assignment 1 and explain the key concepts I need to understand by the end of the assignment."
- Output: Provided a step-by-step walkthrough covering the 6-rule ordered variant classification logic, input normalization (`strip()`, case folding, integer casting), avoiding input mutation in `triage`, writing boundary/immutability unit tests with Group 3 parameters (`min_depth=12`, `min_quality=75`, `priority_genes`), passing `ruff` linting, and maintaining clean atomic Git commits.
- Verified by: ran pytest, ran ruff check, and compared logic against the docstrings in `src/a1_triage.py` and values in `data/params.json`
- My change: Used the guidance to understand the rule ordering, edge cases, and Git/linting workflow, then wrote and formatted my pseudocode in `docs/design.md`, implemented `classify_variant` and `triage` in `src/a1_triage.py`, and created unit tests in `tests/test_a1_triage.py` using Group 3's exact parameters.


Name: ALLISYA MAISARAH BINTI SURAIZAL  Matric No: A24CS0044
## Entry 3

- Date: 22 November 2026, 9:58 PM
- Tool: Google (2026). Gemini. Retrieved 22 November 2026 from https://gemini.google.com
- Purpose: review
- Prompt: "can you check if there is any error in rank_variants part? *attach a screenshot*"
- Output: Confirmed there are no syntax errors and that the sorting order matches the docstring, while identifying potential edge-case issues including a `dict[str, str]` type annotation mismatch in `sort_key`, unhandled `KeyError` for missing keys or unrecognized `decision`/`impact` labels, unhandled `ValueError` for non-integer `quality`/`depth`/`pos` values, and missing boolean validation for `k`.
- Verified by: ran pytest, ran ruff check, and compared logic against the docstrings in `src/a1_triage.py`
- My change: Reviewed the edge-case feedback for `rank_variants`, updated the `sort_key` type annotation and validation handling where needed in `src/a1_triage.py`, and confirmed all unit tests pass.

Name: Najihah Binti Azhan Khan Matric No: A24CS0144
## Entry 1
- Date: 2026-11-22 (Note: Update to the actual date/time you ran this prompt before submission)
- Tool: Google, Gemini, accessed 22 November 2026, https://gemini.google.com/
- Purpose: other (work distribution and project planning)
- Prompt: "I need you to divide this work for 4 members equally" (with SECB3203_assignment1_student.docx attached) followed by "can you do it in bullet points form"
- Output: Proposed a 3-phase equal workload breakdown across 4 team members covering docs/design.md, the 8 functions in src/a1_triage.py, unit tests in tests/test_a1_triage.py, README.md, and minimum Git commit milestones.
- Verified by: Cross-checked the suggested task list against the function specifications, deliverables, and marking rubric (R1–R15, M1–M4) in SECB3203_assignment1_student.docx.
- My change: Adapted the suggested task allocation into our group's work plan and assigned specific functions/sections to each of the 4 members.
- Used in: GROUP_CONTRACT.md and docs/design.md (Work plan section)

## Group signature 
- Signed: Najihah Binti Azhan Khan, A24CS0144, 22/11/2026
- Signed: Alisya Humayraa Binti Mohd Khairani, A24CS0043, 22/11/2026
- Signed: Allisya Maisarah Binti Suraizal, A24CS0044, 22/11/2026
- Signed: Nur Anisah Solehah Binti Mohd Hamim, A24CS0157, 22/11/2026