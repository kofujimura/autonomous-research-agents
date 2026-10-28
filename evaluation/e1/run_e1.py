#!/usr/bin/env python3
"""E1（評価の段階）：束にした5本の論文を、AI 査読者に絶対評価させる（手順は README.md）。

- 査読者ごとに、1回目を5本すべて、次に2回目を同じ順で送る。1件ずつ順に送る。
- reviews/<査読者>/run-NNN.rK.json があるものは飛ばす。止まったら同じコマンドでもう一度起動すればよい。
- 費用の上限（査読者ごとに $10）を超えるおそれがあるときは送らずに止める。失敗した試みの費用も数える。
- 鍵の値は表示も記録もしない。
使い方：python3 run_e1.py gemini|gemini-pdf|muse [この起動で送る件数の上限]
"""
import base64
import datetime as dt
import json
import pathlib
import re
import ssl
import stat
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
BUNDLE = HERE / "bundle"
PDFS = HERE.parent / "papers-pdf" / "out"
RUNS = ["014", "015", "016", "017", "018"]
REPS = 2
CAP_USD = {"gemini-4-argon": 10.0, "muse-wonder-1.0": 20.0}  # Muse は 2026-10-28 に人間の判断で $20 に上げた
FIRST_ESTIMATE_USD = 1.5
KEYDIR = pathlib.Path.home() / ".config/ai-free-research"
REVIEWERS = {
    "gemini": dict(model="gemini-4-argon", keyfile="gemini.env", keyname="GEMINI_API_KEY", thinking="high",
                   price=dict(input=2.0, output=10.0, search=0.014), input="md"),
    # 2026-10-28 追加（人間の判断で5本を PDF で公開することにしたため）：同じ査読者に PDF を読ませる
    "gemini-pdf": dict(model="gemini-4-argon", keyfile="gemini.env", keyname="GEMINI_API_KEY", thinking="high",
                       price=dict(input=2.0, output=10.0, search=0.014), input="pdf"),
    # 2026-10-28 に Meta の公式の文書で確認：Responses API、reasoning.effort は minimal〜max、
    # web_search の道具、入力 $4・キャッシュ $0.20・出力 $20／100万トークン、検索 $2.50／1,000回
    "muse": dict(model="muse-wonder-1.0", keyfile="meta.env", keyname="META_MODEL_API_KEY", effort="max",
                 price=dict(input=4.0, cached_input=0.2, output=20.0, search=0.0025), input="pdf"),
}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def load_key(spec):
    f = KEYDIR / spec["keyfile"]
    if not f.exists():
        sys.exit(f"鍵のファイルがありません：{f}（人間が作成する）")
    if stat.S_IMODE(f.stat().st_mode) & 0o077:
        sys.exit(f"鍵のファイルの権限が広すぎます：{f}（600 にする）")
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip().removeprefix("export ")
        if line.startswith(spec["keyname"] + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit(f"{f} に {spec['keyname']} がありません")


def mask(s):
    s = re.sub(r"(key=)[^&\s\"']+", r"\1＊＊＊", s, flags=re.I)
    return re.sub(r"(AIza|sk-)[A-Za-z0-9_\-]+", r"\1＊＊＊", s)


def material(run, mode):
    """md：本文の Markdown と図の画像。pdf：PDF の1ファイル（図と表を含む）。"""
    if mode == "pdf":
        return (HERE / "prompt-pdf.md").read_text(encoding="utf-8"), [(PDFS / f"run-{run}.pdf", "paper.pdf")]
    d = BUNDLE / f"run-{run}"
    paper = (d / "paper.md").read_text(encoding="utf-8")
    man = next(m for m in json.loads((BUNDLE / "manifest.json").read_text(encoding="utf-8")) if m["run"] == run)
    figs = [(BUNDLE / f["file"], f["ref"]) for f in man["figures"]]
    listing = "\n".join(f"{i}. {ref}" for i, (_, ref) in enumerate(figs, 1)) or "(none)"
    text = ((HERE / "prompt.md").read_text(encoding="utf-8")
            + "\n\n# Attached figures (path in the paper, in attachment order)\n\n" + listing
            + "\n\n# Paper\n\n" + paper)
    return text, figs


def mime(p):
    return {".png": "image/png", ".pdf": "application/pdf"}.get(p.suffix, "image/jpeg")


def check(out, schema):
    """必須の項目と、点数・選択肢の値だけを確かめる。"""
    for k in schema["required"]:
        if k not in out:
            raise ValueError(f"missing {k}")
    for k, v in out["scores"].items():
        if not isinstance(v, int) or not 1 <= v <= 5:
            raise ValueError(f"bad score {k}")
    if out["verdict"] not in schema["properties"]["verdict"]["enum"]:
        raise ValueError("bad verdict")
    if not isinstance(out["overall_10"], int) or not 1 <= out["overall_10"] <= 10:
        raise ValueError("bad overall_10")


def first_json(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(re.search(r"\{.*\}", text, re.S).group(0))


# ---------- Gemini ----------
def gemini_post(spec, key, body):
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{spec['model']}:generateContent",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=1800, context=ssl_context()) as f:
        return json.loads(f.read().decode("utf-8"))


def call_gemini(spec, key, text, figs, schema):
    parts = [{"text": text}] + [{"inline_data": {"mime_type": mime(p), "data": base64.b64encode(p.read_bytes()).decode()}}
                                for p, _ in figs]
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseMimeType": "application/json", "responseJsonSchema": schema,
                                 "thinkingConfig": {"thinkingLevel": spec["thinking"]}},
            "tools": [{"google_search": {}}]}
    mode = "schema"
    try:
        d = gemini_post(spec, key, body)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:600]
        if e.code != 400:
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        # 検索の道具と出力の形の指定を同時に使えない場合は、形を本文で指示して読み取る
        body["generationConfig"].pop("responseJsonSchema")
        body["generationConfig"].pop("responseMimeType")
        parts[0]["text"] = text + "\n\nOutput only one JSON object that follows this JSON Schema:\n" + json.dumps(schema)
        mode = "schema-in-prompt"
        d = gemini_post(spec, key, body)
    c = d["candidates"][0]
    reply = "".join(p.get("text", "") for p in c["content"]["parts"] if not p.get("thought"))
    um = d.get("usageMetadata", {})
    gm = c.get("groundingMetadata", {})
    usage = dict(input_tokens=um.get("promptTokenCount", 0),
                 output_tokens=um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0),
                 thought_tokens=um.get("thoughtsTokenCount", 0),
                 search_queries=len(gm.get("webSearchQueries", [])))
    p = spec["price"]
    cost = (usage["input_tokens"] * p["input"] + usage["output_tokens"] * p["output"]) / 1e6 \
        + usage["search_queries"] * p["search"]
    trace = dict(mode=mode, model_version=d.get("modelVersion"), finish_reason=c.get("finishReason"),
                 web_search_queries=gm.get("webSearchQueries", []),
                 sources=[ch.get("web", {}).get("uri") for ch in gm.get("groundingChunks", [])])
    return reply, usage, cost, trace


