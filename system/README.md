# Free Research system (v1.10)

Instructions and skills that let an off-the-shelf coding agent (Claude Code or Codex CLI) choose its own research question, carry out one study, take one AI review and submit a revised paper, with a human only granting permissions, resuming after stops and passing on the review.

There is no orchestration code. Each role is a text document given to an ordinary agent session; the only script fills in the per-run fields and copies the files into the research workspace.

## Layout

```
instructions/
  input_prompt.md          research instructions (template; first message of the research session)
  review_prompt.md         review instructions (template; first message of the review session)
skills/
  research-question/       topic and question selection, including the critique by another model
    SKILL.md
    references/critique-request.md
  peer-review/             review procedure and report format
    SKILL.md
operator/
  prepare_run.py           fills the templates for one run and deploys them with the skills
  OPERATIONS.md            the operator's protocol: fixed messages, session settings, new-machine setup
CHANGES.md                 changes from the previous version
```

## How the parts fit together

| Part | Used by | When |
|---|---|---|
| `input_prompt.md` | researcher | whole run: request, readers, AI API rules, conditions (12 h, 10 GiB, 2 processes, 30 min per process, USD 20 API budget), permissions, records, paper, verifiability, submission, review response, safety |
| `skills/research-question` | researcher | topic selection (§2.1 of the research instructions), before the main plan |
| critic (`references/critique-request.md`) | one API call by the researcher | step 6 of the research-question skill |
| `review_prompt.md` + `skills/peer-review` | reviewer, a different model in a separate session | after the tag `submission-1` |
| `OPERATIONS.md` | operator | start, stops, review handoff |

Design choices:
- **The instructions name the skill files, and the agent reads them by path.** Skill discovery is not relied on, so a required step cannot be skipped because a skill was not triggered, and the research sessions can keep all other skills disabled (`OPERATIONS.md`). The skills are still standard `SKILL.md` folders and can be installed as ordinary skills elsewhere.
- **Independence comes from separate sessions, not from the skills.** The reviewer is a different model in a different session that cannot see the researcher's context, and the critic is a different model reached only through the API with a fixed request. Do not run the peer-review skill inside the research session.
- **Every run records exactly what it was given.** The researcher saves the instruction text as `input_prompt.md` and copies the research-question skill into `input_skills/`. The reviewer does the same with the review instruction and the peer-review skill.
- **Filled instructions differ only in four fields** (version label, run number, workspace path, reviewer model). `prepare_run.py --check` re-fills them and compares with the workspace.

## Using the skills elsewhere

Copy a skill folder into your agent's skills directory (for example `~/.claude/skills/` for Claude Code or `~/.agents/skills/` for Codex). The skills refer to "the run instructions" for the conditions they need (time limit, compute, AI API budget, the critic model, the intended readers, the safety rules); supply those in your own instructions, or adapt `instructions/input_prompt.md`.

## Status

- Version 1.10 is the first English version. It was used in the pilot run-014 (2026-10-25) and frozen on 2026-10-26. Runs 015–018 used it unchanged as v1.10.1–v1.10.4, which differ only in the version and run number (`CHANGES.md`).
- Licence: `operator/prepare_run.py` under the MIT License; the instructions, skills and documents under CC BY 4.0.
