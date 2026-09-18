"""
Eine ZIM-Datei von einem ausdruecklich gewaehlten Spiegel fortsetzbar laden.

Der Lastverteiler download.kiwix.org weist mal schnelle, mal langsame Spiegel zu
(17.09.2026: ftp.nluug.nl 1 MB/s, mirrors.dotsrc.org 3,9 MB/s). Mit diesem Skript
laesst sich der Spiegel festlegen; die .part-Datei aus ddbox_fetch wird weiterverwendet,
weil alle Spiegel dieselben Bytes liefern. Pruefung, Manifest und library.xml macht
anschliessend wie gewohnt:

    python ddbox_fetch.py zim --root D:/DoomsdayBox --ark D:/AI-ARK --max-prio 3

Aufruf:
    python zim_direct.py https://mirrors.dotsrc.org/kiwix/zim/gutenberg/gutenberg_en_all_2025-11.zim
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ddbox_fetch import download, remote_size, log  # noqa: E402

ROOT = "D:/DoomsdayBox"


def main(url, versuche=60):
    dest = Path(ROOT) / "zim" / url.rsplit("/", 1)[-1]
    total = remote_size(url)
    log(ROOT, f"Direktlast {dest.name} von {url.split('/')[2]}: {total / 1e9:.1f} GB")
    for v in range(1, versuche + 1):
        got = download(url, dest, ROOT, retries=6)
        if got and got.stat().st_size == total:
            log(ROOT, f"{dest.name} komplett nach Versuch {v}: {got.stat().st_size / 1e9:.1f} GB")
            return 0
        log(ROOT, f"Versuch {v} unvollstaendig, weiter in 60 s")
        time.sleep(60)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
