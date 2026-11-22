# Evaluation

- `preregistration.md`: the protocol fixed before the evaluation runs (system files and their SHA-256, models, limits, inclusion rules).
- `amendment-1.md`: the change made after three runs (the pilot run-014 counted as the first run), reported as a deviation.
- `amendment-2.md`, `amendment-3.md`, `amendment-4.md`: changes to the human evaluation (E2):
  - (2) E2 is reported in the journal version of the paper rather than in a separate paper, under reporting rules fixed before any rating existed;
  - (3) the author does not rate the papers;
  - (4) the ratings of H2, which arrived after the deadline, are used.

  The record and the deviations from the plan are in `e2/README.md`.
- `e1-procedure.md`: the external AI evaluation (E1), fixed before the first review, with every later change and its time.
- `e1/`: prompts (`prompt.md` for the Markdown sources, `prompt-pdf.md` for the PDFs), output schema, scripts (`prepare.py`, `run_e1.py`, `analyze.py`), the reviews (`reviews/<reviewer>/run-NNN.rK.json`), the raw replies with search queries and sources (`logs/`), the request log with usage and cost (`runs.jsonl`) and the summary (`results.md`, `results.json`). Reviewer keys: `gemini` (Gemini 4 Argon on Markdown), `gemini-pdf` (Gemini 4 Argon on PDF), `muse` (Muse Wonder on PDF). The scripts read the papers from the original workspace paths; the papers themselves are in `../papers/`.
- `e2/`: the human evaluation (E2):
  - the rating form as the raters used it;
  - the procedure and the summary method;
  - the record, and the deviations from the plan.

  The individual responses are not released. The numbers are reported in the journal version of the paper.
- `inputs/run-NNN.jsonl`: every input sent to the research session during each run, from the agent's input history: the start message (the filled instruction document, shortened here; the full text is `runs/run-NNN/input_prompt.md`), the fixed resumption messages and the review relay (shortened; the full text is `reviews/review-NNN/review-1.md`).

## About amendments 2–4

- They were added on 2026-11-22, unchanged. Their last line ("not yet in the public release") was true when they were written.
- They refer to files by their paths in the author's workspace:
  - `../e1-eval/` is `e1/` here. Its README, a working note, is not released.
  - These are not released: `../e2-eval/README.md` (the management agent's working record of E2, in Japanese), `../e2-eval/request-email.md` (the request e-mail) and `../ieice/` (the source of the journal paper).
- What the amendments cite from those files is given in `e2/README.md`.
