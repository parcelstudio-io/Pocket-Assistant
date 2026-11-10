"""Prints Mochi's paper templates 1:1 on US Letter, black only: page 1 the hoop profile and the side disc, page 2 the card wrap.

    python3 mochi_templates.py      writes ../print/mochi-templates.pdf (Rev B, the gears, approved); --wheel white writes mochi-templates-rev-a.pdf

Print at Actual size (100 %), never Fit to page; the 100 mm bar on each page is the check."""
from __future__ import annotations
import pathlib, re, shutil, subprocess, tempfile, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mochi_build as M

PRINT = HERE.parent / "print"; PRINT.mkdir(exist_ok=True)
BLACK = ("<style>:root{--bg:#fff;--fg:#000;--muted:#333;--line:#999;--panel:#fff;--hid:#fff;--brass:#000;--brass-dk:#000;--steel:#666;--ivory:#fff;--ivory-2:#fff;"
         "--skin-edge:#000;--black:#000;--black-2:#222;--window:#777;--tyre:#000;--tyre-2:#333;--glass:#000;--eye:#fff;--lens:#000;--beam:#000;--scan:#000;--desk:#ddd;--ink:#000}"
         "html,body{background:#fff;margin:0;color:#000;font-family:'IBM Plex Sans',system-ui,sans-serif}"
         "svg text{font-family:ui-monospace,Menlo,monospace;font-size:7.5px;fill:#000} svg text.hid{font-size:6.5px;fill:#222} svg text.dimlab{font-size:7px;fill:#000} svg text.tag{fill:#000}"
         "h1{font-size:14pt;margin:0 0 2mm;font-weight:600} p{font-size:9.5pt;margin:0 0 2mm;line-height:1.35} .row{display:flex;gap:6mm;align-items:flex-start}"
         ".bar{margin-top:3mm} table{border-collapse:collapse;font-size:8.5pt} td,th{border-bottom:0.3pt solid #999;padding:1pt 6pt 1pt 0;text-align:left;vertical-align:top}</style>")


def mm_svg(svg, w, h):
    return re.sub(r"<svg ", f'<svg width="{w}mm" height="{h}mm" ', svg, count=1)


def ruler(length=100):
    s = M.C.S
    o = [f'<svg width="{length + 6}mm" height="8mm" viewBox="0 0 {(length + 6) * s} {8 * s}">']
    o.append(f'<line x1="{3*s}" y1="{4*s}" x2="{(3+length)*s}" y2="{4*s}" stroke="#000" stroke-width="1.2"/>')
    for i in range(0, length + 1, 10):
        o.append(f'<line x1="{(3+i)*s}" y1="{2*s}" x2="{(3+i)*s}" y2="{6*s}" stroke="#000" stroke-width="1"/>')
    o.append(f'<text x="{(3+length/2)*s}" y="{7.6*s}" text-anchor="middle" style="font-size:7px">{length} mm when printed at actual size</text></svg>')
    return "".join(o)


def main():
    kind = sys.argv[sys.argv.index("--wheel") + 1] if "--wheel" in sys.argv else "gear"    # Rev B (approved 2026-11-07 evening); --wheel white prints Rev A
    M.configure(kind)
    rev = "Rev B, gear wheels" if kind == "gear" else "Rev A, white wheels"
    figs = M.frame_and_card(); (hw, hh), (ww, wh), (dw, dh) = M.frame_and_card.sizes
    hoop, wrap, disc = (f for f, c in figs)
    rods = "".join(f"<tr><td>{M.esc(p)}</td><td>{q}</td><td>{r}</td><td>{l}</td><td>{M.esc(wh_)}</td></tr>" for p, q, r, l, wh_ in M.RODS)
    page1 = (f"<!doctype html><meta charset=utf-8><style>@page{{size:letter;margin:12mm 13mm 12mm}}</style>{BLACK}"
             f"<h1>Mochi templates, 1:1 · {rev} · page 1 of 2 · hoop profile and side disc</h1>"
             f"<p>Print at Actual size, not Fit. Check the bar. Bend each hoop of 1.5 mm brass rod on the outline (rod centreline), r 4 at the four corners, lap 6 mm at the bottom centre and solder. "
             f"The dots are where the 1.0 mm rods between the two hoops meet this profile; the disc is the card that fills each hoop, glued to its inner face.</p>"
             f"<div class='row'>{mm_svg(hoop, hw, hh)}{mm_svg(disc, dw, dh)}</div><div class='bar'>{ruler()}</div>"
             f"<table><tr><th>Piece</th><th>Qty</th><th>Rod</th><th>mm each</th><th>Where</th></tr>{rods}</table>")
    page2 = (f"<!doctype html><meta charset=utf-8><style>@page{{size:letter landscape;margin:10mm 12mm}}</style>{BLACK}"
             f"<h1>Mochi templates, 1:1 · {rev} · page 2 of 2 · the card wrap</h1>"
             f"<p>One strip of cardstock, 209 × 54.5 mm, running inside the hoops: back, top, front, floor, with a 3 mm arc between each pair (the shaded bands). "
             f"Cut every opening but the lidar hole before spraying; cut the lidar hole last, to the flange you measure. The hatch stays a flap: cut three sides.</p>"
             f"{mm_svg(wrap, ww, wh)}<div class='bar'>{ruler()}</div>")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "p1.html").write_text(page1); (d / "p2.html").write_text(page2)
        for src in ("p1", "p2"):
            subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                            f"--print-to-pdf={d / (src + '.pdf')}", f"file://{d / (src + '.html')}"], check=True, capture_output=True, timeout=180)
        out = PRINT / ("mochi-templates.pdf" if kind == "gear" else "mochi-templates-rev-a.pdf")
        subprocess.run(["pdfunite", str(d / "p1.pdf"), str(d / "p2.pdf"), str(out)], check=True)
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print(out, [l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])


if __name__ == "__main__":
    main()
