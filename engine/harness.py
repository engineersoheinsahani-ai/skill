#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.py — the REAL multi-model executor (v4-pro), tuned for SMALL local models.

Law 9 (execution honesty): every finding written by this harness is stamped
`"indep": "harness"` with `"executor": "<model>@<stamp>#<i>"`. Without an API key
the harness REFUSES to run — it never fakes independence.

Optimized for qwen3.5:4b-class local models (4 GB VRAM, CPU/GPU hybrid):
  * compact laws digest (~700 chars) + ONE few-shot JSONL example
  * anchors capped (--max-anchors, default 20) and trimmed to 120 chars
  * generation capped (--max-tokens, default 1200) => short dense findings
  * low temperature profile 0.2..0.5 (small models degrade above ~0.7)
  * /no_think soft-switch for qwen3-family (--think off, default)
  * robust JSONL extraction: code fences, trailing commas, concatenated objects
  * one parse-retry with a stricter reminder (--retries, default 1)

The API key NEVER lives in the workspace: it is read from the owner's
environment (ARENA_API_KEY). No key -> only --dry-run / brief assembly works.

Usage:
  python3 engine/harness.py brief --gid G6 --work work [--attach FILE]
  python3 engine/harness.py run   --gid G6 --work work --n 6 [--dry-run]
  python3 engine/harness.py ingest --gid G6 --file answer.txt --indep human
