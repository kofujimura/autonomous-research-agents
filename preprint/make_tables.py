#!/usr/bin/env python3
"""Tables for the preprint, generated from the run records and the management ledger.

Values read from the run records (research workspace, read only):
  start time (manifest.json), topic selection (events.jsonl), draft and final tags (git),
  review start and end (review-NNN/manifest.json), claims at the final tag (claims.jsonl),
  intervention types (interventions.jsonl).
Values from the management records (facts below; source: runs.md, evaluations/run-NNN.md,
candidates.md, ~/.codex-research/history.jsonl): usage-limit stops, messages sent, critique and
review tallies. E1 values are read from ../e1-eval/results.json.
Development runs 001-013 (Japanese instructions): model, version and candidates by object class are read from
../recount/out/runs.csv (recount of the run records; classes from the management file candidates.md). The area
setting of each version is summarised from the management file changelog.md, the chosen study from the paper titles.
Usage: python3 make_tables.py   (writes tables/*.tex and facts.json)
"""
import csv
import datetime as dt
import json
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
WS = pathlib.Path("/Users/fujimura/Research/ai-free-research-en")
E1 = HERE.parent / "e1-eval" / "results.json"
RUNS = ["014", "015", "016", "017", "018"]
HISTORY = pathlib.Path.home() / ".codex-research" / "history.jsonl"  # inputs sent to the research sessions (time and text)

# Management-side facts (see the docstring for sources).
FACTS = {
    "014": dict(version="1.10", stops_s=6763, resumes_limit=2, resumes_other=1, topic_min=64, candidates=15, techs=6,
                critic_points=26, critic_adopted=22, critic_on_selected=9, findings=(0, 6, 2), responded=(5, 3),
                verdict="major", scores=[4, 5, 3, 2, 3, 2], cost="2.02",
                topic="Screening one-year tree-cover change in the contiguous US with annual satellite embeddings",
                data="LCMAP, NLCD; AlphaEarth, TESSERA embeddings"),
    "015": dict(version="1.10.1", stops_s=10052, resumes_limit=3, resumes_other=1, topic_min=54, candidates=15, techs=6,
                critic_points=26, critic_adopted=21, critic_on_selected=7, findings=(0, 4, 3), responded=(5, 2),
                verdict="minor", scores=[4, 5, 2, 2, 3, 2], cost="2.02",
                topic="Bounds on joint temperature-exceedance probabilities from published ensemble summaries",
                data="ECMWF ensemble forecasts"),
    "016": dict(version="1.10.2", stops_s=6772, resumes_limit=2, resumes_other=0, topic_min=72, candidates=15, techs=6,
                critic_points=23, critic_adopted=13, critic_on_selected=7, findings=(0, 6, 3), responded=(5, 4),
                verdict="major", scores=[4, 5, 2, 2, 3, 2], cost="1.94",
                topic="Re-sampling reference locations to estimate change in Swiss crop-group diversity",
                data="Swiss crop declarations; annual embeddings"),
    "017": dict(version="1.10.3", stops_s=3533, resumes_limit=1, resumes_other=0, topic_min=33, candidates=15, techs=6,
                critic_points=23, critic_adopted=19, critic_on_selected=6, findings=(0, 4, 2), responded=(6, 0),
                verdict="major", scores=[3, 5, 3, 2, 3, 2], cost="1.95--2.02",
                topic="Training-point allocation and recovery of small wetland patches",
                data="US National Wetlands Inventory; AlphaEarth, Sentinel-2"),
    "018": dict(version="1.10.4", stops_s=22672, resumes_limit=4, resumes_other=0, topic_min=60, candidates=17, techs=7,
                critic_points=21, critic_adopted=14, critic_on_selected=6, findings=(1, 5, 4), responded=(8, 2),
                verdict="major", scores=[3, 5, 3, 2, 3, 2], cost="1.99",
                topic="Do satellite embedding distances improve matching of wetland water regimes?",
                data="US National Wetlands Inventory; AlphaEarth, TESSERA; terrain and surface water"),
}
# Candidate fields over runs 014-018 (management classification, candidates.md; 77 candidates).
FIELDS = [("Environment", 17), ("Disaster and water", 14), ("Food and agriculture", 12), ("Health", 7),
          ("Transport and welfare", 7), ("Resources and materials", 7), ("Public administration", 6),
          ("Energy", 4), ("Cultural heritage", 3)]

