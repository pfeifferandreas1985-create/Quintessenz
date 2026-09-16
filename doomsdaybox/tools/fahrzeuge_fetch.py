#!/usr/bin/env python3
"""
fahrzeuge_fetch.py - Phase F: Explosionszeichnungen und Teilelisten der eigenen Fahrzeuge spiegeln
und als einheitliche PDFs setzen (eine Tafel/Zeichnung je Seite, Teileliste darunter).

  python fahrzeuge_fetch.py minispares      # Mini: Katalog cat001-cat003 -> PDF je Kapitel + Teileliste CSV
  python fahrzeuge_fetch.py scootercenter   # Vespa V50 N (V5A1T) und Schwestermodelle -> PDF je Modell + CSV
  python fahrzeuge_fetch.py alle

Ziel: <root>/pdf/fahrzeuge/<fahrzeug>/explosionszeichnungen/  und  <root>/own/fahrzeuge/*.csv
Zwischenspeicher (HTML, Bilder, AJAX-Antworten): <stage>/fahrzeuge/_cache/  - erneuter Lauf laedt nichts doppelt.
Privatkopie fuer den Eigengebrauch; Quelle und Abrufdatum stehen auf jeder Seite.
"""
import argparse, base64, csv, html, io, re, time, urllib.request, urllib.error
from datetime import date
from pathlib import Path
import pymupdf
from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
      "Accept-Language": "de,en;q=0.8"}
HEUTE = date.today().isoformat()


# ---------------------------------------------------------------- Netz + Cache
class Netz:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.n_net = self.n_cache = 0
        self.takt = 1.0

    def _key(self, url):
        import hashlib
        kurz = re.sub(r"[^A-Za-z0-9._-]+", "_", url.split("://", 1)[-1])[:100]
        return f"{kurz}__{hashlib.sha1(url.encode()).hexdigest()[:16]}"

    def get(self, url, binary=False, retries=6, referer=None):
        f = self.cache / (self._key(url) + (".bin" if binary else ".html"))
        if f.exists() and f.stat().st_size > 0:
            self.n_cache += 1
            return f.read_bytes() if binary else f.read_text(encoding="utf-8", errors="replace")
        hdr = dict(UA)
        if referer:
            hdr["Referer"] = referer
            hdr["X-Requested-With"] = "XMLHttpRequest"
        for i in range(retries):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=90) as r:
                    data = r.read()
                f.write_bytes(data)
                self.n_net += 1
                time.sleep(self.takt)  # hoeflich bleiben
                return data if binary else data.decode("utf-8", "replace")
            except urllib.error.HTTPError as e:
                if e.code in (429, 403, 500, 502, 503, 504) and i < retries - 1:
                    # scooter-center antwortet bei Ueberlast mit 503 "calm down for at least 600s"
                    wartezeit = 630 if e.code in (429, 503) else min(60 * (2 ** i), 600)
                    print(f"    HTTP {e.code} - Server bremst, warte {wartezeit} s ({url[-60:]})", flush=True)
                    time.sleep(wartezeit)
                    continue
                print(f"    FEHLER HTTP {e.code}: {url}", flush=True)
                return None
            except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
                if i == retries - 1:
                    print(f"    FEHLER {type(e).__name__}: {url}", flush=True)
                    return None
                time.sleep(3 * (i + 1))


