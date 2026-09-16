#!/usr/bin/env python3
"""
seiten_zu_pdf.py - Wiki-Artikel, Forenthreads und Fachartikel als einheitliche PDFs sichern (Privatkopie).

  python seiten_zu_pdf.py wiki  --api https://wiki.germanscooterforum.de/api.php --titel "Kontakt-Zündung einstellen" ... --ziel D:/DoomsdayBox/own/fahrzeuge/vespa_gsf-wiki
  python seiten_zu_pdf.py wiki  --api ... --suche "smallframe|v50|zünd|kurbel"      # alle Seiten, deren Titel passt
  python seiten_zu_pdf.py url   --ziel D:/DoomsdayBox/own/fahrzeuge/defender_forenwissen  https://... https://...
  python seiten_zu_pdf.py liste --ziel ... quellen.txt                                 # eine URL je Zeile, optional "URL | Dateiname"

Erzeugt je Seite ein PDF (A4, Textfluss, Bilder eingebettet, Quelle + Datum im Fuss) sowie INDEX.md im Zielordner.
MediaWiki: Inhalt ueber action=parse (sauberes HTML ohne Navigation). Sonstige Seiten: groesster Textblock
(article/main/Beitraege), Navigation/Skripte/Werbung entfernt. Forenthreads: alle Beitraege der ersten Seiten.
"""
import argparse, html, io, re, sys, time, urllib.parse, urllib.request, urllib.error
from datetime import date
from pathlib import Path
import pymupdf
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
      "Accept-Language": "de,en;q=0.8"}
HEUTE = date.today().isoformat()
CSS = """
body { font-family: sans-serif; font-size: 9.5pt; line-height: 1.35; }
h1 { font-size: 16pt; margin: 0 0 4pt 0; } h2 { font-size: 12.5pt; margin: 10pt 0 3pt 0; } h3 { font-size: 11pt; margin: 8pt 0 2pt 0; }
p { margin: 0 0 5pt 0; } li { margin: 0 0 2pt 0; }
table { border-collapse: collapse; font-size: 8.5pt; } td, th { border: 0.5pt solid #999; padding: 2pt 4pt; }
img { max-width: 100%; }
.quelle { color: #666; font-size: 8pt; margin-bottom: 8pt; }
.beitrag { border-top: 0.5pt solid #bbb; padding-top: 5pt; margin-top: 8pt; }
.autor { color: #444; font-size: 8.5pt; font-weight: bold; }
pre, code { font-family: monospace; font-size: 8pt; }
a { color: inherit; text-decoration: none; }
"""


def holen(url, binary=False, referer=None, timeout=60):
    # Nicht-ASCII-Zeichen in URLs (z.B. Umlaute in Bildpfaden) prozentkodieren, sonst UnicodeEncodeError
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@!$()*[]~-._")
    hdr = dict(UA)
    if referer:
        hdr["Referer"] = referer
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=timeout) as r:
                data = r.read()
            time.sleep(0.4)
            return data if binary else data.decode("utf-8", "replace")
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            if i == 2:
                print(f"    FEHLER {type(e).__name__}: {url}", flush=True)
                return None
            time.sleep(2 * (i + 1))


def dateiname(s):
    s = html.unescape(s)
    s = re.sub(r"[\\/:*?\"<>|#%&{}$!'`@+=]+", "-", s)
    s = re.sub(r"\s+", "-", s.strip())
    return re.sub(r"-{2,}", "-", s)[:90].strip("-") or "seite"


