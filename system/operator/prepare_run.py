#!/usr/bin/env python3
"""Fill the instruction templates for one run and deploy them, with the skills, into the research workspace.

The filled files differ from the templates only in the placeholders below, so every run of a version
uses the same text. The script refuses to overwrite anything that differs from what it would write.

  {{VERSION}}         label of the filled instructions, e.g. 1.10 (later runs of the same text: 1.10.1, 1.10.2, ...)
  {{RUN_NO}}          three-digit run number, e.g. 014
  {{WORKSPACE}}       absolute path of the research workspace
  {{REVIEWER_MODEL}}  reviewer model as told to the review session, e.g. "gpt-6.1-sol, reasoning effort xhigh"

Usage:
  python3 prepare_run.py --version 1.10 --run 014 --workspace /abs/path --reviewer-model "..."          # write
  python3 prepare_run.py --version 1.10 --run 014 --workspace /abs/path --reviewer-model "..." --check  # compare only

Writes (in the workspace): input_prompt_v<version>.md, review_prompt_v<version>.md, skills/<name>/...
Prints the SHA-256 of every template, skill file and filled file.
"""
import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = {"input_prompt": ROOT / "instructions" / "input_prompt.md",
             "review_prompt": ROOT / "instructions" / "review_prompt.md"}
SKILLS = ROOT / "skills"
# Files that must never be in the research workspace (management knowledge, project rules, agent memory).
FORBIDDEN = ["CLAUDE.md", "AGENTS.md", ".claude", ".codex", ".agents"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fill(text: str, values: dict) -> str:
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))
    if left:
        sys.exit(f"unfilled placeholders: {left}")
    return text


def plan(args) -> list:
    """(destination, bytes) for every file to deploy."""
    values = {"VERSION": args.version, "RUN_NO": args.run, "WORKSPACE": str(args.workspace),
              "REVIEWER_MODEL": args.reviewer_model}
    out = []
    for name, tpl in TEMPLATES.items():
        out.append((args.workspace / f"{name}_v{args.version}.md",
                    fill(tpl.read_text(encoding="utf-8"), values).encode("utf-8")))
    for f in sorted(p for p in SKILLS.rglob("*") if p.is_file() and p.name != ".DS_Store"):
        out.append((args.workspace / "skills" / f.relative_to(SKILLS), f.read_bytes()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--workspace", required=True, type=pathlib.Path)
    ap.add_argument("--reviewer-model", required=True)
    ap.add_argument("--check", action="store_true", help="compare the workspace with a fresh fill; write nothing")
    args = ap.parse_args()

    if not re.fullmatch(r"\d+(\.\d+)+", args.version):
        sys.exit("--version must look like 1.10 or 1.10.1")
    if not re.fullmatch(r"\d{3}", args.run):
        sys.exit("--run must be three digits, e.g. 014")
    if not args.workspace.is_absolute():
        sys.exit("--workspace must be an absolute path")
    if re.search(r"[{}\n]", args.reviewer_model):
        sys.exit("--reviewer-model must be one line without braces")
    args.workspace = args.workspace.resolve()

    found = [n for n in FORBIDDEN if (args.workspace / n).exists()]
    if found:
        sys.exit(f"the research workspace must not contain {found}")
    for d in (f"run-{args.run}", f"review-{args.run}"):
        if (args.workspace / d).exists() and not args.check:
            sys.exit(f"{args.workspace / d} already exists")

    files = plan(args)
    problems = []
    for dest, data in files:
        if dest.exists() and dest.read_bytes() != data:
            problems.append(f"differs: {dest}")
        elif not dest.exists() and args.check:
            problems.append(f"missing: {dest}")
    deployed_skills = args.workspace / "skills"
    if deployed_skills.exists():
        expected = {d for d, _ in files}
        for p in deployed_skills.rglob("*"):
            if p.is_file() and p.name != ".DS_Store" and p not in expected:
                problems.append(f"extra file in the workspace skills: {p}")
    if problems:
        print("\n".join(problems))
        sys.exit("nothing written" if not args.check else "check failed")

    if not args.check:
        args.workspace.mkdir(parents=True, exist_ok=True)
        for dest, data in files:
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)

    print("templates:")
    for tpl in TEMPLATES.values():
        print(f"  {sha(tpl.read_bytes())}  {tpl.relative_to(ROOT)}")
    print("deployed:" if not args.check else "checked (all match):")
    for dest, data in files:
        print(f"  {sha(data)}  {dest}")


if __name__ == "__main__":
    main()