def text(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()


def titel_von(seite):
    m = re.search(r"<title>(.*?)</title>", seite or "", re.S)
    return text(m.group(1)) if m else ""


def bild_laden(netz, url):
    """Bild holen und als PNG-Bytes zurueckgeben (webp/gif -> PNG, damit pymupdf sie sicher einbettet)."""
    raw = netz.get(url, binary=True)
    if not raw:
        return None, (0, 0)
    try:
        im = Image.open(io.BytesIO(raw))
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        out = io.BytesIO()
        im.save(out, format="PNG")
        return out.getvalue(), im.size
    except Exception as e:
        print(f"    Bild unlesbar ({type(e).__name__}): {url}", flush=True)
        return None, (0, 0)


# ---------------------------------------------------------------- PDF-Setzer
class Pdf:
    """A4 quer: oben Zeichnung (max. 58 % Hoehe), darunter Teileliste; laeuft ueber, wenn die Liste laenger ist."""
    W, H, M = 842, 595, 28

    def __init__(self, titel, quelle):
        self.doc = pymupdf.open()
        self.titel = titel
        self.quelle = quelle

    def _kopf(self, page, ueberschrift, unter):
        page.insert_text((self.M, self.M + 6), ueberschrift[:110], fontsize=13, fontname="helv")
        page.insert_text((self.M, self.M + 22), unter[:170], fontsize=8, fontname="helv", color=(0.35, 0.35, 0.35))
        page.insert_text((self.M, self.H - 12),
                         f"{self.titel}  |  Quelle: {self.quelle}  |  abgerufen {HEUTE}  |  Privatkopie, nicht weitergeben",
                         fontsize=6.5, fontname="helv", color=(0.5, 0.5, 0.5))

    def tafel(self, ueberschrift, unter, png, size, zeilen, spalten=("Pos.", "Teilenummer", "Bezeichnung")):
        page = self.doc.new_page(width=self.W, height=self.H)
        self._kopf(page, ueberschrift, unter)
        y = self.M + 34
        if png and size[0] > 0:
            maxw, maxh = self.W - 2 * self.M, self.H * 0.58
            s = min(maxw / size[0], maxh / size[1])
            w, h = size[0] * s, size[1] * s
            page.insert_image(pymupdf.Rect(self.M, y, self.M + w, y + h), stream=png)
            y += h + 12
        self._tabelle(page, y, zeilen, spalten, ueberschrift, unter)

    def _tabelle(self, page, y, zeilen, spalten, ueberschrift, unter):
        cols = [self.M, self.M + 50, self.M + 190]

        def kopf(pg, yy):
            for c, s in zip(cols, spalten):
                pg.insert_text((c, yy), s, fontsize=8, fontname="hebo")
            return yy + 12

        y = kopf(page, y)
        for z in zeilen:
            if y > self.H - 30:
                page = self.doc.new_page(width=self.W, height=self.H)
                self._kopf(page, ueberschrift + " (Fortsetzung)", unter)
                y = kopf(page, self.M + 34)
            pos = str(z[0]) if len(z) > 0 else ""
            nr = str(z[1]) if len(z) > 1 else ""
            bez = str(z[2]) if len(z) > 2 else ""
            page.insert_text((cols[0], y), pos[:8], fontsize=7.5, fontname="helv")
            page.insert_text((cols[1], y), nr[:22], fontsize=7.5, fontname="helv")
            page.insert_text((cols[2], y), bez[:125], fontsize=7.5, fontname="helv")
            y += 10.5

    def speichern(self, pfad):
        Path(pfad).parent.mkdir(parents=True, exist_ok=True)
        self.doc.set_metadata({"title": self.titel, "author": self.quelle,
                               "subject": "Explosionszeichnungen, Privatkopie", "creationDate": pymupdf.get_pdf_now()})
        self.doc.save(str(pfad), garbage=3, deflate=True)
        n = len(self.doc)
        self.doc.close()
        return n


def dateiname(s):
    s = html.unescape(s)
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)
    s = re.sub(r"\s+", "-", s.strip())
    return re.sub(r"-{2,}", "-", s)[:80].strip("-")


# ---------------------------------------------------------------- Minispares (Mini MPi)
MS = "https://www.minispares.com/catalogues/catalogue/"
MS_KATALOGE = {"cat001": "Mechanical-Parts", "cat002": "Mechanical-Parts-2", "cat003": "Bodywork"}