# ---------- Muse Wonder ----------
def muse_request(key, method, path, body=None):
    req = urllib.request.Request(f"https://api.meta.ai/v1{path}", method=method,
                                 data=json.dumps(body).encode("utf-8") if body is not None else None,
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=600, context=ssl_context()) as f:
        return json.loads(f.read().decode("utf-8"))


def call_muse(spec, key, text, figs, schema):
    content = [{"type": "input_text", "text": text}] + [
        {"type": "input_file", "filename": name, "file_data": f"data:{mime(p)};base64," + base64.b64encode(p.read_bytes()).decode()}
        if p.suffix == ".pdf" else
        {"type": "input_image", "image_url": f"data:{mime(p)};base64," + base64.b64encode(p.read_bytes()).decode()}
        for p, name in figs]
    body = {"model": spec["model"], "input": [{"type": "message", "role": "user", "content": content}],
            "reasoning": {"effort": spec["effort"]}, "max_output_tokens": 128000,
            "tools": [{"type": "web_search"}], "include": ["web_search_call.results"],
            "text": {"format": {"type": "json_schema", "name": "review", "schema": schema, "strict": True}},
            "background": True}
    mode = "schema"
    try:
        d = muse_request(key, "POST", "/responses", body)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:600]
        if e.code != 400:
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        # 検索の道具と出力の形の指定を同時に使えない場合は、形を本文で指示して読み取る
        body.pop("text")
        content[0]["text"] = text + "\n\nOutput only one JSON object that follows this JSON Schema:\n" + json.dumps(schema)
        mode = "schema-in-prompt"
        d = muse_request(key, "POST", "/responses", body)
    while d.get("status") in ("queued", "in_progress"):
        time.sleep(15)
        d = muse_request(key, "GET", f"/responses/{d['id']}")
    if d.get("status") != "completed":
        raise RuntimeError(f"status {d.get('status')}: {json.dumps(d.get('error') or d.get('incomplete_details'))[:300]}")
    reply = "".join(c.get("text", "") for it in d.get("output", []) if it.get("type") == "message"
                    for c in it.get("content", []) if c.get("type") == "output_text")
    calls = [it for it in d.get("output", []) if it.get("type") == "web_search_call"]
    u = d.get("usage") or {}
    cached = (u.get("input_tokens_details") or {}).get("cached_tokens", 0)
    usage = dict(input_tokens=u.get("input_tokens", 0), cached_input_tokens=cached,
                 output_tokens=u.get("output_tokens", 0),
                 thought_tokens=(u.get("output_tokens_details") or {}).get("reasoning_tokens", 0),
                 search_queries=len(calls))
    p = spec["price"]
    cost = ((usage["input_tokens"] - cached) * p["input"] + cached * p["cached_input"]
            + usage["output_tokens"] * p["output"]) / 1e6 + usage["search_queries"] * p["search"]
    trace = dict(mode=mode, model_version=d.get("model"), finish_reason=d.get("status"),
                 web_search_queries=[(c.get("action") or {}).get("query") for c in calls],
                 sources=[r.get("url") for c in calls for r in (c.get("results") or [])])
    return reply, usage, cost, trace


