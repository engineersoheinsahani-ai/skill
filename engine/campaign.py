#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""campaign.py — the real 100-agent campaign (v4-pro, ENB exclusive).

Topology EXACTLY like the original v2 division: 16 duty groups (G1..G16 from
engine/orchestrate.py GROUPS — single source of truth), equal split, waves of 10.
Pro difference: the owner's standing law "<= 100 agents" is enforced exactly
(v2 ceil-arithmetic yielded 112 slots for --agents 100; Pro distributes the
remainder to the first groups: 100 = G1..G4 x7 + G5..G16 x6).

Every executor call is a SEPARATE local-model call via harness.py (law 9:
indep=harness, executor=<model>@<stamp>#<slot>). The campaign is resumable:
state lives in work/campaign-state.json; interrupted runs continue where they
stopped. After each completed group: machine checkpoint (matrix3 check + matrix
+ council refresh) so partial campaigns are always usable.

The research pipeline is NEVER executed by agents (owner decision 2026-10-12):
`campaign prep` runs the MACHINE wave over input/ (map, precheck, figureqc,
diffnum, inventory) and every judgment brief embeds the duty-relevant
manuscript excerpt + machine facts. Agents judge; machines measure.

Commands:
  prep    --work W --input DIR [--manuscript PATH]   machine wave (no key)
  plan    --work W [--agents 100]                    slot table + waves + ETA
  run     --work W [--stage division|writers] [--group G6] [--slot G6-a03]
          [--dry-run] [--max-slots N] [--think off] [--max-tokens 1200]
  status  --work W                                   progress table
"""
import argparse, datetime, glob, json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import harness  # noqa: E402

GIDS = [f"G{i}" for i in range(1, 17)]

# G -> literature-anchor pools (ledger rows are keyed by E-gids from the v3.1 study)
MAP_G2E = {
    "G2": ["E6"], "G4": ["E2", "E4"], "G5": ["E2", "E4"], "G6": ["E4", "E5"],
    "G7": ["E6"], "G8": ["E6"], "G9": ["E4", "E6"],
}
# G -> manuscript sections (duty-relevant excerpt only; small-model budget)
MAP_G2SEC = {
    "G1": ["TITLE PAGE"], "G2": ["ABSTRACT"], "G3": ["TITLE PAGE", "Highlights"],
    "G4": ["1. INTRODUCTION"], "G5": ["1. INTRODUCTION", "REFERENCES"],
    "G6": ["3. METHODOLOGY"], "G7": ["2. DATA", "DECLARATIONS"],
    "G8": ["4. RESULTS"], "G9": ["3. METHODOLOGY", "4. RESULTS"],
    "G10": ["5. DISCUSSION", "6. CONCLUSIONS"], "G11": ["5. DISCUSSION", "6. CONCLUSIONS"],
    "G12": ["REFERENCES"], "G13": ["DECLARATIONS"], "G14": ["Highlights", "TITLE PAGE"],
    "G15": ["ABSTRACT", "5. DISCUSSION"],
    "G16": ["ABSTRACT", "1. INTRODUCTION", "4. RESULTS", "6. CONCLUSIONS"],
}
# precheck rule families -> owning G group (machine facts injected into briefs)
PRECHECK2G = {
    "ENB-TP": "G1", "ENB-ABS": "G2", "ENB-KW": "G3", "ENB-HL": "G3", "ENB-GA": "G3",
    "ENB-TBL": "G8", "ENB-FIG": "G8", "REF": "G12", "DAT": "G7",
    "POL": "G13", "SAGER": "G13", "LEFTOVER": "G14", "ENB-LINE": "G14",
}
WRITERS = [
    ("WR-TEXT-1", "abstract + introduction + title page revisions"),
    ("WR-TEXT-2", "methods + results revisions (numbers ONLY from input/results artifacts)"),
    ("WR-TEXT-3", "discussion + conclusions + response-letter scaffolding"),
    ("FIG-MPL", "matplotlib specialist: publication figure code on templates/figures/*"),
    ("FIG-GV", "graphviz specialist: pipeline/architecture diagram code (DOT + wrapper)"),
    ("STAT-CHECK", "statistics wording: uncertainty phrasing, coverage claims, hedge calibration"),
]


def _py(script, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args],
                          capture_output=True, text=True)


def allocate(n):
    """v2 division spirit (equal split, waves of 10) + exact <=100 cap."""
    n = min(max(int(n), 16), 100)
    base, rem = divmod(n, 16)
    slots = []
    for i, gid in enumerate(GIDS):
        cnt = base + (1 if i < rem else 0)
        slots += [f"{gid}-a{k+1:02d}" for k in range(cnt)]
    waves = [slots[i:i + 10] for i in range(0, len(slots), 10)]
    return n, slots, waves


# ---------------------------------------------------------------- machine wave
def resolve_manuscript(inp, override=None):
    """--manuscript > input/manuscript.txt > the single *.txt > *manuscript*.txt."""
    if override:
        return override if os.path.exists(override) else None
    std = os.path.join(inp, "manuscript.txt")
    if os.path.exists(std):
        return std
    cands = sorted(glob.glob(os.path.join(inp, "*.txt"))) if os.path.isdir(inp) else []
    if len(cands) == 1:
        return cands[0]
    pref = [c for c in cands if "manuscript" in os.path.basename(c).lower()]
    return pref[0] if pref else None


def ledger_note(work):
    """Warn loudly when the anchor-pool ledger is absent (public builds ship none)."""
    led = os.path.join(work, "ledger.jsonl")
    if not os.path.exists(led) or os.path.getsize(led) == 0:
        print("NOTE: work/ledger.jsonl missing/empty -> anchor pools EMPTY (rulebook-only")
        print("      briefs; valid but weaker grounding). Owner fix: copy your ledger from")
        print("      the PRIVATE bundle (or journal-arena v3.1 work/ledger.jsonl) into work/,")
        print("      or build one: run.py corpus fetch + run.py ledger add (ceiling-20).")
        return False
    n = sum(1 for l in open(led, encoding="utf-8") if l.strip())
    print(f"ledger: {n} anchor rows available for pools")
    return True


def cmd_prep(a):
    os.makedirs(a.work, exist_ok=True)
    ms = resolve_manuscript(a.input, a.manuscript)
    if not ms:
        cands = sorted(os.path.basename(c) for c in glob.glob(os.path.join(a.input, "*.txt"))) \
            if os.path.isdir(a.input) else []
        print(f"PREP BLOCKED: no manuscript found in {a.input}")
        print("Put the raw text at input/manuscript.txt, or pass --manuscript PATH.")
        if cands:
            print("txt candidates seen:", ", ".join(cands))
        return 1
    if not a.manuscript and os.path.basename(ms) != "manuscript.txt":
        print(f"manuscript auto-selected: {ms}")
    inv = {"manuscript": ms, "manuscript_words": len(open(ms, encoding="utf-8",
           errors="replace").read().split()), "input_dir": a.input}
    for sub in ("figures", "results", "pipeline"):
        d = os.path.join(a.input, sub)
        files = []
        for root, _, fns in os.walk(d):
            for fn in sorted(fns):
                files.append(os.path.relpath(os.path.join(root, fn), a.input))
        inv[sub] = files[:80]
        inv[f"n_{sub}"] = len(files)
    json.dump(inv, open(os.path.join(a.work, "inventory.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"inventory: {inv['manuscript_words']} w | figures {inv['n_figures']} | "
          f"results {inv['n_results']} | pipeline {inv['n_pipeline']}")
    ledger_note(a.work)

    r = _py("manuscript_map.py", ms, os.path.join(a.work, "map"))
    print("map:", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "?")
    mp = os.path.join(a.work, "map", "manuscript-map.json")
    r = _py("precheck.py", mp, ms, os.path.join(a.work, "precheck"))
    print("precheck:", (r.stdout or "").strip() or r.stderr.strip()[:200])
    if inv["n_figures"]:
        r = _py("figureqc.py", "scan", os.path.join(a.input, "figures"),
                "--work", a.work)
        print("figureqc:", (r.stdout or "").strip().splitlines()[-1:] or r.stderr[:200])
    else:
        print("figureqc: skipped (input/figures empty)")
    if inv["n_results"]:
        r = _py("diffnum.py", "check", "--manuscript", ms, "--input", a.input,
                "--work", a.work)
        print("diffnum:", (r.stdout or "").strip().splitlines()[-1:] or r.stderr[:200])
    else:
        print("diffnum: skipped (input/results empty — artifact-diff law 10 inactive)")
    print("PREP DONE — machine facts in", a.work)
    return 0


# ---------------------------------------------------------------- brief assembly
def _sections_text(work, names, cap=6000):
    mp = os.path.join(work, "map", "manuscript-map.json")
    if not os.path.exists(mp):
        return ""
    secs = json.load(open(mp, encoding="utf-8")).get("sections", {})
    keys = {k.lower().lstrip("0123456789. "): k for k in secs}
    out, used = [], 0
    for name in names:
        key = name if name in secs else keys.get(name.lower().lstrip("0123456789. "))
        if not key:
            continue
        t = secs[key]
        room = max(0, cap - used)
        out.append(f"--- [{key}] ---\n" + t[:room])
        used += min(len(t), room)
        if used >= cap:
            break
    return "\n".join(out)


def _machine_digest(work, gid):
    """Deterministic facts for this group's duty (law 10: agents judge, machines measure)."""
    lines = []
    pp = os.path.join(work, "precheck", "precheck.json")
    if os.path.exists(pp):
        mine = [f for f in json.load(open(pp, encoding="utf-8"))
                if any(f["id"].startswith(pre) for pre, g in PRECHECK2G.items() if g == gid)]
        for f in mine[:4]:
            lines.append(f"[precheck {f['id']}|{f['severity']}] {f['issue'][:110]}")
    dn = os.path.join(work, "diffnum.json")
    if os.path.exists(dn) and gid in ("G2", "G8", "G9", "G10"):
        d = json.load(open(dn, encoding="utf-8"))
        lines.append(f"[diffnum] traced {d.get('traced',0)}/{d.get('total',0)} numbers; "
                     f"UNTRACED {len(d.get('untraced',[]))} (top: "
                     + "; ".join(u["num"] + "@" + u.get("context", "")[:24]
                                 for u in d.get("untraced", [])[:4]) + ")")
    fq = os.path.join(work, "figureqc.json")
    if os.path.exists(fq) and gid in ("G3", "G14"):
        d = json.load(open(fq, encoding="utf-8"))
        lines.append(f"[figureqc] {d.get('n_files',0)} files; fails: "
                     + "; ".join(f"{x['file']}:{x['check']}" for x in d.get("fails", [])[:5]))
    iv = os.path.join(work, "inventory.json")
    if os.path.exists(iv):
        d = json.load(open(iv, encoding="utf-8"))
        lines.append(f"[input] results artifacts available: {d.get('n_results',0)} "
                     f"(READ-ONLY; never re-run the pipeline — law 10)")
    return "\n".join(lines)


def brief_for(slot, work, max_anchors=20, excerpt_cap=6000):
    gid = slot.split("-")[0]
    duty_pool = MAP_G2E.get(gid, [])
    txt = harness.assemble(gid, work, anchor_gids=duty_pool or [gid],
                           max_anchors=max_anchors,
                           extra_sections=_sections_text(work, MAP_G2SEC.get(gid, []),
                                                         excerpt_cap))
    dig = _machine_digest(work, gid)
    if dig:
        txt += "\n\n=== MACHINE FACTS (deterministic, already measured) ===\n" + dig
    txt += f"\n\n=== SLOT ===\nYou are executor {slot}. Stamp claim_id prefix '{slot}'."
    return txt


def writer_brief(role, work, cap=8000):
    pb = open(os.path.join(ROOT, "groups", "16-group-playbooks.md"), encoding="utf-8").read()
    import re
    m = re.search(rf"^### {re.escape(role)}(.+?)(?=^### |\Z)", pb, re.S | re.M)
    card = (f"### {role}" + (m.group(1) if m else " (duty card missing)"))
    council = ""
    cp = os.path.join(work, "council-input.md")
    if os.path.exists(cp):
        council = "\n\n=== COUNCIL VERDICTS TO IMPLEMENT ===\n" + open(cp, encoding="utf-8").read()[:cap]
    figs = ""
    if role in ("FIG-MPL", "FIG-GV"):
        sp = os.path.join(ROOT, "templates", "figures", "figure-spec.md")
        if os.path.exists(sp):
            figs = ("\n\n=== FIGURE SPEC + TEMPLATE INDEX ===\n"
                    + open(sp, encoding="utf-8").read()[:6000])
    out = ("You are a WRITER/PRODUCER executor (post-council). Output JSONL only:\n"
           '{"type":"revision","section":"...","old":"...exact...","new":"...","rationale":"..."}\n'
           'or {"type":"figure-code","file":"figures/figX.py","code":"...","rationale":"..."}\n'
           "Never invent numbers: every number comes from input/results artifacts or "
           "carries [number needed].\n\n" + card + council + figs)
    return out


# ---------------------------------------------------------------- run / status
def load_state(work):
    p = os.path.join(work, "campaign-state.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"slots": {}, "writers": {}}


def save_state(work, st):
    json.dump(st, open(os.path.join(work, "campaign-state.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def cmd_plan(a):
    ledger_note(a.work)
    n, slots, waves = allocate(a.agents)
    model_default = os.environ.get("ARENA_MODEL", "qwen3.5:4b")
    per_model = {g: os.environ.get(f"ARENA_MODEL_{g}", model_default) for g in GIDS}
    est_min = round(len(slots) * 3.5)
    plan = {"agents": n, "slots": slots, "waves_of_10": waves, "models": per_model,
            "writers": [w[0] for w in WRITERS],
            "eta_note": f"~{est_min} min sequential on GTX960M-class hardware (heuristic 3.5 min/slot)",
            "date": datetime.date.today().isoformat()}
    p = os.path.join(a.work, "campaign-plan.json")
    os.makedirs(a.work, exist_ok=True)
    json.dump(plan, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i, w in enumerate(waves, 1):
        print(f"wave {i:2d}: {', '.join(w)}")
    print(f"plan: {n} agents / 16 groups / {len(waves)} waves / model default {model_default}")
    print("ETA:", plan["eta_note"], "->", p)
    return 0


def cmd_run(a):
    st = load_state(a.work)
    model_default = os.environ.get("ARENA_MODEL", "qwen3.5:4b")
    if a.stage == "writers":
        slots = [r for r, _ in WRITERS]
        get_brief = lambda s: writer_brief(s, a.work)
        bucket, fp = st["writers"], os.path.join(a.work, "writer-output.jsonl")
    else:
        _, all_slots, _ = allocate(a.agents)
        slots = all_slots
        get_brief = lambda s: brief_for(s, a.work, a.max_anchors, a.excerpt_cap)
        bucket, fp = st["slots"], os.path.join(a.work, "findings.jsonl")
        ledger_note(a.work)
    if a.group:
        slots = [s for s in slots if s.split("-")[0] == a.group]
    if a.slot:
        slots = [s for s in slots if s == a.slot]
    if a.max_slots:
        slots = [s for s in slots if s not in bucket][:a.max_slots]
    if a.dry_run:
        total_chars = 0
        for s in slots:
            gid = s.split("-")[0]
            mdl = os.environ.get(f"ARENA_MODEL_{gid}", model_default)
            b = get_brief(s)
            total_chars += len(b)
            print(f"{s:10s} model={mdl:18s} brief={len(b):6d} chars (~{len(b)//4} tok) "
                  f"anchors={sum(1 for l in b.splitlines() if l.startswith('[L:'))}")
        est = round(len(slots) * 3.5)
        print(f"DRY-RUN: {len(slots)} slots, ~{total_chars//4} tokens total, "
              f"ETA ~{est} min sequential. Set ARENA_API_KEY to run for real.")
        return 0
    if not os.environ.get("ARENA_API_KEY"):
        print("ARENA_API_KEY not set — refusing to fake independence (law 9).")
        print("Ollama:  set ARENA_API_BASE=http://localhost:11434/v1  ARENA_API_KEY=ollama")
        return 1
    stamp0 = datetime.datetime.now(datetime.timezone.utc)
    done_groups = set()
    for idx, s in enumerate(slots, 1):
        if s in bucket:
            continue
        gid = s.split("-")[0]
        model = os.environ.get(f"ARENA_MODEL_{gid}", model_default)
        prompt = get_brief(s)
        temp = round(0.2 + 0.1 * (idx % 4), 2)
        try:
            text = harness.call_api(prompt, model, temp, a.max_tokens,
                                    think_off=(a.think == "off"))
        except Exception as e:                    # keep the campaign alive
            print(f"{s}: CALL FAILED ({e}) — slot left pending, resume later")
            continue
        rows = harness.extract_jsonl(text)
        tries = 0
        while not rows and tries < 1:
            tries += 1
            try:
                text = harness.call_api(prompt + "\n\nREMINDER: JSONL lines ONLY.",
                                        model, temp, a.max_tokens,
                                        think_off=(a.think == "off"))
                rows = harness.extract_jsonl(text)
            except Exception:
                break
        stamp = harness.utc_stamp()
        harness.append_findings(fp, rows, gid, f"{model}@{stamp}#{s}",
                                extra={"aid": s, "campaign": "enb-pro-v4",
                                       "indep": "harness"} if a.stage != "writers"
                                else {"role": s, "campaign": "enb-pro-v4-writers"})
        bucket[s] = {"model": model, "ts": stamp, "rows": len(rows)}
        save_state(a.work, st)
        el = (datetime.datetime.now(datetime.timezone.utc) - stamp0).total_seconds() / 60
        print(f"[{idx}/{len(slots)}] {s}: {len(rows)} rows ({el:.1f} min elapsed)")
        if a.stage != "writers":
            done_groups.add(gid)
    # checkpoint after campaign chunk: refresh aggregate (machine, no key)
    if a.stage != "writers" and os.path.exists(fp):
        for args in (["check", fp], ["matrix", fp, os.path.join(a.work, "matrix-v3.md")],
                     ["council", fp, os.path.join(a.work, "council-input.md")]):
            r = _py("matrix3.py", *args)
            tail = [l for l in (r.stdout or "").splitlines() if l.startswith(("VERDICT", "written"))]
            print("checkpoint:", " | ".join(tail) or (r.stderr or "")[:120])
    save_state(a.work, st)
    print(f"campaign {a.stage}: {len([s for s in slots if s in bucket])}/{len(slots)} slots done")
    return 0


def cmd_status(a):
    st = load_state(a.work)
    pp = os.path.join(a.work, "campaign-plan.json")
    plan = json.load(open(pp, encoding="utf-8")) if os.path.exists(pp) else None
    n, slots, _ = allocate(plan["agents"] if plan else 100)
    print("group  slots  done  findings  model")
    for gid in GIDS:
        gs = [s for s in slots if s.startswith(gid + "-")]
        dn = [s for s in gs if s in st["slots"]]
        fnd = sum(st["slots"][s].get("rows", 0) for s in dn)
        mdl = (plan or {}).get("models", {}).get(gid, os.environ.get("ARENA_MODEL", "qwen3.5:4b"))
        bar = "GREEN" if len(dn) == len(gs) else ("part" if dn else "-")
        print(f"{gid:5s} {len(gs):5d} {len(dn):5d} {fnd:9d}  {mdl}  {bar}")
    wr = st.get("writers", {})
    print(f"writers: {len(wr)}/{len(WRITERS)} done")
    fj = os.path.join(a.work, "findings.jsonl")
    if os.path.exists(fj):
        tot = sum(1 for l in open(fj, encoding="utf-8") if l.strip())
        print(f"findings.jsonl total rows: {tot}")
    return 0


def cmd_briefs(a):
    """Dump the exact prompt files (no API calls): inspection or paste-back use."""
    outdir = a.out or os.path.join(a.work, "briefs")
    os.makedirs(outdir, exist_ok=True)
    if not os.path.exists(os.path.join(a.work, "map", "manuscript-map.json")):
        print("WARNING: no manuscript map in work/ — run `run.py prep` FIRST;")
        print("         briefs dumped now would lack excerpts and machine facts.")
    if a.stage == "writers":
        slots = [r for r, _ in WRITERS]
        get_brief = lambda s: writer_brief(s, a.work)
    else:
        _, slots, _ = allocate(a.agents)
        get_brief = lambda s: brief_for(s, a.work, a.max_anchors, a.excerpt_cap)
    if a.group:
        slots = [s for s in slots if s.split("-")[0] == a.group]
    if a.slot:
        slots = [s for s in slots if s == a.slot]
    for s in slots:
        b = get_brief(s)
        open(os.path.join(outdir, f"brief-{s}.txt"), "w", encoding="utf-8").write(b + "\n")
    print(f"briefs: wrote {len(slots)} prompt files -> {outdir}")
    print("paste-back use: send a file to any model, save the reply, then")
    print("  python3 engine/harness.py ingest --gid <G> --file reply.txt "
          "--indep human --label \"<model>@paste#1\"")
    return 0


def cmd_ingest_dir(a):
    """AGENT MODE (no API): ingest per-slot answer files <slot>.txt from work/answers/.

    A cloning agent (or any operator) answers the dumped briefs itself and saves
    one text file per slot; this command extracts the JSONL, stamps law-9 labels
    HONESTLY (--indep single = same-session agent wearing 100 hats; human =
    paste-back by the owner) and marks slots done so status/resume keep working.
    """
    ans = a.dir or os.path.join(a.work, "answers")
    if not os.path.isdir(ans):
        print(f"ingest-dir: no answers directory at {ans}")
        print("Agent mode: 1) campaign briefs  2) answer each brief  3) save as")
        print(f"            {os.path.join(a.work, 'answers', '<slot>.txt')}  4) re-run this command.")
        return 1
    st = load_state(a.work)
    _, all_slots, _ = allocate(a.agents)
    valid = set(r for r, _ in WRITERS) if a.stage == "writers" else set(all_slots)
    bucket = st["writers"] if a.stage == "writers" else st["slots"]
    fp = os.path.join(a.work, "writer-output.jsonl" if a.stage == "writers"
                      else "findings.jsonl")
    label = a.label or "agent@clone"
    stamp = harness.utc_stamp()
    ing = skip = empty = 0
    for fn in sorted(os.listdir(ans)):
        if not fn.endswith(".txt"):
            continue
        slot = fn[:-4]
        if slot not in valid:
            print(f"  {slot}: not a valid {a.stage} slot name — ignored")
            continue
        if slot in bucket and not a.force:
            skip += 1
            continue
        text = open(os.path.join(ans, fn), encoding="utf-8", errors="replace").read()
        rows = harness.extract_jsonl(text)
        if not rows:
            print(f"  {slot}: no JSONL objects in answer — slot left pending")
            empty += 1
            continue
        gid = slot.split("-")[0]
        extra = ({"role": slot, "campaign": "enb-pro-v4-writers"} if a.stage == "writers"
                 else {"aid": slot, "campaign": "enb-pro-v4"})
        harness.append_findings(fp, rows, gid, f"{label}#{slot}", a.indep, extra)
        bucket[slot] = {"model": label, "ts": stamp, "rows": len(rows),
                        "indep": a.indep, "mode": "agent"}
        ing += 1
        print(f"  {slot}: {len(rows)} rows (indep={a.indep})")
    save_state(a.work, st)
    print(f"ingest-dir: {ing} ingested, {skip} already-done skipped, {empty} empty -> {fp}")
    if a.stage != "writers" and ing:
        print("next (machine, no key): run.py check / matrix / council / validate")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prep", "plan", "run", "status", "briefs",
                                    "ingest-dir"])
    ap.add_argument("--work", default="work")
    ap.add_argument("--input", default=os.path.join(ROOT, "input"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--label", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--indep", default="single", choices=["single", "human", "harness"])
    ap.add_argument("--manuscript", default=None)
    ap.add_argument("--agents", type=int, default=100)
    ap.add_argument("--stage", default="division", choices=["division", "writers"])
    ap.add_argument("--group", default=None)
    ap.add_argument("--slot", default=None)
    ap.add_argument("--max-slots", type=int, default=0)
    ap.add_argument("--max-anchors", type=int, default=20)
    ap.add_argument("--excerpt-cap", type=int, default=6000)
    ap.add_argument("--max-tokens", type=int, default=1200)
    ap.add_argument("--think", default="off", choices=["off", "on"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    return {"prep": cmd_prep, "plan": cmd_plan, "run": cmd_run,
            "status": cmd_status, "briefs": cmd_briefs,
            "ingest-dir": cmd_ingest_dir}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