DEV = HERE.parent / "recount" / "out" / "runs.csv"
# How each version set the research area (changelog.md); "unchanged" refers to the area setting only.
DEV_AREA = {
    "001": "None: no field, no selection procedure",
    "002": "Field: computer science (CS)",
    "003": "CS; at least 8 candidates; aim at questions that change someone's judgment",
    "004": "CS; ``AI-era problems'' welcomed and scored",
    "005": "unchanged (research model changed)",
    "006": "CS; readers are future autonomous research agents; AI-era axis removed",
    "007": "unchanged",
    "008": "unchanged",
    "009": "CS; readers are researchers and practitioners of the field",
    "010": "unchanged",
    "011": "No field; hint: discover, or help solve, societal problems using open data",
    "012": "As 011; diverge from technologies practical since 2024 into fields outside CS",
    "013": "unchanged (research model changed)",
}
DEV_TOPIC = {
    "001": "Non-uniform birthday problem (exact computation)",
    "002": "Admission control for LRU caches",
    "003": "Third-party tracking on Japanese local-government websites",
    "004": "Silent mis-application in coding-agent edit tools",
    "005": "Cost of structured-generation engines under JSON-Schema rewrites",
    "006": "Do hypothesis-supporting results make LLM agents check less?",
    "007": "Granularity checks of benchmark values reported in LLM papers",
    "008": "Reuse conditions for learning-curve archives",
    "009": "Re-ranking to parent documents in retrieval",
    "010": "Workflow-cache savings and postdominator bounds",
    "011": "Simulated re-measurement of PFAS non-detects in water monitoring",
    "012": "Forecasters and data recency in wastewater surveillance",
    "013": "Machine translation of Japan's new weather-warning names",
}
DEV_CLASSES = ["AI", "AI道具", "研究慣行", "システム", "数理", "社会"]  # AI, tools, practice, systems, math, societal
DEV_MODEL = {"Opus 5.5": "Opus 5.5"}


def dev_runs():
    rows = []
    for r in csv.DictReader(open(DEV, encoding="utf-8")):
        counts = {c: int(r[f"cand_{c}"]) for c in DEV_CLASSES}
        assert sum(counts.values()) == int(r["candidates"]), r["run"]
        rows.append(dict(run=r["run"], version=r["version"].split("（")[0], model=DEV_MODEL.get(r["model"], r["model"]),
                         counts=counts, chosen=r["chosen_category"]))
    return rows


