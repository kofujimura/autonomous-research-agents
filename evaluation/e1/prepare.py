#!/usr/bin/env python3
"""E1（評価の段階）：run-014〜018 の最終版の論文と図を、査読に渡す束にする。

- 各 run の git のタグ final から `git show` で読むだけで、run のディレクトリには何も書かない。
- 本文は変えない。本文が参照する図を取り出し、SVG は qlmanage で PNG に変換する。
- 元のファイルと渡すファイルの SHA-256 を bundle/manifest.json に記録する。
使い方：python3 prepare.py
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
WS = pathlib.Path("/Users/fujimura/Research/ai-free-research-en")
RUNS = ["014", "015", "016", "017", "018"]
OUT = HERE / "bundle"
FIG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def show(run, path):
    return subprocess.run(["git", "-C", str(WS / f"run-{run}"), "show", f"final:{path}"],
                          capture_output=True, check=True).stdout


def svg_to_png(data, dest):
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "figure.svg"
        src.write_bytes(data)
        subprocess.run(["qlmanage", "-t", "-s", "2000", "-o", td, str(src)],
                       capture_output=True, check=True)
        shutil.copyfile(pathlib.Path(td) / "figure.svg.png", dest)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    manifest = []
    for run in RUNS:
        commit = subprocess.run(["git", "-C", str(WS / f"run-{run}"), "rev-parse", "final^{commit}"],
                                capture_output=True, text=True, check=True).stdout.strip()
        paper = show(run, "paper.md")
        d = OUT / f"run-{run}"
        (d / "figs").mkdir(parents=True)
        (d / "paper.md").write_bytes(paper)
        figs = []
        for i, ref in enumerate(dict.fromkeys(FIG.findall(paper.decode("utf-8"))), 1):
            data = show(run, ref)
            suffix = pathlib.Path(ref).suffix.lower()
            dest = d / "figs" / f"fig{i:02d}{'.png' if suffix == '.svg' else suffix}"
            if suffix == ".svg":
                svg_to_png(data, dest)
            else:
                dest.write_bytes(data)
            figs.append(dict(ref=ref, source_sha256=sha(data), file=str(dest.relative_to(OUT)),
                             file_sha256=sha(dest.read_bytes()), converted=suffix == ".svg"))
        manifest.append(dict(run=run, tag="final", commit=commit, paper_sha256=sha(paper),
                             words=len(paper.decode("utf-8").split()), figures=figs))
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
    for m in manifest:
        print(m["run"], m["commit"][:7], m["words"], "words", len(m["figures"]), "figures")


if __name__ == "__main__":
    main()
