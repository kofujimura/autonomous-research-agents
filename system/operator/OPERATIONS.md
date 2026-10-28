# Operating a run

This is the operator's side of the Free Research system: how a run is prepared, started, resumed and reviewed. The operator is a human, optionally assisted by a management agent that sends only the fixed messages below. The operator never gives research advice.

## Roles

| Role | Runs as | Reads | Writes |
|---|---|---|---|
| Researcher | a coding agent session (Claude Code or Codex CLI), started in the research workspace | the filled `input_prompt_v<version>.md` (first message), `skills/research-question/` | `run-<NNN>/` only |
| Critic | one OpenAI Responses API call made by the researcher (step 6 of the research-question skill) | the candidate list the researcher sends | nothing |
| Reviewer | a separate coding agent session with a different model, started in the research workspace without the API key | the filled `review_prompt_v<version>.md` (first message), `skills/peer-review/`, `run-<NNN>/` at tag `submission-1` | `review-<NNN>/` only |
| Operator | human (+ management agent) | screens of the sessions | nothing in the research workspace except what `prepare_run.py` deploys |

## Messages the operator may send

Only these. Anything else reaches the researcher as advice and must be recorded by it as `scientific_feedback`, which is a deviation from the conditions.

| When | Message (exact text) | Who |
|---|---|---|
| Start | the whole filled `input_prompt_v<version>.md` as the first message | operator |
| Resume after a stop caused by the usage limit | `Resuming after a stop caused by the AI usage limit.` | operator |
| Resume after any other stop (service errors, etc.) | `Resuming after a stop.` | operator |
| Answer to a permission request | `PERM-001: granted / denied / granted with conditions. Scope: …` | human only |
| Review handoff | the whole `review-<NNN>/review-1.md`, whose first line is `REVIEW-1` | operator |

The research instructions exclude a stop from the deadline only when the stop reason can be confirmed from the runtime's display or from the resume message, so use the usage-limit text only for usage-limit stops. Claude Code resumes by itself when the limit resets; send the resume text only if it does not. Never choose extra usage, a plan upgrade, or a switch to another model offered by the runtime.

## One run, step by step

1. **Prepare.** Fill and deploy the instructions and skills:
   `python3 operator/prepare_run.py --version <v> --run <NNN> --workspace <abs path> --reviewer-model "<model, effort>"`
   It refuses to overwrite anything that differs, so the skills stay identical across the runs of one version. Record the printed SHA-256 values.
   For each later run of the same text, use the next patch version (for example 1.10.1, then 1.10.2), since the filled files carry the run number.
2. **Check the workspace.** It must contain only the filled instructions, `skills/`, and earlier `run-*`/`review-*` directories (or nothing else at all for an independent series). No `CLAUDE.md`, `AGENTS.md`, `.claude/`, `.codex/`, `.agents/`, notes or summaries of earlier runs. The agent's memory for the workspace path must be empty.
3. **API key.** In the researcher's terminal only, export `FREE_RESEARCH_OPENAI_API_KEY` from a file outside the workspace (permissions 600). Check with `env | grep -c '^FREE_RESEARCH_OPENAI_API_KEY='` (prints 1, not the value). Do not set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` there (the session itself could then be billed to the API). Make one small call to the critic model to confirm the key's project can use it.
4. **Start the researcher** (settings below), with the filled instruction as the first message.
5. **Watch.** Resume after stops with the fixed texts. Permission requests are answered by the human.
6. **Review.** When the tag `submission-1` appears, start the reviewer (settings below; no API key in its environment). When `review-1.md` is complete and starts with `REVIEW-1`, send its whole text to the researcher.
7. **End.** The run is final when the tag `final` appears. After that, nothing is written into `run-<NNN>/` or `review-<NNN>/`; later notes go to the operator's own records outside the workspace.

## Session settings

The research and review sessions use their own configuration directories so that the operator's skills, rules, memory, plugins, MCP servers and connected apps are not visible to them.

**Claude Code** (researcher or reviewer)

```sh
cd <workspace> && env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY \
  CLAUDE_CONFIG_DIR="$HOME/.claude-research" CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 ENABLE_CLAUDEAI_MCP_SERVERS=false \
  claude --disallowedTools Artifact,ArtifactComments,ArtifactData,RemoteTrigger,PushNotification,ListAgents,SendMessage,DesignSync \
    --strict-mcp-config --no-chrome --disable-slash-commands \
    --model <model> --effort xhigh --permission-mode auto "$(cat input_prompt_v<version>.md)"
```

- Log in once with `CLAUDE_CONFIG_DIR="$HOME/.claude-research" claude` (subscription), trust the workspace folder, and exit without sending anything. `settings.json` there should contain only `"autoMemoryEnabled": false`.
- `--disable-slash-commands` disables all skills, including skills synced from the claude.ai account. This is intended: the system's own skills are not loaded through skill discovery but read by path, because the instructions name the file. This keeps the operator's skills hidden and makes loading deterministic.
- For a reviewer session, keep `FREE_RESEARCH_OPENAI_API_KEY` out of the environment as well (`env -u FREE_RESEARCH_OPENAI_API_KEY ...`) and use `review_prompt_v<version>.md`.

**Codex CLI** (researcher or reviewer)

```sh
cd <workspace> && env -u OPENAI_API_KEY CODEX_HOME="$HOME/.codex-research" \
  codex --no-daemon -m <model> -c model_reasoning_effort=xhigh \
    -s workspace-write -c sandbox_workspace_write.network_access=true -c 'web_search="live"' \
    --disable computer_use --disable browser_use --disable browser_use_external --disable in_app_browser \
    --disable memories --disable apps --disable plugins -a on-request "$(cat input_prompt_v<version>.md)"
```

- Log in once with `CODEX_HOME="$HOME/.codex-research" codex login`. `config.toml` there should contain only display settings and `[[skills.config]]` entries with `enabled = false` for every skill in `~/.agents/skills` (Codex reads that folder in addition to `CODEX_HOME`).
- `--no-daemon` matters: without it the session can attach to a background server started earlier, whose environment lacks the API key exported in the terminal.
- When Codex reaches its usage limit it may offer to switch to a cheaper model with that option preselected. Choose "Keep current model", then send the resume text.
- For a reviewer session, unset `FREE_RESEARCH_OPENAI_API_KEY` too and use `review_prompt_v<version>.md`.

## Setting up a new machine

1. Install Claude Code and/or Codex CLI, Python 3, Git and a TeX distribution if papers will be typeset later.
2. Create the research workspace as a new, empty directory. Do not copy earlier runs into it unless the series is meant to see them.
3. Create the isolated configuration directories and log in (above). Disable every skill under `~/.agents/skills` in the Codex research config. Check that no skills, MCP tools, `CLAUDE.md` or memory are visible, using a throwaway session with a small model in an empty folder.
4. Place the API key file outside the workspace (permissions 600).
5. Run `prepare_run.py` for the first run, then follow "One run, step by step".