def minispares(root, stage):
    netz = Netz(Path(stage) / "fahrzeuge" / "_cache" / "minispares")
    ziel = Path(root) / "pdf" / "fahrzeuge" / "mini" / "explosionszeichnungen"
    ziel.mkdir(parents=True, exist_ok=True)
    teile = []
    n_pdf = 0
    for cat, catname in MS_KATALOGE.items():
        idx = netz.get(MS + cat + "/")
        if not idx:
            continue
        chaps = sorted(set(re.findall(r'catalogue/%s/chapter/(chap\d+)/' % cat, idx)))
        print(f"== {cat} ({catname}): {len(chaps)} Kapitel", flush=True)
        for chap in chaps:
            ch = netz.get(f"{MS}{cat}/chapter/{chap}/")
            if not ch:
                continue
            ktitel = titel_von(ch).split("/")[-1].strip()
            pages = sorted(set(int(x) for x in re.findall(r'chapter/%s/page/(\d+)/' % chap, ch)))
            if not pages:
                print(f"   {chap} {ktitel}: keine Seiten (Einleitung)", flush=True)
                continue
            pdf = Pdf(f"Mini Spares Katalog {catname} - {ktitel}", "minispares.com")
            n_tafeln = 0
            for pg in pages:
                url = f"{MS}{cat}/chapter/{chap}/page/{pg}/"
                p = netz.get(url)
                if not p:
                    continue
                stitel = titel_von(p).split("/")[-1].strip()
                img = re.search(r'class="c-akm2__map__image"\s+src="([^"]+)"', p)
                png, size = bild_laden(netz, img.group(1)) if img else (None, (0, 0))
                zeilen = []
                for it in re.findall(r'<li[^>]*js-akm2-list-item[^>]*>(.*?)</li>', p, re.S):
                    vals = [text(v) for v in re.findall(r'c-akm2__map__list__value[^"]*">(.*?)</div>', it, re.S)]
                    if len(vals) >= 3:
                        pos, name, sku = vals[0], vals[1], vals[2]
                        zeilen.append((pos, sku, name))
                        teile.append((cat, chap, pg, ktitel, stitel, pos, sku, name))
                hm = re.search(r'c-akm2__map__image"[^>]*/?>(?:\s*</div>){1,5}\s*<br\s*/?>\s*(.*?)</div>', p, re.S)
                hinweis = text(hm.group(1)) if hm else ""
                if not img and not zeilen:
                    # reine Textseite (Tabellen, Hinweise): Hauptinhalt zeilenweise als Liste ausgeben
                    m = re.search(r"<main[^>]*>(.*?)</main>", p, re.S) or re.search(r'class="[^"]*catalogue[^"]*"[^>]*>(.*)', p, re.S)
                    roh = m.group(1) if m else p
                    roh = re.sub(r"<(script|style|nav|footer|header|form)[^>]*>.*?</\1>", " ", roh, flags=re.S | re.I)
                    roh = re.sub(r"</(tr|p|li|h[1-6]|div)>", "\n", roh, flags=re.I)
                    roh = re.sub(r"</t[dh]>", " | ", roh, flags=re.I)
                    for ln in [text(x) for x in roh.split("\n")]:
                        if len(ln) > 2 and not re.search(r"^(Standard Product View|Categories|Site Links|Reference:)", ln):
                            zeilen.append(("", "", ln[:125]))
                    zeilen = zeilen[:400]
                pdf.tafel(f"{ktitel}  -  {stitel}",
                          f"Katalog {catname}, Kapitel {chap[-2:]}, Seite {pg}   {hinweis[:100]}", png, size, zeilen)
                n_tafeln += 1
            out = ziel / f"Mini-MPi_{catname}_{chap[-2:]}-{dateiname(ktitel)}_minispares.pdf"
            n = pdf.speichern(out)
            n_pdf += 1
            print(f"   {chap} {ktitel}: {n_tafeln} Tafeln, {n} Seiten -> {out.name}", flush=True)
    csvp = Path(root) / "own" / "fahrzeuge" / "minispares_teileliste.csv"
    csvp.parent.mkdir(parents=True, exist_ok=True)
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["katalog", "kapitel", "seite", "kapitel_titel", "tafel_titel", "pos", "teilenummer", "bezeichnung"])
        w.writerows(teile)
    print(f"Minispares fertig: {n_pdf} PDFs, {len(teile)} Teilepositionen -> {csvp.name}  "
          f"(Netz {netz.n_net}, Cache {netz.n_cache})", flush=True)


# ---------------------------------------------------------------- Scooter Center (Vespa V50 N / V5A1T-Familie)
SC = "https://www.scooter-center.com/explosionszeichnungen/"
SC_MODELLE = {  # Seite -> Kurzname fuer Dateinamen
    "c-4979": "Vespa-50-N-V5A1T",
    "c-4975": "Vespa-50-V5A1T-1963",
    "c-4977": "Vespa-50-L-V5A1T",
    "c-5007": "Vespa-50-S-V5A1T-1964",
    "c-5221": "Vespa-50-R-V5A1T-bis-752188",
    "c-5211": "Vespa-50-R-V5A1T-ab-752189",
    "c-5223": "Vespa-50-V5SA1T-bis-69601",
    "c-5209": "Vespa-50-S-V5SA1T-ab-69602",
}
PREIS = re.compile(r"\s\d{1,4}[,.]\d{2}\s*€")


_PRODUKTE = {}


def sc_produkt(netz, url_unterseite, pid):
    """Hotspot-Details per AJAX: (Artikelname, Produktlink). Je Produkt-ID nur einmal geladen."""
    if pid in _PRODUKTE:
        return _PRODUKTE[pid]
    pf = netz.cache / f"produkt_{pid}.html"
    if pf.exists() and pf.stat().st_size > 0:
        aj = pf.read_text(encoding="utf-8", errors="replace")
        netz.n_cache += 1
    else:
        action = base64.b64encode((url_unterseite + "?action=add_product").encode()).decode()
        aj = netz.get(f"https://www.scooter-center.com/ax_run.php?ax_action=expoint_cart&action_url={action}&p_id={pid}",
                      referer=url_unterseite)
        if aj:
            pf.write_text(aj, encoding="utf-8")
    if not aj:
        return "", ""
    m = re.search(r'href="(https://www\.scooter-center\.com/[^"]+/p-\d+\.html)"', aj)
    link = m.group(1) if m else ""
    body = re.sub(r"<script.*?</script>", " ", aj, flags=re.S)
    t = text(body)
    t = re.sub(r"^[×x]\s*", "", t)
    name = PREIS.split(t)[0].strip()[:150]
    _PRODUKTE[pid] = (name, link)
    return name, link