CALL = {"gemini": call_gemini, "muse": call_muse}


def spent(reviewer):
    """上限は査読者のモデルごと（Markdown と PDF の査読を合わせる）。"""
    log = HERE / "runs.jsonl"
    if not log.exists():
        return 0.0, 0.0
    model = REVIEWERS[reviewer]["model"]
    costs = [r.get("cost_usd") or 0.0 for r in map(json.loads, log.read_text().splitlines())
             if r["model"] == model]
    return sum(costs), max(costs, default=0.0)


def main(reviewer, limit=None):
    spec = REVIEWERS[reviewer]
    if spec["price"] is None:
        sys.exit("単価がまだ入っていません（README.md）")
    key = load_key(spec)
    schema = json.loads((HERE / "schema.json").read_text(encoding="utf-8"))
    outdir = HERE / "reviews" / reviewer
    outdir.mkdir(parents=True, exist_ok=True)
    (HERE / "logs").mkdir(exist_ok=True)
    sent = 0
    for rep in range(1, REPS + 1):
        for run in RUNS:
            dest = outdir / f"run-{run}.r{rep}.json"
            if dest.exists():
                continue
            total, biggest = spent(reviewer)
            if total + (biggest or FIRST_ESTIMATE_USD) > CAP_USD[spec["model"]]:
                print(f"{now()} stop: budget (spent ${total:.2f}, next estimate ${biggest or FIRST_ESTIMATE_USD:.2f})")
                return
            if limit is not None and sent >= limit:
                print(f"{now()} stop: limit of {limit} review(s) for this start")
                return
            sent += 1
            text, figs = material(run, spec["input"])
            rec = dict(reviewer=reviewer, model=spec["model"], run=run, rep=rep, started_utc=now(), figures=len(figs))
            t0 = time.time()
            try:
                reply, usage, cost, trace = CALL["muse" if spec["model"].startswith("muse") else "gemini"](spec, key, text, figs, schema)
                rec.update(usage=usage, cost_usd=round(cost, 6), **{k: trace[k] for k in ("mode", "model_version", "finish_reason")})
                (HERE / "logs" / f"{reviewer}-run-{run}.r{rep}.{int(t0)}.json").write_text(
                    json.dumps(dict(trace=trace, reply=reply), ensure_ascii=False, indent=1), encoding="utf-8")
                out = first_json(reply)
                check(out, schema)
                dest.write_text(json.dumps(dict(meta=rec, review=out, trace=trace), ensure_ascii=False, indent=1),
                                encoding="utf-8")
                rec["status"] = "ok"
            except Exception as e:  # 鍵を含みうる情報は書かない
                rec["status"] = mask(f"failed: {type(e).__name__}: {str(e)[:300]}")
            rec.update(ended_utc=now(), seconds=round(time.time() - t0, 1))
            with open(HERE / "runs.jsonl", "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(rec["ended_utc"], reviewer, run, f"r{rep}", rec["status"], f"${rec.get('cost_usd', 0):.3f}",
                  f"{rec['seconds']}s", flush=True)
    print(f"{now()} done: spent ${spent(reviewer)[0]:.2f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