def t(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def git_time(run, tag):
    return t(subprocess.run(["git", "-C", str(WS / f"run-{run}"), "log", "-1", "--format=%cI", tag],
                            capture_output=True, text=True, check=True).stdout.strip())


def jl(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def hm(seconds):
    m = round(seconds / 60)
    return f"{m // 60}:{m % 60:02d}"


def collect():
    out = {}
    for run in RUNS:
        d = WS / f"run-{run}"
        f = dict(FACTS[run])
        start = t(json.loads((d / "manifest.json").read_text())["start_time_utc"])
        topic = next(t(e["observed_at_utc"]) for e in jl(d / "events.jsonl") if e.get("type") == "topic_selected")
        sub1, final = git_time(run, "submission-1"), git_time(run, "final")
        rm = json.loads((WS / f"review-{run}" / "manifest.json").read_text())
        rs = t(rm.get("start_time_utc") or rm.get("start_at_utc"))
        re_ = t(rm.get("end_time_utc") or rm.get("end_at_utc"))
        claims = [json.loads(l) for l in subprocess.run(["git", "-C", str(d), "show", "final:claims.jsonl"],
                                                        capture_output=True, text=True, check=True).stdout.splitlines() if l.strip()]
        types = [i.get("type") for i in jl(d / "interventions.jsonl")]
        deadline = start + dt.timedelta(hours=12, seconds=f["stops_s"])
        received = min(dt.datetime.fromtimestamp(h["ts"], dt.timezone.utc) for h in jl(HISTORY)
                       if h.get("text", "").startswith("REVIEW-1") and h["ts"] >= re_.timestamp())
        f.update(start=start.isoformat(), topic_selected=topic.isoformat(), draft=sub1.isoformat(), final=final.isoformat(),
                 draft_wall_s=(sub1 - start).total_seconds(), draft_active_s=(sub1 - start).total_seconds() - f["stops_s"],
                 margin_s=(deadline - sub1).total_seconds(), review_min=round((re_ - rs).total_seconds() / 60),
                 response_min=round((final - received).total_seconds() / 60), review_received=received.isoformat(),
                 claims=len(claims), claims_exploratory=sum(c.get("exploratory") is True for c in claims),
                 permission_requests=sum(1 for x in types if x and "permission" in x),
                 research_advice=sum(1 for x in types if x and "scientific" in x))
        out[run] = f
    return out


def write(name, rows):
    (HERE / "tables").mkdir(exist_ok=True)
    (HERE / "tables" / f"{name}.tex").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main():
    F = collect()
    D = dev_runs()
    (HERE / "facts.json").write_text(json.dumps(dict(F, development=D), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write("dev", [f"{d['run']} & {d['version']} & {d['model']} & {DEV_AREA[d['run']]} & "
                  + " & ".join(f"\\textbf{{{d['counts'][c]}}}" if c == d["chosen"] else str(d["counts"][c]) for c in DEV_CLASSES)
                  + f" & {DEV_TOPIC[d['run']]} \\\\" for d in D])
    write("runs", [f"{r} & v{F[r]['version']} & {F[r]['topic']} & {F[r]['data']} \\\\" for r in RUNS])
    write("ops", [f"{r} & {F[r]['topic_min']} & {hm(F[r]['draft_wall_s'])} & {hm(F[r]['stops_s'])} & {hm(F[r]['draft_active_s'])}"
                  f" & {hm(F[r]['margin_s'])} & {F[r]['resumes_limit']} + {F[r]['resumes_other']} & {F[r]['permission_requests']}"
                  f" & {F[r]['research_advice']} & {F[r]['review_min']} & {F[r]['response_min']} & {F[r]['cost']} \\\\" for r in RUNS])
    write("selection", [f"{r} & {F[r]['candidates']} & {F[r]['techs']} & {F[r]['critic_points']} & {F[r]['critic_adopted']}"
                        f" & {F[r]['critic_on_selected']} \\\\" for r in RUNS])
    sev = lambda r: F[r]["findings"]
    write("review", [f"{r} & {F[r]['verdict']} & " + " & ".join(map(str, F[r]["scores"]))
                     + f" & {sev(r)[0]} & {sev(r)[1]} & {sev(r)[2]} & {F[r]['responded'][0]} + {F[r]['responded'][1]}"
                     f" & {F[r]['claims']} ({F[r]['claims_exploratory']}) \\\\" for r in RUNS])
    write("fields", [", ".join(f"{n.lower()} ({k})" for n, k in FIELDS[:-1]) + f" and {FIELDS[-1][0].lower()} ({FIELDS[-1][1]})%"])
    e1 = json.loads(E1.read_text(encoding="utf-8"))
    rows = []
    for key, label in [("gemini-pdf", "Gemini 4 Argon"), ("muse", "Muse Wonder")]:
        for r in RUNS:
            s = e1[key]["runs"][r]
            ws = "/".join(x[0].upper() for x in s["workshop"])
            mt = "/".join(x[0].upper() for x in s["main_track"])
            vd = "/".join({"accept": "A", "minor revision": "m", "major revision": "M", "reject": "R"}[v] for v in s["verdicts"])
            rows.append(f"{label if r == '014' else ''} & {r} & " + " & ".join(f"{s['axes'][a]:.1f}" for a in
                        ["correctness", "verifiability", "novelty", "generality", "usefulness", "clarity"])
                        + f" & {'/'.join(map(str, s['overall_each']))} & {vd} & {ws} & {mt} \\\\")
        a = e1[key]["all"]
        rows.append(f"& \\emph{{mean}} & " + " & ".join(f"{a['axes'][x]:.1f}" for x in
                    ["correctness", "verifiability", "novelty", "generality", "usefulness", "clarity"])
                    + f" & {a['overall_10']:.1f} & & & \\\\" + ("\\midrule" if key == "gemini-pdf" else ""))
    write("e1", rows)
    tot = dict(stops=sum(F[r]["stops_s"] for r in RUNS), resumes=sum(F[r]["resumes_limit"] + F[r]["resumes_other"] for r in RUNS),
               candidates=sum(F[r]["candidates"] for r in RUNS), findings=sum(sum(F[r]["findings"]) for r in RUNS))
    print(json.dumps(tot))


if __name__ == "__main__":
    main()
