#!/usr/bin/env python3
"""E1（評価の段階）の集計。reviews/ の JSON から results.md と results.json を作る。

- 主の結果は PDF の査読（gemini-pdf、muse）。Markdown の査読（gemini）も並べる（README.md と e1-procedure.md）。
- 研究の中の査読（Opus 5.5、記録から再計算。初稿を読んだもの）の点数と判定を参考に並べる。条件が違うので差は比べない。
使い方：python3 analyze.py
"""
import collections
import glob
import json
import pathlib
import statistics as st

HERE = pathlib.Path(__file__).resolve().parent
RUNS = ["014", "015", "016", "017", "018"]
AXES = ["correctness", "verifiability", "novelty", "generality", "usefulness", "clarity"]
REVIEWERS = [("gemini-pdf", "Gemini 4 Argon (PDF)"), ("muse", "Muse Wonder (PDF)"), ("gemini", "Gemini 4 Argon (Markdown)")]
# 研究の中の査読（review-0NN/review-1.md の §2〜3。管理側の runs.md と dashboard/build.py の REVIEWS と同じ値）
IN_LOOP = {
    "014": ("major revision", [4, 5, 3, 2, 3, 2]),
    "015": ("minor revision", [4, 5, 2, 2, 3, 2]),
    "016": ("major revision", [4, 5, 2, 2, 3, 2]),
    "017": ("major revision", [3, 5, 3, 2, 3, 2]),
    "018": ("major revision", [3, 5, 3, 2, 3, 2]),
}


def load(reviewer):
    out = collections.defaultdict(list)
    for f in sorted(glob.glob(str(HERE / "reviews" / reviewer / "run-*.json"))):
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        out[d["meta"]["run"]].append(d)
    return out


def mean(xs):
    return round(st.mean(xs), 2) if xs else None


def summarize(reviews):
    rv = [d["review"] for d in reviews]
    return dict(
        n=len(rv),
        axes={a: mean([r["scores"][a] for r in rv]) for a in AXES},
        overall_10=mean([r["overall_10"] for r in rv]),
        overall_each=[r["overall_10"] for r in rv],
        verdicts=[r["verdict"] for r in rv],
        workshop=[r["workshop_level"] for r in rv],
        main_track=[r["main_track_level"] for r in rv],
        question_quality=mean([r["research_question"]["question_quality"] for r in rv]),
        predictable=[r["research_question"]["predictable"] for r in rv],
        critical=[sum(i["severity"] == "critical" for i in r["main_issues"]) for r in rv],
        searches=[d["meta"]["usage"]["search_queries"] for d in reviews],
        cost_usd=round(sum(d["meta"]["cost_usd"] for d in reviews), 3),
        familiar=[r["familiarity"] for r in rv if not r["familiarity"].strip().lower().startswith("no")],
    )


def main():
    res = {}
    for key, label in REVIEWERS:
        data = load(key)
        res[key] = dict(label=label, runs={run: summarize(data.get(run, [])) for run in RUNS})
        allrev = [d for run in RUNS for d in data.get(run, [])]
        res[key]["all"] = summarize(allrev)
        # 同じ論文の2回の総合点の差
        pairs = [res[key]["runs"][run]["overall_each"] for run in RUNS]
        res[key]["rep_overall_absdiff"] = mean([abs(p[0] - p[1]) for p in pairs if len(p) >= 2])
    (HERE / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    L = ["# E1（評価の段階）の結果（自動生成：analyze.py）", ""]
    L += ["## 査読者ごとの平均（全論文）", "",
          "| 査読者 | 件数 | " + " | ".join(AXES) + " | overall_10 | 2回の総合点の差（平均） | question_quality | 重大の指摘（件／査読） | 費用 USD |",
          "|---|---|" + "---|" * len(AXES) + "---|---|---|---|---|"]
    for key, label in REVIEWERS:
        a = res[key]["all"]
        L.append(f"| {label} | {a['n']} | " + " | ".join(str(a["axes"][x]) for x in AXES)
                 + f" | {a['overall_10']} | {res[key]['rep_overall_absdiff']} | {a['question_quality']} | {mean(a['critical'])} | {a['cost_usd']} |")
    L += ["", "## 論文ごと", ""]
    for run in RUNS:
        dec, sc = IN_LOOP[run]
        L += [f"### run-{run}", "",
              "| 査読者 | n | " + " | ".join(AXES) + " | overall_10 | 判定 | ワークショップ | 主会議 | 問いの質 | 予想できたか | 重大 | 検索 |",
              "|---|---|" + "---|" * len(AXES) + "---|---|---|---|---|---|---|---|"]
        for key, label in REVIEWERS:
            s = res[key]["runs"][run]
            if not s["n"]:
                L.append(f"| {label} | 0 |" + " |" * (len(AXES) + 8))
                continue
            L.append(f"| {label} | {s['n']} | " + " | ".join(str(s["axes"][x]) for x in AXES)
                     + f" | {'/'.join(map(str, s['overall_each']))} | {'/'.join(s['verdicts'])} | {'/'.join(s['workshop'])}"
                     + f" | {'/'.join(s['main_track'])} | {s['question_quality']} | {'/'.join(s['predictable'])}"
                     + f" | {'/'.join(map(str, s['critical']))} | {'/'.join(map(str, s['searches']))} |")
        L.append(f"| 研究の中の査読（Opus 5.5、記録あり、初稿） | 1 | " + " | ".join(map(str, sc)) + f" | — | {dec} | — | — | — | — | — | — |")
        L.append("")
    fam = {k: res[k]["all"]["familiar"] for k, _ in REVIEWERS if res[k]["all"]["familiar"]}
    L += ["## この論文を知っていると答えた査読", "", json.dumps(fam, ensure_ascii=False) if fam else "なし", ""]
    (HERE / "results.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
