#!/usr/bin/env python3
"""評価の段階の5本（run-014〜018 の最終版）を、arXiv のプレプリントの体裁の PDF にする。

- 本文は各 run の git のタグ final の paper.md をそのまま使う（E1 の束 ../e1-eval/bundle/ と同じもの）。
  文言は変えない。変えるのは体裁だけ：題名を表題に、「## Abstract」を要旨の欄に、見出しを1段上げる。
  題名と要旨の間にあった注記の行は、表題の脚注に移す。HTML の注釈は出力されない。
- 著者は「Autonomous Research Agents」。表題の脚注に、出所（run、タグ、コミット）と変換したことを書く。
- 図は束の画像（SVG は PNG に変換済み）を使う。
- 確定した run のディレクトリには何も書かない。
使い方：python3 build_pdfs.py
"""
import json
import pathlib
import re
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
BUNDLE = HERE.parent / "e1-eval" / "bundle"
OUT = HERE / "out"
WORK = HERE / "work"
WS = pathlib.Path("/Users/fujimura/Research/ai-free-research-en")
FIG = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)(\))")
STUDY = "Letting AI Formulate the Research Question: Autonomous Research Agents (2026)"  # 本体の論文の題名（変わったら直す）

HEADER = r"""
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\textsc{A Preprint}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\usepackage{etoolbox}
\AtBeginEnvironment{longtable}{\footnotesize}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.1}
\usepackage{xurl}
\usepackage{newunicodechar}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{∈}{\ensuremath{\in}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{ᵀ}{\textsuperscript{T}}
\sloppy
"""


def final_date(run):
    """最終提出の日付（タグ final のコミットの日付、UTC）。"""
    return subprocess.run(["git", "-C", str(WS / f"run-{run}"), "log", "-1", "--date=format-local:%-d %B %Y",
                           "--format=%cd", "final"], capture_output=True, text=True, check=True,
                          env={"TZ": "UTC", "PATH": "/usr/bin:/bin:/opt/homebrew/bin"}).stdout.strip()


def split(md):
    lines = md.splitlines()
    assert lines[0].startswith("# "), "first line must be the title"
    title = lines[0][2:].strip()
    i_abs = next(i for i, l in enumerate(lines) if l.strip() == "## Abstract")
    note = "\n".join(l for l in lines[1:i_abs] if l.strip() and not l.strip().startswith("<!--")).strip()
    i_body = next(i for i in range(i_abs + 1, len(lines)) if lines[i].startswith("## "))
    abstract = "\n".join(lines[i_abs + 1:i_body]).strip()
    body = "\n".join(lines[i_body:]) + "\n"
    return title, note, abstract, body


def main():
    OUT.mkdir(exist_ok=True)
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    manifest = json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8"))
    built = []
    for m in manifest:
        run = m["run"]
        md = (BUNDLE / f"run-{run}" / "paper.md").read_text(encoding="utf-8")
        figmap = {f["ref"]: str(BUNDLE / f["file"]) for f in m["figures"]}
        md = FIG.sub(lambda x: x.group(1) + figmap.get(x.group(2), x.group(2)) + x.group(3), md)
        title, note, abstract, body = split(md)
        when = final_date(run)
        thanks = (f"Written autonomously by an AI research agent in run-{run} of the study \\emph{{{STUDY}}}; "
                  f"no human edited the text. This is the final version after one AI review "
                  f"(Git tag \\texttt{{final}}, commit \\texttt{{{m['commit'][:7]}}}), converted from Markdown to PDF "
                  f"without changes to the wording.")
        if note:
            thanks += " Note at the head of the manuscript: " + note
        meta = dict(title=title, author=[f"Autonomous Research Agents\\thanks{{{thanks}}}"], date=when,
                    abstract=abstract, documentclass="article", fontsize="10pt",
                    geometry="margin=1in", mainfont="STIX Two Text", mathfont="STIX Two Math",
                    colorlinks=True, linkcolor="blue", urlcolor="blue", **{"header-includes": HEADER})
        src = WORK / f"run-{run}.md"
        src.write_text("---\n" + json.dumps(meta, ensure_ascii=False) + "\n---\n\n" + body, encoding="utf-8")
        pdf = OUT / f"run-{run}.pdf"
        p = subprocess.run(["pandoc", str(src), "-f", "markdown-implicit_figures+tex_math_single_backslash", "--shift-heading-level-by=-1",
                            "--columns=60", "--pdf-engine=xelatex", "-o", str(pdf)],
                           capture_output=True, text=True)
        log = (p.stdout + p.stderr).strip()
        (WORK / f"run-{run}.log").write_text(log, encoding="utf-8")
        print(run, "ok" if p.returncode == 0 else f"FAILED {p.returncode}", when, title[:60])
        if p.returncode == 0:
            built.append(run)
    print("built:", built)


if __name__ == "__main__":
    main()