def scootercenter(root, stage, modelle=None, startpause=0, takt=3.0):
    if startpause:
        print(f"Startpause {startpause} s (Rate-Limit des Servers abwarten)", flush=True)
        time.sleep(startpause)
    netz = Netz(Path(stage) / "fahrzeuge" / "_cache" / "scootercenter")
    netz.takt = takt  # scooter-center sperrt bei > ~1 Abruf/s fuer 10 Minuten
    ziel = Path(root) / "pdf" / "fahrzeuge" / "vespa" / "explosionszeichnungen"
    ziel.mkdir(parents=True, exist_ok=True)
    teile = []
    for code, kurz in SC_MODELLE.items():
        if modelle and code not in modelle:
            continue
        p = netz.get(f"{SC}{code}.html")
        if not p:
            continue
        mtitel = titel_von(p).split("|")[0].strip()
        subs = re.findall(r'<a href="(https://www\.scooter-center\.com/[^"]+/%s_\d+\.html)" title="([^"]+)"' % code, p)
        subs = list(dict.fromkeys(subs))
        print(f"== {code} {mtitel}: {len(subs)} Baugruppen", flush=True)
        pdf = Pdf(f"Explosionszeichnungen {mtitel}", "scooter-center.com")
        n_tafeln = 0
        for url, btitel in subs:
            btitel = html.unescape(btitel)
            sp = netz.get(url)
            if not sp:
                continue
            m = re.search(r'<div class="explosion-bg">.*?<img src="([^"]+)"', sp, re.S)
            tafel_url = m.group(1) if m else None
            zeilen = []
            for hs in re.finditer(r'<div class="ihotspot"[^>]*data-popover-content="#(ex\d+)"[^>]*data-sort="(\d+)"', sp):
                pid, pos = hs.group(1), hs.group(2)
                name, link = sc_produkt(netz, url, pid)
                zeilen.append((str(int(pos)), pid.replace("ex", "p-"), name or link))
            zeilen.sort(key=lambda z: int(z[0]) if z[0].isdigit() else 999)
            png, size = bild_laden(netz, tafel_url) if tafel_url else (None, (0, 0))
            pdf.tafel(f"{mtitel}  -  {btitel}", f"Baugruppe: {btitel}   {url}", png, size, zeilen,
                      spalten=("Pos.", "Artikel", "Bezeichnung"))
            n_tafeln += 1
            for z in zeilen:
                teile.append((code, mtitel, btitel) + tuple(z))
            print(f"   {btitel}: {len(zeilen)} Positionen", flush=True)
        out = ziel / f"{kurz}_Explosionszeichnungen_scooter-center.pdf"
        n = pdf.speichern(out)
        print(f"   {n_tafeln} Tafeln, {n} Seiten -> {out.name}", flush=True)
    csvp = Path(root) / "own" / "fahrzeuge" / "scootercenter_teileliste.csv"
    csvp.parent.mkdir(parents=True, exist_ok=True)
    codes_neu = {t[0] for t in teile}
    alt = []
    if csvp.exists():  # Zeilen anderer Modelle aus frueheren Laeufen behalten
        with open(csvp, newline="", encoding="utf-8") as f:
            r = csv.reader(f, delimiter=";"); next(r, None)
            alt = [z for z in r if z and z[0] not in codes_neu]
    with open(csvp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["modell_code", "modell", "baugruppe", "pos", "artikel", "bezeichnung"])
        w.writerows(alt); w.writerows(teile)
    teile = alt + teile
    print(f"Scooter Center fertig: {len(teile)} Positionen -> {csvp.name}  (Netz {netz.n_net}, Cache {netz.n_cache})",
          flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle", choices=["minispares", "scootercenter", "alle"])
    ap.add_argument("--root", default="D:/DoomsdayBox")
    ap.add_argument("--stage", default="C:/stage")
    ap.add_argument("--modelle", default="", help="Scooter Center: nur diese Modellcodes, kommagetrennt (z.B. c-4979)")
    ap.add_argument("--startpause", type=int, default=0, help="Sekunden warten, bevor Scooter Center beginnt")
    ap.add_argument("--takt", type=float, default=3.0, help="Sekunden zwischen Abrufen bei Scooter Center")
    a = ap.parse_args()
    if a.quelle in ("minispares", "alle"):
        minispares(a.root, a.stage)
    if a.quelle in ("scootercenter", "alle"):
        scootercenter(a.root, a.stage, [m for m in a.modelle.split(",") if m], a.startpause, a.takt)
