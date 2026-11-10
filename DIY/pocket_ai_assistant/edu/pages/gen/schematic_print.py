"""Print version of pip-schematic.html: one Letter page per figure, black only (edu/pages/print/pip-schematic.pdf)."""
import pathlib, re, subprocess, tempfile, shutil

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "pip-schematic.html"
OUT = HERE.parent / "print" / "pip-schematic.pdf"

s = SRC.read_text()
svgs = re.findall(r"<svg.*?</svg>", s, re.S)
style, extra = re.findall(r"<style>.*?</style>", s, re.S)[:2]
pcss = """<style>@page { size: letter; margin: 10mm; } html,body{background:#fff;margin:0}
:root { --bg:#fff; --surface:#fff; --ink:#000; --muted:#333; --line:#999; --accent:#000; --accent-ink:#000; --accent-tint:#f2f2f2; --brass:#444; --brass-tint:#f0f0f0; --warn:#222; --warn-tint:#f4f4f4; --pass:#000; --pass-tint:#f2f2f2; --code-bg:#f0f0f0; --figure-bg:#fff;
 --w-red:#000; --w-black:#000; --w-yellow:#666; --w-green:#000; --w-blue:#333; --w-white:#888; --w-orange:#444; --w-olive:#444; --w-purple:#222; --w-teal:#000; --w-navy:#000; --w-pink:#555; }
figure{margin:0;border:0;padding:0;background:#fff;page-break-after:always} figure:last-of-type{page-break-after:auto} figure svg{height:auto;display:block;margin:0 auto;filter:grayscale(1)}
figure.a svg{width:180mm} figure.b svg{width:148mm}
p{font:8pt sans-serif;margin:2mm auto 0;width:180mm}</style>"""
html = ("<!doctype html><meta charset=utf-8><title>Pip schematic</title>" + style + extra + pcss
        + f"<figure class='a'>{svgs[0]}<p>Pin to pin with the two rails · dots are joints, rings are taps, every crossing is a hop · edu/pages/pip-schematic.html</p></figure>"
        + f"<figure class='b'>{svgs[1]}<p>The same device as rails and lanes · place parts anywhere, keep the joints</p></figure>")
with tempfile.TemporaryDirectory() as d:
    src = pathlib.Path(d) / "sch-print.html"; pdf = pathlib.Path(d) / "sch-print.pdf"
    src.write_text(html)
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", f"file://{src}"], check=True, capture_output=True, timeout=90)
    shutil.copyfile(pdf, OUT)
print("wrote", OUT, subprocess.run(["pdfinfo", str(OUT)], capture_output=True, text=True).stdout.split("Pages:")[1].split()[0], "pages")