Environment:
  ARENA_API_BASE (default http://localhost:11434/v1 — Ollama)
  ARENA_API_KEY  (any non-empty string for Ollama, e.g. "ollama")
  ARENA_MODEL    (default qwen3.5:4b)  /  ARENA_MODEL_<GID> per-group override
"""
import argparse, datetime, json, os, re, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

LAWS_DIGEST = """LAWS (non-negotiable): (1) DUAL GROUNDING — every finding needs an exact quote
from the ANCHORS below with its [L:...] id, plus an exact manuscript quote (ms_quote)
when mapping a claim. No anchor -> finding is quarantined. (2) DECISION VALUE —
verdict + <=3 concrete actions, no paraphrase. (3) NO FABRICATION — never invent
numbers; write [number needed]. (4) CLAIM SIZE — no claim bigger than its evidence.
(5) OUTPUT — JSONL only: one JSON object per line, max 5 findings, each <=120 words,
no prose before/after. Example line:
{"claim_id":"G6-01","gid":"G6","verdict":"supported","lit_quote":"...exact anchor text...","lit_quote_id":"L:e4-012","lit_tier":"body","severity":"major","action":"...","ms_quote":"...exact manuscript text..."}"""

EXAMPLE_FIELDS = ("claim_id", "gid", "verdict", "lit_quote", "lit_quote_id",
                  "lit_tier", "severity", "action", "ms_quote")


def load_duty(gid, playbook="groups/16-group-playbooks.md"):
    p = os.path.join(ROOT, playbook)
    txt = open(p, encoding="utf-8").read()
    m = re.search(rf"^## {re.escape(gid)}[ ·]+(.+?)(?=^## |\Z)", txt, re.S | re.M)
    if not m:
        raise SystemExit(f"duty card for {gid} not found in {playbook}")
    return f"## {gid} · {m.group(1).strip()}"


def load_anchors(gids, work, limit=20, maxlen=120):
    """gids: list of ledger gids to pool (G->E mapping lives in campaign.py)."""
    p = os.path.join(work, "ledger.jsonl")
    out = []
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("gid") not in gids:
                continue
            for q in (r.get("quote_bank") or []):
                if len(q.get("quote", "")) >= 15 and q.get("locator"):
                    w = "1.0" if r.get("tier") == "body" else "0.5"
                    out.append(f"[L:{r['source_id']} {q['locator']}] (w={w}) "
                               + q["quote"][:maxlen])
            if len(out) >= limit:
                break
    return "\n".join(out[:limit]) or "(no ledger anchors — rulebook-only group)"


def assemble(gid, work, playbook="groups/16-group-playbooks.md", attach=None,
             max_anchors=20, anchor_gids=None, extra_sections=""):
    txt = (LAWS_DIGEST + "\n\n=== YOUR DUTY (one duty only) ===\n"
           + load_duty(gid, playbook)
           + "\n\n=== ANCHORS (the ONLY pool for lit_quote/lit_quote_id) ===\n"
           + load_anchors(anchor_gids or [gid], work, max_anchors)
           + (("\n\n=== MANUSCRIPT EXCERPT (your duty only) ===\n" + extra_sections)
              if extra_sections else "")
           + f"\n\n=== OUTPUT ===\nJSONL only (max 5). Every line: gid=\"{gid}\".")
    if attach:
        src = open(attach, encoding="utf-8", errors="replace").read()
        cap = 60_000                      # small-model budget
        note = f" [TRUNCATED to {cap} chars]" if len(src) > cap else ""
        txt += (f"\n\n=== ATTACHED READ-ONLY SOURCE ({os.path.basename(attach)}{note}) ===\n"
                + src[:cap])
    return txt


def call_api(prompt, model, temperature, max_tokens=1200, timeout=900, think_off=True):
    base = os.environ.get("ARENA_API_BASE", "http://localhost:11434/v1").rstrip("/")
    key = os.environ.get("ARENA_API_KEY")
    if not key:
        raise SystemExit("ARENA_API_KEY not set — refusing to fake independence. "
                         "Use --dry-run, or set the key in YOUR environment.")
    if think_off and not prompt.endswith("/no_think"):
        prompt = prompt + "\n/no_think"
    body = json.dumps({"model": model, "temperature": temperature,
                       "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(base + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {key}"})
    r = json.load(urllib.request.urlopen(req, timeout=timeout))
    return r["choices"][0]["message"]["content"]


def extract_jsonl(text):
    """Robust for small models: strips code fences, tolerates trailing commas and
    objects concatenated on one line (brace-depth scan)."""
    text = re.sub(r"```(?:json|jsonl)?", " ", text)
    rows = []
    for line in text.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{") and line.endswith("}"):
            try:
                rows.append(json.loads(line))
                continue
            except json.JSONDecodeError:
                pass
    if rows:
        return rows
    depth, start = 0, None                      # brace-depth fallback
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                frag = text[start:i + 1]
                frag = re.sub(r",\s*([}\]])", r"\1", frag)   # trailing commas
                try:
                    rows.append(json.loads(frag))
                except json.JSONDecodeError:
                    pass
                start = None
    return rows


def utc_stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S")


def append_findings(fp, rows, gid, executor, indep="harness", extra=None):
    with open(fp, "a", encoding="utf-8") as f:
        for r in rows:
            r["gid"] = r.get("gid") or gid
            r["executor"] = executor
            r["indep"] = indep
            if extra:
                r.update(extra)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def cmd_ingest(a):
    text = open(a.file, encoding="utf-8", errors="replace").read()
    rows = extract_jsonl(text)
    if not rows:
        print("no JSONL objects found in", a.file)
        return 1
    fp = os.path.join(a.work, "findings.jsonl")
    append_findings(fp, rows, a.gid, a.label or f"chat-paste@{utc_stamp()}", a.indep)
    print(f"ingested {len(rows)} findings ({a.gid}, indep={a.indep}) -> {fp}")
    print("next (local, no key): run.py check / matrix / council on", fp)
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["brief", "run", "ingest"])
    ap.add_argument("--gid", default=None)
    ap.add_argument("--work", default="work")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--attach", default=None)
    ap.add_argument("--max-anchors", type=int, default=20)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--think", default="off", choices=["off", "on"])
    ap.add_argument("--retries", type=int, default=1)
    ap.add_argument("--playbook", default="groups/16-group-playbooks.md")
    ap.add_argument("--file", default=None)
    ap.add_argument("--indep", default="human", choices=["human", "harness"])
    ap.add_argument("--label", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "ingest":
        if not (a.file and a.gid):
            raise SystemExit("ingest: --file and --gid required")
        return cmd_ingest(a)
    if not a.gid:
        raise SystemExit(f"{a.cmd}: --gid required")
    prompt = assemble(a.gid, a.work, a.playbook, a.attach, a.max_anchors)
    if a.cmd == "brief":
        print(prompt)
        return 0
    model = os.environ.get(f"ARENA_MODEL_{a.gid}",
                           os.environ.get("ARENA_MODEL", "qwen3.5:4b"))
    if a.dry_run:
        print(f"DRY-RUN {a.gid}: {a.n} executor calls, model={model}, "
              f"prompt={len(prompt)} chars (~{len(prompt)//4} tok), "
              f"anchors={sum(1 for l in prompt.splitlines() if l.startswith('[L:'))}, "
              f"think={a.think}, max_tokens={a.max_tokens}")
        print("--- first 400 chars ---\n" + prompt[:400])
        return 0
    fp = os.path.join(a.work, "findings.jsonl")
    stamp = utc_stamp()
    total = 0
    for i in range(a.n):
        temp = round(0.2 + 0.1 * (i % 4), 2)
        text = call_api(prompt, model, temp, a.max_tokens, think_off=(a.think == "off"))
        rows = extract_jsonl(text)
        tries = 0
        while not rows and tries < a.retries:
            tries += 1
            text = call_api(prompt + "\n\nREMINDER: reply with JSONL lines ONLY.",
                            model, temp, a.max_tokens, think_off=(a.think == "off"))
            rows = extract_jsonl(text)
        append_findings(fp, rows, a.gid, f"{model}@{stamp}#{i}")
        total += len(rows)
        print(f"executor #{i} (T={temp}): {len(rows)} findings")
    print(f"total: {total} findings -> {fp} (stamped indep=harness)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
