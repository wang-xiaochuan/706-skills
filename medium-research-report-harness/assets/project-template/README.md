# {{PROJECT_TITLE}} Research Harness

Slug: `{{PROJECT_SLUG}}`  
Mode: `{{MODE}}`  
Primary language: `{{PRIMARY_LANGUAGE}}`  
Audience: {{AUDIENCE}}  
Initialized: {{DATE}}

## Start here

1. Read `goal.md` and `decisions.md`.
2. Read `state.csv`; only the `ACTIVE` stage may create official stage outputs.
3. Complete the active stage handoff under `stages/` and mark `Status: PASS` only after its gate has actually passed.
4. Run the skill's `check_harness.py` before and after advancing a stage.

## Layers

- `source/`: raw and extracted corpus plus source registers.
- `research/`: coverage, claims, cases, unknowns, and removals.
- `prewriting/`: multidimensional extraction and alignment.
- `writing/`: architecture, conservation, drafts, translation, and terminology.
- `media/`: images and image register.
- `publication/`: builds, complete share package, and reader package.
- `audit/`: research, narrative, publication, and release gates.
- `stages/`: machine-readable handoffs for the fourteen-stage lifecycle.

## Completion

The project is complete only when every row of `state.csv` is `PASSED` and `audit/audit-summary.md` records the final artifact checks.
