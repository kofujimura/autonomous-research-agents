# Evaluation phase: pre-registration

Written 2026-10-26, before run-015 (the first evaluation run) was started. Decisions are the human author's: the evaluation phase, its size and the human evaluation (2026-10-25), the models (2026-10-25, for the pilot, kept as is), and freezing v1.10 without changes after the pilot (2026-10-26). The management agent wrote this text.

## 1. System under evaluation

v1.10, frozen after the pilot run-014. The package is `ai-free-research-system/`. SHA-256 of the frozen files:

| File | SHA-256 |
|---|---|
| `instructions/input_prompt.md` | 74f1f4adbce50a95c1414dd39546a6e3850d4f1c3ee899d8ea968a7846e453d4 |
| `instructions/review_prompt.md` | 864a90beedb6ee75bd61d91373c7d0b9ad5cc2b90a3f208b1985cd6c5ccd8b33 |
| `skills/research-question/SKILL.md` | 55fc2c084a593bc8c1a954bc133e349c7538625c2084a677c2eb57828606e2e6 |
| `skills/research-question/references/critique-request.md` | 1322b5db2015ee2b2b08a55760ee7196420d6ccb1b8fe916f66915947ca6f64c |
| `skills/peer-review/SKILL.md` | 0ac39a61ee69c40d98d3dbaff4c4801ab966b97afb8f81d7f94ce3626a55aa52 |
| `operator/prepare_run.py` | 1f5f0a97b608cbf2acaf23fa4baa6f605df29a0c2be53dcc2bddba74d5f5bef9 |

## 2. Runs

- Five consecutive runs: run-015 to run-019, filled as versions v1.10.1 to v1.10.5 by `prepare_run.py`. The filled instructions differ from the pilot's only in the version number and the run number. Each deployment is checked with `prepare_run.py --check`, and its SHA-256 values are recorded in the run ledger.
- The pilot run-014 is not counted. This was decided on 2026-10-25, before the pilot started.
- One run at a time, never in parallel.

## 3. Models and settings (same as the pilot)

- **Researcher:** gpt-6.1-sol, reasoning effort xhigh, in Codex CLI. It uses a research-only `CODEX_HOME` and the launch flags in `operator/OPERATIONS.md` (web search live; computer use, browser, memories, apps and plugins disabled; `-a on-request`).
- **Critic of topic candidates:** gpt-6-astra, reasoning effort xhigh, through the OpenAI API. It is called once, as the research-question skill specifies.
- **Reviewer:** Opus 5.5, effort xhigh, in Claude Code. It uses a research-only configuration directory and permission mode auto.
- **Operator:** a management agent (Claude Code, Opus 5.5) and the human author.
  - The agent starts sessions and sends only the fixed messages in `OPERATIONS.md`: the start message, the resume messages and the review handoff.
  - The human sets the API key and decides every permission request.
  - Nobody gives the research or review sessions research advice.
- **Machine and workspace:**
  - Machine: MacBook Pro (M3 Pro, 18 GiB, no discrete GPU).
  - Research workspace: `/Users/fujimura/Research/ai-free-research-en/`. It also holds the earlier `run-*` and `review-*` directories, which the instructions forbid reading.
  - The Codex CLI version is recorded for every run. If it changes, the change is recorded and the short isolation check is repeated before the run.

## 4. Inclusion rules

- Every run whose start message has been sent is counted and reported, whatever its outcome. This includes no submission, a missed deadline, or a crash.
- A launch that fails before the research session begins work is moved out of the workspace and relaunched under the same ID. Examples: the session does not start, or the API key is missing. All such attempts are reported.
- No run is excluded, replaced or repeated after its result has been seen.
- If the human decides to add a run, it is numbered after the series and reported separately, with the reason.

## 5. No changes during the series

The following stay fixed:

- the instructions, the skills and the critique request;
- the models and their reasoning efforts;
- the fixed operator messages;
- the time limits (12 hours of research and 2 hours of review response, excluding stops caused by usage limits);
- the resource limits.

If a change becomes unavoidable, the series stops at that point and the change is reported. Examples: a model is withdrawn, or access to the account or the API is lost. Runs after such a change form a separate series.

## 6. What is recorded

- **For every run:**
  - the run ledger, which covers times, stops, deadline extensions, permission requests, cost (the research side's record and the provider dashboard) and the Codex version;
  - the management agent's evaluation, written with the same template as the development phase;
  - the topic candidates and their classification;
  - the AI review: its verdict, scores, findings and severities, and the research side's responses.
- **Human evaluation (E2):** by the author and 2–3 Japanese colleague researchers.
  - The form and the procedure are fixed and recorded before any colleague reads any paper.
  - The author's ratings are reported separately from the colleagues', because the author knows how the runs were made.
- **Re-review by AI reviewers (E1) on these runs:** its procedure is fixed and recorded before it is run. When the researcher is a GPT model, reviewers from at least two model families are used.
- Finalized run directories are not changed. Later findings go into the management records.
