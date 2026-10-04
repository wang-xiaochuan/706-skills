# Evaluation notes

- `evals.json` contains three end-to-end scenarios: new continuous research, revision with conservation, and plan-only design.
- `trigger-evals.json` contains ten positive and ten near-miss trigger queries.
- `scripts/self_test.py` is the deterministic acceptance test for scaffold creation, stage advancement, and invalid-state detection.
- Agent-vs-baseline benchmark runs are intentionally not stored in the skill itself. Run them in a sibling workspace when the environment permits independent agents; do not turn benchmark outputs into bundled runtime instructions.
