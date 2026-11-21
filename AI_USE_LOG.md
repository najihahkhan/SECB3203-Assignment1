# AI USE LOG

<!-- SECB3203 prompt log. Policy: PROPOSED - for approval by the SECB3203 course team before circulation to students. Fill in, then run: python tools/check_ai_log.py AI_USE_LOG.md --assessment <key> -->

- Course: SECB3203
- Assessment: <Assignment 1 >
- Student name: <NUR ANISAH SOLEHAH BINTI MOHD HAMIM>
- Matric no: <A24CS0157>
- Group ID: <METAFOUR>
- AI level: <0, 1 or 2 - see the assessment brief>
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