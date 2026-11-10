"""Reading PDF of one edu/pages HTML: Letter, black only, 9.5 pt, figures at 72 % width.
usage: python3 page_print.py <page-name-without-.html> [...]"""
import pathlib, subprocess, sys, tempfile, shutil

PAGES = pathlib.Path(__file__).resolve().parent.parent
PCSS = """<style>
  @page { size: letter; margin: 12mm 13mm 14mm; }
  :root { --bg:#fff; --surface:#fff; --ink:#000; --muted:#333; --line:#999; --accent:#000; --accent-ink:#000; --accent-tint:#f2f2f2; --brass:#444; --brass-tint:#f0f0f0; --warn:#222; --warn-tint:#f4f4f4; --pass:#000; --pass-tint:#f2f2f2; --code-bg:#f0f0f0; --figure-bg:#fff;
          --w-red:#000; --w-black:#000; --w-yellow:#555; --w-green:#000; --w-blue:#333; --w-white:#777; --w-orange:#222; --w-olive:#444; --w-purple:#222; --w-teal:#000; --w-navy:#000; --w-pink:#555; }
  html, body { background:#fff !important; color:#000 !important; font-size:9.5pt !important; line-height:1.4; }
  .wrap { max-width:none; padding:0; }
  .progress, button.reset, details.more > summary { display:none !important; } details.more { margin-left:0; }
  figure { width:72%; margin:6pt auto 8pt; break-inside:avoid; page-break-inside:avoid; border-color:#bbb; }
  figure svg { min-width:0 !important; width:100% !important; filter:grayscale(1); }
  figcaption { font-size:8.5pt; } .step { break-inside:avoid; page-break-inside:avoid; }
  table.t { font-size:8.5pt; } h2 { page-break-after:avoid; font-size:14pt; margin-top:18pt; } h3 { font-size:11pt; } .lede { font-size:10pt; }
  .step input { width:11pt; height:11pt; } a { color:#000; text-decoration:none; } pre, code { background:#f0f0f0; } p, li { max-width:none; }
  .own, .buy { color:#000; }
</style>"""


def print_page(name):
    src = (PAGES / f"{name}.html").read_text()
    src = src.replace('<details class="more">', '<details class="more" open>')
    with tempfile.TemporaryDirectory() as d:
        html = pathlib.Path(d) / f"{name}.html"; pdf = pathlib.Path(d) / f"{name}.pdf"
        html.write_text("<!doctype html><meta charset=utf-8>" + src.replace("</style>", "</style>" + PCSS, 1))
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{html}"], check=True, capture_output=True, timeout=180)
        out = PAGES / "print" / f"{name}.pdf"
        shutil.copyfile(pdf, out)
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print(name, "→", out.name, [l for l in info.splitlines() if l.startswith("Pages")][0])


def print_letter_svg(svg_name, pdf_name):
    """A 1:1 Letter SVG (mm units) to a Letter PDF with no margins."""
    svg = (PAGES / svg_name).read_text()
    with tempfile.TemporaryDirectory() as d:
        html = pathlib.Path(d) / "t.html"; pdf = pathlib.Path(d) / "t.pdf"
        html.write_text('<!doctype html><meta charset=utf-8><style>@page{size:letter;margin:0} html,body{margin:0;padding:0} svg{display:block}</style>' + svg)
        subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", f"file://{html}"], check=True, capture_output=True, timeout=180)
        out = PAGES / pdf_name
        shutil.copyfile(pdf, out)
    info = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    print(svg_name, "→", out.name, [l for l in info.splitlines() if l.startswith(("Pages", "Page size"))])


if __name__ == "__main__":
    for n in sys.argv[1:]:
        print_page(n)
