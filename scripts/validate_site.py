from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import sys

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

html_files = sorted(ROOT.glob("*.html"))
required = {
    "index.html",
    "404.html",
    "gizlilik-politikasi.html",
    "cerez-politikasi.html",
    "kvkk-aydinlatma-metni.html",
    "kullanim-sartlari.html",
    "iletisim.html",
}

missing = required - {path.name for path in html_files}
if missing:
    errors.append(f"Eksik dosyalar: {', '.join(sorted(missing))}")

for path in html_files:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    if not soup.title or not soup.title.get_text(strip=True):
        errors.append(f"{path.name}: title eksik")
    if not soup.html or soup.html.get("lang") != "tr":
        errors.append(f"{path.name}: lang=tr eksik")
    if not soup.find("meta", attrs={"name": "viewport"}):
        errors.append(f"{path.name}: viewport meta eksik")
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        parsed = urlparse(href)
        if parsed.scheme or href.startswith("#") or href.startswith("mailto:"):
            continue
        candidate = ROOT / (parsed.path.lstrip("/") or "index.html")
        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.exists() and not candidate.with_suffix(".html").exists():
            errors.append(f"{path.name}: kırık dahili bağlantı {href}")

index_text = (ROOT / "index.html").read_text(encoding="utf-8")
index_soup = BeautifulSoup(index_text, "html.parser")
if not index_soup.find("h1"):
    errors.append("index.html: h1 eksik")
if "el.innerHTML" in index_text or "+n+" in index_text:
    errors.append("index.html: kullanıcı girdisi için riskli innerHTML kalıbı bulundu")

headers = (ROOT / "_headers").read_text(encoding="utf-8")
for header in ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]:
    if header not in headers:
        errors.append(f"_headers: {header} eksik")

try:
    ET.parse(ROOT / "sitemap.xml")
except ET.ParseError as exc:
    errors.append(f"sitemap.xml geçersiz: {exc}")

inline_scripts = [script.string for script in index_soup.find_all("script") if script.string]
Path("/tmp/kargorapor-index-inline.js").write_text("\n".join(inline_scripts), encoding="utf-8")

if errors:
    print("DOĞRULAMA BAŞARISIZ")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(f"DOĞRULAMA BAŞARILI: {len(html_files)} HTML dosyası ve dahili bağlantılar kontrol edildi.")
