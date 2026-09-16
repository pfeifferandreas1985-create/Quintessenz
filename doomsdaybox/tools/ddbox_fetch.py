#!/usr/bin/env python3
"""
ddbox_fetch.py - Beschaffung fuer D:\\DoomsdayBox nach UEBERGABE_Download-Agent.md
Laeuft mit Windows-Python (kein WSL noetig). Nur Standardbibliothek + externe Werkzeuge:
  hf.exe (huggingface_hub), pmtiles.exe, zimcheck.exe, kiwix-manage.exe, git  (liegen in AI-ARK/00_RUNTIME/tools/win)

Phasen:
  python ddbox_fetch.py zim      --max-prio 2                # Phase A  ZIM-Dateien (sequentiell, 1 Verbindung, Resume)
  python ddbox_fetch.py models   --max-prio 3                # Phase B  Modelle fuer den Pi (erst aus AI-ARK kopieren)
  python ddbox_fetch.py maps     --regions deutschland,dach  # Phase C  PMTiles, Assets, PBF, GraphHopper
  python ddbox_fetch.py software                             # Phase D  llama.cpp arm64, kiwix, Wheels, Pi OS, Meshtastic
  python ddbox_fetch.py verify   [--full]                    # alle MANIFEST.sha256 pruefen (+ zimcheck)

HDD-Regel (2,5" SMR): grosse Dateien mit EINER Verbindung sequentiell direkt ins Ziel.
Optional --stage C:/stage: erst auf SSD laden, dann verschieben.
Pfade immer im Windows-Stil (D:/...), nicht /d/... - Windows-Python kennt MSYS-Pfade nicht.
"""
import argparse, csv, ctypes, hashlib, json, os, re, shutil, subprocess, sys, time
import urllib.request, urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT_DEFAULT = "D:/DoomsdayBox"
ARK_DEFAULT = "D:/AI-ARK"
UA = {"User-Agent": "ai-ark-ddbox/1.0"}
CHUNK = 8 * 1024 * 1024


