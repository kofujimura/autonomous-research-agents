# Evaluation

- `preregistration.md`: the protocol fixed before the evaluation runs (system files and their SHA-256, models, limits, inclusion rules).
- `amendment-1.md`: the change made after three runs (the pilot run-014 counted as the first run), reported as a deviation.
- `e1-procedure.md`: the external AI evaluation (E1), fixed before the first review, with every later change and its time.
- `e1/`: prompts (`prompt.md` for the Markdown sources, `prompt-pdf.md` for the PDFs), output schema, scripts (`prepare.py`, `run_e1.py`, `analyze.py`), the reviews (`reviews/<reviewer>/run-NNN.rK.json`), the raw replies with search queries and sources (`logs/`), the request log with usage and cost (`runs.jsonl`) and the summary (`results.md`, `results.json`). Reviewer keys: `gemini` (Gemini 4 Argon on Markdown), `gemini-pdf` (Gemini 4 Argon on PDF), `muse` (Muse Wonder on PDF). The scripts read the papers from the original workspace paths; the papers themselves are in `../papers/`.
- `inputs/run-NNN.jsonl`: every input sent to the research session during each run, from the agent's input history: the start message (the filled instruction document, shortened here; the full text is `runs/run-NNN/input_prompt.md`), the fixed resumption messages and the review relay (shortened; the full text is `reviews/review-NNN/review-1.md`).
