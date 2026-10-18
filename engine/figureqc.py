#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""figureqc.py — deterministic figure QC against ENB/Elsevier artwork specs.

Machine layer (law 9: indep=machine). Zero-dependency PNG parsing (IHDR/pHYs);
PIL is OPTIONAL and adds TIFF/JPEG support + colour-blindness confusion checks.

Checks per file:
  format      TIFF/EPS/PDF/PNG/JPG accepted by Elsevier artwork guidelines
  dpi         >= 300 (photos/combination); >= 600 heuristic for line art
              (palette PNG); missing pHYs => flagged (assume 72)
  width       print width at embedded dpi vs single column 1063 px /
              full page 2244 px @300dpi equivalents
  mode        RGB/CMYK/Gray reported (CMYK => info, not fail)
  colourblind (PIL only) simulated protanopia/deuteranopia palette-collapse pairs
  fonts       HONEST LIMIT: font size inside rasters is NOT machine-verifiable
              => every raster gets an owner-check flag (>= 7 pt at final size)
  vector      PDF/EPS/SVG => pass with "embed fonts" note

Usage:
  python3 engine/figureqc.py scan input/figures [--work W] [--emit-findings]
"""
import argparse, json, os, struct, sys

SINGLE_COL_PX = 1063      # ENB/Elsevier @ ~300 dpi (checklists/01 ENB-FIG-2)
FULL_PAGE_PX = 2244
RASTER_EXT = ("png", "tif", "tiff", "jpg", "jpeg", "bmp")
VECTOR_EXT = ("pdf", "eps", "svg", "ai")


def png_info(path):
    """Pure-python PNG header parse: (w, h, bitdepth, colortype, dpi|None, palette_colors|None)."""
    with open(path, "rb") as f:
        data = f.read(200_000)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, w = 8, None
    h = bd = ct = dpi = pal = None
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", body[:10])
        elif typ == b"pHYs":
            ppu_x = struct.unpack(">I", body[:4])[0] if len(body) >= 4 else 0
            unit = body[8] if len(body) > 8 else 0
            if unit == 1:
                dpi = round(ppu_x * 0.0254)
        elif typ == b"PLTE":
            pal = ln // 3
        elif typ == b"IDAT":
            break
        pos += 12 + ln
    if w is None:
        return None
    return {"w": w, "h": h, "bitdepth": bd, "colortype": ct, "dpi": dpi,
            "palette_colors": pal}


def cvd_confusion(path, max_colors=48, thresh=14.0):
    """PIL-only: simulate protanopia/deuteranopia; count palette pairs that collapse."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(path).convert("RGB").resize((160, 160))
    except Exception:
        return None
    cols = {}
    for px in im.getdata():
        key = tuple(c // 24 * 24 for c in px)
        cols[key] = cols.get(key, 0) + 1
    top = [c for c, _ in sorted(cols.items(), key=lambda kv: -kv[1])[:max_colors]]
    M_P = ((0.567, 0.433, 0.0), (0.558, 0.442, 0.0), (0.0, 0.242, 0.758))   # protanopia
    M_D = ((0.625, 0.375, 0.0), (0.70, 0.30, 0.0), (0.0, 0.30, 0.70))       # deuteranopia
    def sim(c, M):
        return tuple(sum(M[i][j] * c[j] for j in range(3)) for i in range(3))
    pairs = 0
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            for M in (M_P, M_D):
                a, b = sim(top[i], M), sim(top[j], M)
                if sum((a[k] - b[k]) ** 2 for k in range(3)) ** 0.5 < thresh:
                    pairs += 1
                    break
    return pairs


def check_file(path):
    fails, infos = [], []
    ext = path.lower().rsplit(".", 1)[-1] if "." in path else ""
    name = os.path.basename(path)
    if ext in VECTOR_EXT:
        infos.append({"check": "vector", "detail": "vector artwork OK — ensure fonts embedded"})
        return name, fails, infos
    if ext not in RASTER_EXT:
        infos.append({"check": "format", "detail": f".{ext} not a standard artwork format"})
        return name, fails, infos
    info = None
    if ext == "png":
        info = png_info(path)
    if info is None:
        try:
            from PIL import Image
            im = Image.open(path)
            dpi = im.info.get("dpi")
            info = {"w": im.width, "h": im.height, "dpi": round(dpi[0]) if dpi else None,
                    "colortype": im.mode, "palette_colors": None}
        except Exception:
            fails.append({"check": "parse", "detail": "cannot parse header (install Pillow for TIFF/JPEG)"})
            return name, fails, infos
    dpi = info.get("dpi")
    w = info["w"]
    if dpi is None:
        fails.append({"check": "dpi-missing", "detail": "no embedded DPI (pHYs) — assumed 72; re-export at 300+"})
        dpi = 72
    line_art = (info.get("colortype") == 3 and (info.get("palette_colors") or 999) <= 64)
    need = 600 if line_art else 300
    if dpi < need:
        fails.append({"check": "dpi", "detail": f"{dpi} dpi < {need} required "
                                                f"({'line art' if line_art else 'photo/combination'})"})
    if w < SINGLE_COL_PX:
        fails.append({"check": "width", "detail": f"{w}px < {SINGLE_COL_PX}px single-column @300dpi"})
    elif w >= FULL_PAGE_PX:
        infos.append({"check": "width", "detail": f"{w}px — full-page width class ({FULL_PAGE_PX}px)"})
    mode = info.get("colortype")
    if isinstance(mode, str) and "CMYK" in mode:
        infos.append({"check": "mode", "detail": "CMYK — Elsevier accepts; RGB preferred for online"})
    conf = cvd_confusion(path)
    if conf is not None and conf > 0:
        fails.append({"check": "colourblind", "detail": f"{conf} palette pair(s) collapse under "
                                                        "protanopia/deuteranopia simulation"})
    elif conf is not None:
        infos.append({"check": "colourblind", "detail": "no red-green confusion detected in palette"})
    infos.append({"check": "fonts", "detail": "font size NOT machine-verifiable in raster — "
                                              "owner must confirm >= 7 pt at final print size"})
    return name, fails, infos


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["scan"])
    ap.add_argument("dir")
    ap.add_argument("--work", default="work")
    ap.add_argument("--emit-findings", action="store_true")
    a = ap.parse_args(argv)
    files = sorted(os.path.join(r, f) for r, _, fs in os.walk(a.dir) for f in fs
                   if not f.startswith("."))
    all_fails, all_infos, lines = [], [], ["# figureqc report — ENB artwork specs", "",
                                           f"files scanned: {len(files)}", ""]
    for p in files:
        name, fails, infos = check_file(p)
        for x in fails:
            all_fails.append({"file": name, **x})
        for x in infos:
            all_infos.append({"file": name, **x})
        status = "FAIL" if fails else ("ok" if infos else "?")
        lines.append(f"## {name} — {status}")
        for x in fails:
            lines.append(f"- FAIL [{x['check']}] {x['detail']}")
        for x in infos:
            lines.append(f"- note [{x['check']}] {x['detail']}")
        lines.append("")
    os.makedirs(a.work, exist_ok=True)
    out = {"n_files": len(files), "fails": all_fails, "infos": all_infos}
    json.dump(out, open(os.path.join(a.work, "figureqc.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    open(os.path.join(a.work, "figureqc-report.md"), "w", encoding="utf-8").write(
        "\n".join(lines))
    print(f"figureqc: {len(files)} files | {len(all_fails)} FAIL | report -> "
          f"{a.work}/figureqc-report.md")
    if a.emit_findings and all_fails:
        fp = os.path.join(a.work, "findings.jsonl")
        with open(fp, "a", encoding="utf-8") as f:
            for i, x in enumerate(all_fails[:12], 1):
                row = {"claim_id": f"FIGQC-{i:03d}", "gid": "G14", "verdict": "violates-spec",
                       "lit_quote": "ENB-FIG-2 Photos >=300 dpi (single col 1063 px / full page "
                                    "2244 px); line art >=1000 dpi; ENB-FIG-1 artwork cited, "
                                    "numbered in order",
                       "lit_quote_id": "L:rule-enb-fig-2", "lit_tier": "rulebook",
                       "anchor_type": "machine", "severity": "major",
                       "action": f"{x['file']}: fix [{x['check']}] — {x['detail']}",
                       "ms_quote": f"(file property) {x['file']}",
                       "indep": "machine", "executor": "engine/figureqc.py@run",
                       "machine_verified": f"figureqc {x['check']}"}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"emitted {min(12, len(all_fails))} machine findings (gid G14) -> {fp}")
    return 1 if all_fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