# ---------------------------------------------------------------- Hilfen
def log(root, msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    Path(root).mkdir(parents=True, exist_ok=True)
    with open(Path(root) / "fetch.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def logbuch(root, aktion, ergebnis):
    p = Path(root) / "LOGBUCH.md"
    if not p.exists():
        p.write_text("# LOGBUCH DoomsdayBox\n\n| Datum | Aktion | Ergebnis |\n|---|---|---|\n", encoding="utf-8")
    with open(p, "a", encoding="utf-8") as f:
        f.write(f"| {datetime.now():%Y-%m-%d %H:%M} | {aktion} | {ergebnis} |\n")


def filesystem(path):
    """Dateisystemname des Laufwerks (Windows), z.B. 'FAT32', 'exFAT', 'NTFS'."""
    drive = os.path.splitdrive(os.path.abspath(path))[0] + "\\"
    buf = ctypes.create_unicode_buffer(64)
    ok = ctypes.windll.kernel32.GetVolumeInformationW(drive, None, 0, None, None, None, buf, 64)
    return buf.value if ok else "?"


def guard_fs(path):
    fs = filesystem(path)
    if "FAT" in fs.upper() and "EXFAT" not in fs.upper():
        sys.exit(f"ABBRUCH: {path} liegt auf {fs} - 4-GB-Dateigrenze. Erst exFAT/NTFS formatieren.")
    return fs


def tool(name, ark):
    """Sucht ein Werkzeug: PATH, dann AI-ARK/00_RUNTIME/tools/win, fuer hf zusaetzlich den pip-Scripts-Ordner."""
    p = shutil.which(name) or shutil.which(name + ".exe")
    if p:
        return p
    cand = Path(ark) / "00_RUNTIME" / "tools" / "win" / (name + ".exe")
    if cand.exists():
        return str(cand)
    if name == "hf":
        for base in (os.environ.get("LOCALAPPDATA", ""), os.environ.get("APPDATA", "")):
            if not base:
                continue
            hits = list(Path(base).glob("Python/**/Scripts/hf.exe"))
            if hits:
                return str(hits[0])
    return None


def run_tool(cmd, root):
    """subprocess.run, das ein fehlendes Programm als 'nicht verfuegbar' (None) meldet statt abzustuerzen."""
    try:
        return subprocess.run(cmd, capture_output=True).returncode
    except FileNotFoundError:
        log(root, f"    Werkzeug nicht erreichbar: {cmd[0]} - Schritt uebersprungen")
        return None


def http_text(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def remote_size(url):
    """Content-Length ueber HEAD; faellt auf GET mit Range 0-0 zurueck (manche Spiegel moegen kein HEAD)."""
    for method, hdr in (("HEAD", dict(UA)), ("GET", dict(UA, Range="bytes=0-0"))):
        try:
            req = urllib.request.Request(url, method=method, headers=hdr)
            with urllib.request.urlopen(req, timeout=60) as r:
                cr = r.headers.get("Content-Range")
                if cr and "/" in cr:
                    return int(cr.rsplit("/", 1)[1])
                return int(r.headers.get("Content-Length", 0) or 0)
        except Exception:
            continue
    return 0


def download(url, dest, root, stage=None, retries=6):
    """Sequentieller Download mit Resume (Range). Eine Verbindung. Gibt Zielpfad oder None."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = (Path(stage) / dest.name if stage else dest).with_suffix(dest.suffix + ".part")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    total = remote_size(url)
    attempt = 0
    while attempt < retries:
        attempt += 1
        have = tmp.stat().st_size if tmp.exists() else 0
        if total and have >= total:
            break
        hdr = dict(UA)
        if have:
            hdr["Range"] = f"bytes={have}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=120) as r:
                mode = "ab"
                if have and r.status != 206:
                    mode = "wb"  # Server kann kein Resume -> von vorn
                    have = 0
                with open(tmp, mode) as f:
                    t0 = time.time(); got = 0; last = t0
                    while True:
                        b = r.read(CHUNK)
                        if not b:
                            break
                        f.write(b); got += len(b)
                        if time.time() - last > 30:
                            done = have + got
                            rate = got / (time.time() - t0) / 1e6
                            pct = f"{done / total * 100:5.1f}%" if total else "?"
                            log(root, f"    {dest.name}: {done / 1e9:.2f} GB {pct}  {rate:.1f} MB/s")
                            last = time.time()
            if not total or tmp.stat().st_size >= total:
                break
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            log(root, f"    Unterbrechung ({type(e).__name__}), Versuch {attempt}/{retries}, warte 30 s")
            time.sleep(30)
    else:
        log(root, f"    AUFGEGEBEN: {dest.name}")
        return None
    if total and tmp.stat().st_size != total:
        log(root, f"    GROESSE FALSCH: {tmp.stat().st_size} != {total}")
        return None
    if stage:
        log(root, f"    verschiebe nach {dest.parent}")
        shutil.move(str(tmp), str(dest))  # laufwerksuebergreifend = sequentielle Kopie + Loeschen
    else:
        tmp.rename(dest)
    return dest


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def manifest_add(folder, fname, digest):
    m = Path(folder) / "MANIFEST.sha256"
    lines = m.read_text(encoding="utf-8").splitlines() if m.exists() else []
    lines = [l for l in lines if not l.endswith("  " + fname)]
    lines.append(f"{digest}  {fname}")
    m.write_text("\n".join(lines) + "\n", encoding="utf-8")


def manifest_has(folder, fname):
    m = Path(folder) / "MANIFEST.sha256"
    return m.exists() and any(l.endswith("  " + fname) for l in m.read_text(encoding="utf-8").splitlines())


# ---------------------------------------------------------------- Phase A: ZIM
CATALOG = "https://library.kiwix.org/catalog/v2/entries?name={}&count=1"
MIRROR = "https://download.kiwix.org/zim/{}/"
CATS = ["wikipedia", "wikibooks", "wiktionary", "wikiversity", "stack_exchange", "ifixit", "gutenberg",
        "wikihow", "devdocs", "other"]
# Praefixe, die im Katalog anders heissen als im Manifest (Ergebnis der Stamm-Suche am 15.09.2026)
ALIAS = {
    "wiktionary_de_all_maxi": "wiktionary_de_all",           # es gibt nur die nopic-Ausgabe
    "lowtechmagazine.com_en_all": "solar.lowtechmagazine.com_mul_all",
}


def resolve_zim(prefix, category):
    prefix = ALIAS.get(prefix, prefix)
    try:
        root = ET.fromstring(http_text(CATALOG.format(prefix)))
        for l in root.iter():
            if l.tag.endswith("link") and l.get("type") == "application/x-zim":
                href = l.get("href", "").replace(".meta4", "")
                if href.endswith(".zim"):
                    return href
    except Exception:
        pass
    for c in dict.fromkeys([category] + CATS):
        try:
            html = http_text(MIRROR.format(c))
        except Exception:
            continue
        m = sorted(set(re.findall(r'href="(%s_\d{4}-\d{2}\.zim)"' % re.escape(prefix), html)))
        if m:
            return MIRROR.format(c) + m[-1]
    return None


def phase_zim(a):
    dest = Path(a.root) / "zim"
    dest.mkdir(parents=True, exist_ok=True)
    fs = guard_fs(dest)
    log(a.root, f"Phase A ZIM  Ziel={dest} ({fs})  max. Prio={a.max_prio}  stage={a.stage or '-'}")
    zimcheck = tool("zimcheck", a.ark)
    kmanage = tool("kiwix-manage", a.ark)
    manifest = Path(a.root) / "tools" / "zim_manifest.tsv"
    rows = list(csv.DictReader(open(manifest, encoding="utf-8"), delimiter="\t"))
    skip = set(x.strip() for x in a.skip.split(",") if x.strip())
    n_ok = n_fail = 0
    nf = []
    gb = 0.0
    for r in rows:
        prefix, prio = r["prefix"], int(r["prio"])
        if prio > a.max_prio or prefix in skip:
            continue
        url = resolve_zim(prefix, r["category"])
        if not url:
            log(a.root, f"NICHT GEFUNDEN: {prefix} ({r['note']})")
            nf.append(prefix)
            continue
        fname = url.rsplit("/", 1)[-1]
        target = dest / fname
        stem = ALIAS.get(prefix, prefix)
        older = sorted(dest.glob(stem + "_????-??.zim"))
        if target.exists() and manifest_has(dest, fname):
            log(a.root, f"aktuell: {fname}")
            continue
        size = remote_size(url)
        if target.exists() and size and target.stat().st_size == size:
            log(a.root, f"vollstaendig vorhanden, nur Pruefung: {fname}")
            got = target
        else:
            log(a.root, f"lade P{prio} {size / 1e9:.1f} GB: {fname} - {r['note']}")
            got = download(url, target, a.root, a.stage)
        if not got:
            n_fail += 1
            continue
        digest = sha256(got)
        ok = True
        try:
            want = http_text(url + ".sha256").split()[0].lower()
            ok = (want == digest)
            log(a.root, f"    SHA-256 {'OK' if ok else 'FEHLER'} (offiziell)")
        except Exception:
            log(a.root, "    keine offizielle .sha256")
        if ok and zimcheck:
            rc = run_tool([zimcheck, "-C", str(got)], a.root)
            if rc is not None:
                ok = (rc == 0)
                log(a.root, f"    zimcheck {'OK' if ok else 'FEHLER'}")
        if not ok:
            got.rename(got.with_suffix(".zim.BAD"))
            n_fail += 1
            continue
        manifest_add(dest, fname, digest)
        n_ok += 1
        gb += got.stat().st_size / 1e9
        for o in older:
            if o != got and o.exists():
                log(a.root, f"    entferne alte Ausgabe {o.name}")
                o.unlink()
    if kmanage:
        lib = dest / "library.xml"
        lib.unlink(missing_ok=True)
        for z in sorted(dest.glob("*.zim")):
            if run_tool([kmanage, str(lib), "add", str(z)], a.root) is None:
                break
        log(a.root, f"library.xml: {len(list(dest.glob('*.zim')))} ZIM-Dateien")
    logbuch(a.root, f"Phase A ZIM bis Prio {a.max_prio}",
            f"{n_ok} neu ({gb:.1f} GB), {n_fail} fehlgeschlagen, nicht gefunden: {', '.join(nf) or '-'}")


# ---------------------------------------------------------------- Phase B: Modelle
MODELS = [  # prio, repo, include-Muster, Zweck
    (1, "unsloth/Qwen3.5-9B-GGUF", "*Q4_K_M*.gguf", "Hauptmodell Text"),
    (1, "unsloth/gemma-4-E4B-it-GGUF", "*Q4_K_M*.gguf", "Bild+Audio-Modell"),
    (1, "unsloth/gemma-4-E4B-it-GGUF", "mmproj*", "Projektor E4B"),
    (1, "Qwen/Qwen3-Embedding-0.6B-GGUF", "*Q8_0*.gguf", "Embedding RAG"),
    (2, "unsloth/gemma-4-E2B-it-GGUF", "*Q4_K_M*.gguf", "Notmodell"),
    (2, "unsloth/gemma-4-E2B-it-GGUF", "mmproj*", "Projektor E2B"),
    (2, "unsloth/Qwen3.5-0.8B-GGUF", "*Q8_0*.gguf", "Kleinstmodell"),
    (2, "nomic-ai/nomic-embed-text-v1.5-GGUF", "*Q8_0*.gguf", "Embedding-Notnagel"),
    (2, "ggerganov/whisper.cpp", "ggml-medium.bin", "Sprache->Text"),
    (2, "ggerganov/whisper.cpp", "ggml-small.bin", "Sprache->Text schnell"),
    (3, "unsloth/granite-4.0-h-1b-GGUF", "*Q8_0*.gguf", "Kleinstmodell, dokumentierte Daten"),
    (3, "rhasspy/piper-voices", "de/de_DE/thorsten/medium/*", "Text->Sprache DE"),
]


def phase_models(a):
    dest = Path(a.root) / "models"
    dest.mkdir(parents=True, exist_ok=True)
    guard_fs(dest)
    hf = tool("hf", a.ark)
    ark_models = Path(a.ark) / "01_MODELS"
    log(a.root, f"Phase B Modelle  Ziel={dest}  hf={hf}  AI-ARK={ark_models}")
    n_copy = n_dl = n_fail = 0
    for prio, repo, pattern, purpose in MODELS:
        if prio > a.max_prio:
            continue
        name = repo.split("/")[-1]
        sub = dest / name
        pat = pattern.split("/")[-1]
        if sub.exists() and any(sub.rglob(pat)):
            log(a.root, f"vorhanden: {repo} {pattern}")
            continue
        hits = []
        if ark_models.exists():
            hits = [p for p in ark_models.rglob(pat)
                    if name in str(p) and ".cache" not in p.parts and not p.name.endswith(".incomplete")]
        if hits:
            sub.mkdir(parents=True, exist_ok=True)
            for h in hits:
                log(a.root, f"kopiere aus AI-ARK: {h.name} ({h.stat().st_size / 1e9:.1f} GB)")
                shutil.copyfile(h, sub / h.name)
            n_copy += 1
            continue
        if not hf:
            log(a.root, f"hf fehlt - ueberspringe {repo}")
            n_fail += 1
            continue
        log(a.root, f"lade P{prio}: {repo} {pattern} - {purpose}")
        rc = subprocess.run([hf, "download", repo, "--include", pattern, "--local-dir", str(sub),
                             "--max-workers", "2"]).returncode
        if rc == 0:
            n_dl += 1
            shutil.rmtree(sub / ".cache", ignore_errors=True)
        else:
            n_fail += 1
            log(a.root, f"    FEHLER {repo} (Lizenz nicht akzeptiert? Muster ohne Treffer?)")
    lines = []
    for f in sorted(dest.rglob("*")):
        if f.is_file() and f.suffix in (".gguf", ".bin", ".onnx", ".json") and f.name != "MANIFEST.sha256":
            lines.append(f"{sha256(f)}  {f.relative_to(dest).as_posix()}")
    (dest / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    logbuch(a.root, f"Phase B Modelle bis Prio {a.max_prio}",
            f"{n_copy} aus AI-ARK kopiert, {n_dl} geladen, {n_fail} fehlgeschlagen")


# ---------------------------------------------------------------- Phase C: Karten
REGIONS = {"europa": "-25,34,45,72", "dach": "5.8,45.8,17.2,55.1", "deutschland": "5.8,47.2,15.1,55.1"}


def phase_maps(a):
    dest = Path(a.root) / "maps"
    (dest / "assets").mkdir(parents=True, exist_ok=True)
    (dest / "routing").mkdir(exist_ok=True)
    guard_fs(dest)
    pm = tool("pmtiles", a.ark)
    log(a.root, f"Phase C Karten  Ziel={dest}  pmtiles={pm}")
    offen = []
    if pm:
        # builds.json existiert nicht mehr (Stand 09/2026). Tagesbuilds heissen YYYYMMDD.pmtiles -
        # die letzten 10 Tage abklopfen, den juengsten vorhandenen nehmen.
        from datetime import timedelta
        build = None
        for i in range(10):
            cand = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d") + ".pmtiles"
            if remote_size(f"https://build.protomaps.com/{cand}") > 1e9:
                build = cand
                break
        if not build:
            sys.exit("Kein Protomaps-Tagesbuild der letzten 10 Tage erreichbar")
        log(a.root, f"Protomaps-Build: {build}")
        for reg in a.regions.split(","):
            reg = reg.strip()
            out = dest / f"{reg}.pmtiles"
            if out.exists():
                log(a.root, f"vorhanden: {out.name}")
                continue
            log(a.root, f"pmtiles extract {reg} bbox={REGIONS[reg]}")
            plog = dest / f"pmtiles_{reg}.log"
            # HTTP/2 zu build.protomaps.com bricht bei langen Extrakten mit PROTOCOL_ERROR ab (kein Resume moeglich).
            # Go-Binary per GODEBUG auf HTTP/1.1 zwingen.
            env = dict(os.environ, GODEBUG="http2client=0")
            with open(plog, "w", encoding="utf-8", errors="replace") as lf:
                rc = subprocess.run([pm, "extract", f"https://build.protomaps.com/{build}", str(out),
                                     f"--bbox={REGIONS[reg]}", "--download-threads=4"],
                                    stdout=lf, stderr=subprocess.STDOUT, env=env).returncode
            tail = plog.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-3:]
            log(a.root, f"    pmtiles rc={rc}: " + " | ".join(t.strip() for t in tail))
            if rc != 0:
                offen.append(f"pmtiles {reg} (rc={rc}, siehe {plog.name})")
                if out.exists():
                    out.rename(out.with_suffix(".pmtiles.FAILED"))   # zur Untersuchung behalten, nicht loeschen
    else:
        offen.append("pmtiles.exe fehlt")
    if not (dest / "assets" / "basemaps-assets").exists():
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/protomaps/basemaps-assets",
                        str(dest / "assets" / "basemaps-assets")])
    for name, url in (("maplibre-gl.js", "https://unpkg.com/maplibre-gl@5/dist/maplibre-gl.js"),
                      ("maplibre-gl.css", "https://unpkg.com/maplibre-gl@5/dist/maplibre-gl.css"),
                      ("pmtiles.js", "https://unpkg.com/pmtiles@4/dist/pmtiles.js")):
        if not (dest / "assets" / name).exists():
            download(url, dest / "assets" / name, a.root)
    pbf = dest / "germany-latest.osm.pbf"
    if not pbf.exists():
        log(a.root, "lade Geofabrik germany-latest.osm.pbf")
        if download("https://download.geofabrik.de/europe/germany-latest.osm.pbf", pbf, a.root, a.stage):
            want = http_text("https://download.geofabrik.de/europe/germany-latest.osm.pbf.md5").split()[0]
            h = hashlib.md5()
            with open(pbf, "rb") as f:
                for b in iter(lambda: f.read(CHUNK), b""):
                    h.update(b)
            log(a.root, f"    MD5 {'OK' if h.hexdigest() == want else 'FEHLER'}")
    ghv = "10.0"
    jar = dest / "routing" / f"graphhopper-web-{ghv}.jar"
    if not jar.exists():
        download(f"https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/{ghv}/graphhopper-web-{ghv}.jar",
                 jar, a.root)
        download(f"https://raw.githubusercontent.com/graphhopper/graphhopper/{ghv}/config-example.yml",
                 dest / "routing" / "config.yml", a.root)
    poi = dest / "poi.sqlite"
    if pbf.exists() and not poi.exists():
        try:
            import osmium, sqlite3
            log(a.root, "baue POI-SQLite aus germany-latest.osm.pbf (pyosmium, dauert 20-60 min)")
            KEYS = {"amenity": {"drinking_water", "pharmacy", "hospital", "clinic", "doctors", "fuel", "fire_station",
                                "police", "shelter"},
                    "shop": {"hardware", "doityourself", "electronics", "agrarian", "farm"},
                    "craft": {"electrician", "metal_construction", "blacksmith"},
                    "man_made": {"water_well", "water_tower"}, "natural": {"spring"}}
            con = sqlite3.connect(str(poi))
            con.execute("CREATE TABLE poi(id INTEGER PRIMARY KEY, lat REAL, lon REAL, kind TEXT, name TEXT, tags TEXT)")

            class H(osmium.SimpleHandler):
                def node(self, n):
                    t = dict(n.tags)
                    for k, vals in KEYS.items():
                        if t.get(k) in vals:
                            con.execute("INSERT OR IGNORE INTO poi VALUES(?,?,?,?,?,?)",
                                        (n.id, n.location.lat, n.location.lon, t[k], t.get("name"), json.dumps(t, ensure_ascii=False)))
                            break
            H().apply_file(str(pbf))
            con.execute("CREATE INDEX idx_kind ON poi(kind)"); con.execute("CREATE INDEX idx_pos ON poi(lat, lon)")
            con.commit()
            log(a.root, f"    POI: {con.execute('select count(*) from poi').fetchone()[0]} Eintraege")
            con.close()
        except ImportError:
            offen.append("POI-SQLite (pip install osmium, dann maps erneut)")
        except Exception as e:
            offen.append(f"POI-SQLite ({type(e).__name__})"); poi.unlink(missing_ok=True)
    offen.append("GraphHopper-Import (java -Xmx8g -jar ... import config.yml, 1-2 h)")
    lines = [f"{sha256(f)}  {f.name}" for f in sorted(dest.glob("*.pmtiles")) + sorted(dest.glob("*.pbf"))]
    (dest / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    logbuch(a.root, f"Phase C Karten ({a.regions})", f"offen: {'; '.join(offen)}")


# ---------------------------------------------------------------- Phase D: Software Pi
WHEELS = ("numpy sqlite-vec llama-cpp-python libzim pymupdf paho-mqtt pyserial pymodbus "
          "fastapi uvicorn huggingface_hub osmium")


def phase_software(a):
    dest = Path(a.root) / "src"
    dest.mkdir(parents=True, exist_ok=True)
    guard_fs(dest)
    rt = Path(a.ark) / "00_RUNTIME"
    log(a.root, f"Phase D Software Pi  Ziel={dest}")
    offen = []
    for pat in ("llamacpp/llama-*-bin-ubuntu-arm64.tar.gz", "ui/kiwix/kiwix-tools_linux-aarch64-*.tar.gz",
                "tools/zim-tools_linux-aarch64-*.tar.gz", "tools/go-pmtiles_*_Linux_arm64.tar.gz"):
        for src in rt.glob(pat):
            if not (dest / src.name).exists():
                log(a.root, f"kopiere {src.name}")
                shutil.copyfile(src, dest / src.name)
    img = dest / "raspios"
    img.mkdir(exist_ok=True)
    if not any(img.glob("*.img.xz")):
        try:
            req = urllib.request.Request("https://downloads.raspberrypi.com/raspios_lite_arm64_latest",
                                         method="HEAD", headers=UA)
            final = urllib.request.urlopen(req, timeout=60).geturl()
            fname = final.rsplit("/", 1)[-1]
            log(a.root, f"Pi OS Lite: {fname}")
            if download(final, img / fname, a.root, a.stage):
                try:
                    (img / (fname + ".sha256")).write_text(http_text(final + ".sha256"), encoding="utf-8")
                except Exception:
                    offen.append("Pi OS .sha256")
        except Exception as e:
            offen.append(f"Pi OS Image ({type(e).__name__})")
    wh = dest / "wheels"
    wh.mkdir(exist_ok=True)
    if not any(wh.glob("*.whl")):
        log(a.root, "pip download aarch64-Wheels (je Paket; ohne Binaerpaket -> Quellpaket)")
        sdist = []
        for pkg in WHEELS.split():
            base = [sys.executable, "-m", "pip", "download", "-q", "--no-deps", "-d", str(wh), pkg]
            rc = subprocess.run(base + ["--platform", "manylinux2014_aarch64", "--only-binary=:all:",
                                        "--python-version", "3.12"]).returncode
            if rc != 0:
                # kein fertiges aarch64-Wheel (z.B. llama-cpp-python): Quellpaket direkt von PyPI holen
                # (nicht ueber pip - das wuerde das Paket lokal zu bauen versuchen)
                try:
                    meta = json.loads(http_text(f"https://pypi.org/pypi/{pkg}/json"))
                    src = next(u for u in meta["urls"] if u["packagetype"] == "sdist")
                    if download(src["url"], wh / src["filename"], a.root):
                        sdist.append(pkg)
                    else:
                        offen.append(f"pip {pkg} (Quellpaket-Download fehlgeschlagen)")
                except Exception as e:
                    offen.append(f"pip {pkg} (weder Wheel noch Quelle: {type(e).__name__})")
        n_whl = len(list(wh.glob("*.whl"))); n_src = len(list(wh.glob("*.tar.gz")))
        log(a.root, f"    {n_whl} Wheels, {n_src} Quellpakete ({', '.join(sdist) or '-'})")
        if sdist:
            offen.append(f"Quellpakete auf dem Pi bauen: {', '.join(sdist)} (apt install build-essential cmake)")
        # Abhaengigkeiten der Wheels (numpy etc. sind eigenstaendig; fastapi/uvicorn ziehen weitere)
        subprocess.run([sys.executable, "-m", "pip", "download", "-q", "-d", str(wh), "--platform", "manylinux2014_aarch64",
                        "--only-binary=:all:", "--python-version", "3.12", "fastapi", "uvicorn", "huggingface_hub", "pymupdf"])
    mesh = dest / "meshtastic"
    mesh.mkdir(exist_ok=True)
    if not any(mesh.glob("*.zip")):
        try:
            rel = json.loads(http_text("https://api.github.com/repos/meshtastic/firmware/releases/latest"))
            for asset in rel["assets"]:
                if re.match(r"firmware-(esp32|esp32s3|nrf52840|rp2040)-.*\.zip$", asset["name"]):
                    download(asset["browser_download_url"], mesh / asset["name"], a.root)
        except Exception as e:
            offen.append(f"Meshtastic ({type(e).__name__})")
    srcs = dest / "sources"
    srcs.mkdir(exist_ok=True)
    for repo in ("ggml-org/llama.cpp", "kiwix/kiwix-tools", "openzim/libzim", "asg017/sqlite-vec",
                 "maplibre/maplibre-gl-js", "protomaps/go-pmtiles"):
        out = srcs / (repo.replace("/", "_") + ".tar.gz")
        if not out.exists():
            download(f"https://api.github.com/repos/{repo}/tarball", out, a.root)
    offen.append("Debian arm64 .deb (kiwix-tools, zim-tools, par2, aria2, hostapd, dnsmasq, openjdk-17, "
                 "ocrmypdf, tesseract-ocr-deu) - braucht arm64-System")
    lines = [f"{sha256(f)}  {f.relative_to(dest).as_posix()}"
             for f in sorted(dest.rglob("*")) if f.is_file() and f.name != "MANIFEST.sha256"]
    (dest / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    logbuch(a.root, "Phase D Software Pi", f"offen: {'; '.join(offen)}")


# ---------------------------------------------------------------- verify
def phase_verify(a):
    root = Path(a.root)
    bad = n = 0
    zimcheck = tool("zimcheck", a.ark)
    for m in root.rglob("MANIFEST.sha256"):
        for line in m.read_text(encoding="utf-8").splitlines():
            if "  " not in line:
                continue
            digest, rel = line.split("  ", 1)
            f = m.parent / rel
            n += 1
            if not f.exists():
                print(f"FEHLT   {f}")
                bad += 1
                continue
            if sha256(f) != digest:
                print(f"DEFEKT  {f}")
                bad += 1
    if zimcheck and a.full:
        for z in (root / "zim").glob("*.zim"):
            if run_tool([zimcheck, "-C", str(z)], a.root) not in (0, None):
                print(f"ZIM DEFEKT {z}")
                bad += 1
    print(f"{n} Dateien geprueft, {bad} Probleme")
    logbuch(a.root, "verify", f"{n} geprueft, {bad} Probleme")
    sys.exit(1 if bad else 0)


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phase", choices=["zim", "models", "maps", "software", "verify"])
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--ark", default=ARK_DEFAULT)
    ap.add_argument("--max-prio", type=int, default=3)
    ap.add_argument("--stage", default=None)
    ap.add_argument("--skip", default="", help="ZIM-Praefixe, kommagetrennt, die nicht geladen werden")
    ap.add_argument("--regions", default="deutschland,dach,europa")
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    {"zim": phase_zim, "models": phase_models, "maps": phase_maps,
     "software": phase_software, "verify": phase_verify}[a.phase](a)