# ---------------------------------------------------------------- HTML -> PDF (pymupdf Story)
def html_zu_pdf(titel, quelle_url, inhalt_html, ziel, bilder_basis):
    """inhalt_html: bereinigtes HTML (nur Inhalt). Bilder werden geladen, in PNG gewandelt und eingebettet."""
    arch = pymupdf.Archive()
    n_img = 0

    def bild(m):
        nonlocal n_img
        src = html.unescape(m.group(1))
        if src.startswith("data:"):
            return ""
        absolut = urllib.parse.urljoin(bilder_basis, src)
        raw = holen(absolut, binary=True, referer=bilder_basis)
        if not raw:
            return ""
        try:
            im = Image.open(io.BytesIO(raw))
            if im.width < 60 or im.height < 60:
                return ""  # Icons, Smilies
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            if im.width > 1600:
                im = im.resize((1600, int(im.height * 1600 / im.width)))
            out = io.BytesIO(); im.save(out, format="PNG")
            name = f"img{n_img}.png"; n_img += 1
            arch.add(out.getvalue(), name)
            w = min(im.width, 640)
            return f'<p><img src="{name}" width="{w}"/></p>'
        except Exception:
            return ""

    inhalt_html = re.sub(r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>", bild, inhalt_html, flags=re.I)
    doc_html = (f"<h1>{html.escape(titel)}</h1><p class='quelle'>Quelle: {html.escape(quelle_url)} · abgerufen {HEUTE} · "
                f"Privatkopie für den Eigengebrauch</p>{inhalt_html}")
    story = pymupdf.Story(html=doc_html, user_css=CSS, archive=arch)
    out = pymupdf.DocumentWriter(str(ziel))
    rect = pymupdf.paper_rect("a4"); where = rect + (36, 36, -36, -40)
    more = True; seiten = 0
    while more and seiten < 400:
        dev = out.begin_page(rect)
        more, _ = story.place(where)
        story.draw(dev)
        out.end_page(); seiten += 1
    out.close()
    doc = pymupdf.open(str(ziel))
    for pg in doc:
        pg.insert_text((36, rect.height - 22), f"{titel[:90]}  |  {quelle_url[:70]}  |  {HEUTE}", fontsize=6.5, color=(0.5, 0.5, 0.5))
    doc.set_metadata({"title": titel, "subject": f"Privatkopie von {quelle_url}", "creationDate": pymupdf.get_pdf_now()})
    doc.save(str(ziel), incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()
    return seiten, n_img


# ---------------------------------------------------------------- Bereinigung
def saeubern(h):
    h = re.sub(r"<(script|style|noscript|svg|form|iframe|nav|footer|header|aside)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    h = re.sub(r"<(div|span|section|article|ul|ol|li|table|tr|td|th|p|h[1-6]|a|img|b|strong|i|em|br|pre|code|blockquote|sup|sub)\b([^>]*)>",
               lambda m: "<" + m.group(1) + (" " + " ".join(a for a in re.findall(r'(?:href|src|colspan|rowspan)="[^"]*"', m.group(2)))
                                              if re.findall(r'(?:href|src|colspan|rowspan)="[^"]*"', m.group(2)) else "") + ">", h, flags=re.I)
    h = re.sub(r"</?(?!(?:div|span|section|article|ul|ol|li|table|tr|td|th|p|h[1-6]|a|img|b|strong|i|em|br|pre|code|blockquote|sup|sub)\b)[a-zA-Z][^>]*>", " ", h)
    h = re.sub(r"<a\s*>", "", h); h = re.sub(r"</a>", "", h)  # Links ohne Ziel weg
    return h


def hauptinhalt(h, url):
    """Groessten inhaltlichen Block finden; Forenthreads: Beitraege einsammeln."""
    # Invision (GSF, theminiforum), vBulletin, phpBB, XenForo (landyzone)
    beitraege = re.findall(r'<article[^>]*class="[^"]*(?:cPost|message|post)[^"]*"[^>]*>(.*?)</article>', h, re.S | re.I)
    if not beitraege:
        beitraege = re.findall(r'<div[^>]*class="[^"]*(?:postbody|post_body|message-body|bbWrapper)[^"]*"[^>]*>(.*?)</div>\s*</div>', h, re.S | re.I)
    if len(beitraege) >= 2:
        teile = []
        for b in beitraege[:60]:
            autor = re.search(r'(?:data-author|itemprop="name"[^>]*>|class="[^"]*(?:username|author)[^"]*"[^>]*>)\s*"?([^"<]{2,40})', b)
            body = re.search(r'(?:data-role="commentContent"|class="[^"]*(?:cPost_contentWrap|message-content|bbWrapper|postbody)[^"]*")[^>]*>(.*?)$', b, re.S)
            teile.append(f"<div class='beitrag'><p class='autor'>{html.escape(autor.group(1).strip()) if autor else ''}</p>{body.group(1) if body else b}</div>")
        return "".join(teile), "forum"
    for pat in (r'<div[^>]*(?:id="mw-content-text"|class="[^"]*mw-parser-output[^"]*")[^>]*>(.*)',
                r"<article[^>]*>(.*?)</article>", r"<main[^>]*>(.*?)</main>",
                r'<div[^>]*(?:id|class)="[^"]*(?:entry-content|post-content|article-content|content-area|td-post-content|blog-post)[^"]*"[^>]*>(.*)'):
        m = re.search(pat, h, re.S | re.I)
        if m and len(re.sub(r"<[^>]+>", "", m.group(1))) > 800:
            return m.group(1), "artikel"
    body = re.search(r"<body[^>]*>(.*)</body>", h, re.S | re.I)
    return (body.group(1) if body else h), "body"


def seite_sichern(url, zieldir, name=None):
    h = holen(url)
    if not h:
        return None
    t = re.search(r"<title>(.*?)</title>", h, re.S | re.I)
    titel = re.sub(r"\s+", " ", html.unescape(t.group(1))).strip() if t else url
    titel = re.split(r"\s[-|–]\s", titel)[0].strip() if len(titel) > 70 else titel
    inhalt, art = hauptinhalt(h, url)
    inhalt = saeubern(inhalt)
    inhalt = re.sub(r'(href|src)="(?!https?:|data:)([^"]+)"', lambda m: f'{m.group(1)}="{urllib.parse.urljoin(url, m.group(2))}"', inhalt)
    ziel = Path(zieldir) / f"{name or dateiname(titel)}.pdf"
    seiten, n_img = html_zu_pdf(titel, url, inhalt, ziel, url)
    print(f"  {art:7s} {seiten:3d} S. {n_img:2d} Bilder  {ziel.name}", flush=True)
    return titel, ziel.name, seiten


def wiki_sichern(api, titel, zieldir):
    q = urllib.parse.urlencode({"action": "parse", "page": titel, "prop": "text|displaytitle", "format": "json", "disableeditsection": 1})
    import json
    j = holen(f"{api}?{q}")
    if not j:
        return None
    try:
        d = json.loads(j)["parse"]
    except Exception:
        print(f"  kein Inhalt: {titel}", flush=True); return None
    inhalt = saeubern(d["text"]["*"])
    inhalt = re.sub(r"<div[^>]*class=\"[^\"]*(?:printfooter|catlinks|navbox|toc|mw-editsection)[^\"]*\"[^>]*>.*?</div>", " ", inhalt, flags=re.S)
    basis = api.rsplit("/", 1)[0] + "/"
    inhalt = re.sub(r'(href|src)="(?!https?:|data:)([^"]+)"', lambda m: f'{m.group(1)}="{urllib.parse.urljoin(basis, m.group(2))}"', inhalt)
    url = basis + "index.php/" + urllib.parse.quote(titel.replace(" ", "_"))
    ziel = Path(zieldir) / f"{dateiname(titel)}.pdf"
    seiten, n_img = html_zu_pdf(html.unescape(re.sub(r"<[^>]+>", "", d.get("displaytitle", titel))), url, inhalt, ziel, basis)
    print(f"  wiki    {seiten:3d} S. {n_img:2d} Bilder  {ziel.name}", flush=True)
    return titel, ziel.name, seiten


def wiki_alle_titel(api):
    import json
    titel, cont = [], {}
    while True:
        q = {"action": "query", "list": "allpages", "aplimit": 500, "format": "json", **cont}
        j = holen(f"{api}?{urllib.parse.urlencode(q)}")
        if not j:
            break
        d = json.loads(j)
        titel += [p["title"] for p in d["query"]["allpages"]]
        if "continue" not in d:
            break
        cont = d["continue"]
    return titel


def index_schreiben(zieldir, eintraege, kopf):
    p = Path(zieldir) / "INDEX.md"
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# {kopf}\n\nErstellt {HEUTE}. Privatkopien fuer den Eigengebrauch.\n\n| Titel | Datei | Seiten |\n|---|---|---|\n")
        for t, fn, s in eintraege:
            f.write(f"| {t} | {fn} | {s} |\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modus", choices=["wiki", "url", "liste"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--ziel", required=True)
    ap.add_argument("--api", default="https://wiki.germanscooterforum.de/api.php")
    ap.add_argument("--titel", nargs="*", default=[])
    ap.add_argument("--suche", default="", help="Regex auf Seitentitel (wiki)")
    ap.add_argument("--ausschluss", default="", help="Regex: passende Titel ueberspringen (wiki)")
    ap.add_argument("--kopf", default="Gesicherte Seiten")
    a = ap.parse_args()
    Path(a.ziel).mkdir(parents=True, exist_ok=True)
    ergebnisse = []
    if a.modus == "wiki":
        titel = list(a.titel)
        if a.suche:
            alle = wiki_alle_titel(a.api)
            titel += [t for t in alle if re.search(a.suche, t, re.I) and t not in titel
                      and not (a.ausschluss and re.search(a.ausschluss, t, re.I))]
            print(f"{len(alle)} Wiki-Seiten, {len(titel)} passend", flush=True)
        for t in titel:
            r = wiki_sichern(a.api, t, a.ziel)
            if r: ergebnisse.append(r)
    else:
        urls = []
        if a.modus == "liste":
            for datei in a.rest:
                for zeile in Path(datei).read_text(encoding="utf-8").splitlines():
                    zeile = zeile.strip()
                    if zeile and not zeile.startswith("#"):
                        urls.append([x.strip() for x in zeile.split("|", 1)])
        else:
            urls = [[u] for u in a.rest]
        for eintrag in urls:
            r = seite_sichern(eintrag[0], a.ziel, eintrag[1] if len(eintrag) > 1 else None)
            if r: ergebnisse.append(r)
    index_schreiben(a.ziel, ergebnisse, a.kopf)
    print(f"Fertig: {len(ergebnisse)} PDFs in {a.ziel}", flush=True)
