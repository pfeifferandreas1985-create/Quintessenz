#!/usr/bin/env bash
# maps.sh – Offline-Karten für das Voll-Szenario: PMTiles Europa + Deutschland, Basemap-Assets,
# Geofabrik-PBF Deutschland, GraphHopper-Routing-Graph.
# Aufruf: ./maps.sh [ZIEL]            z. B. ./maps.sh /srv/box/maps
# Voraussetzungen: pmtiles-CLI (github.com/protomaps/go-pmtiles), curl, java 17+ (nur Routing), git
# Lizenz: OpenStreetMap-Daten ODbL, Protomaps-Basemap BSD. Namensnennung im Viewer einblenden.

set -euo pipefail
DEST="${1:-/srv/box/maps}"
mkdir -p "$DEST/assets" "$DEST/routing"
command -v pmtiles >/dev/null 2>&1 || { echo "pmtiles-CLI fehlt (go-pmtiles Release herunterladen)"; exit 1; }

# 1) Neuesten Protomaps-Planet-Build finden (tägliche Builds, Dateiname YYYYMMDD.pmtiles)
BUILD="$(curl -fsSL https://build.protomaps.com/builds.json | python3 -c 'import sys,json; b=[x["key"] for x in json.load(sys.stdin) if x["key"].endswith(".pmtiles")]; print(sorted(b)[-1])')"
echo "Planet-Build: $BUILD"

# 2) Regionale Extrakte (Bounding-Box: west,süd,ost,nord)
#    Europa ohne Russland-Ost, ca. 30 GB      Deutschland ca. 4 GB      DACH ca. 6 GB
[ -f "$DEST/europa.pmtiles" ]      || pmtiles extract "https://build.protomaps.com/$BUILD" "$DEST/europa.pmtiles"      --bbox=-25,34,45,72
[ -f "$DEST/deutschland.pmtiles" ] || pmtiles extract "https://build.protomaps.com/$BUILD" "$DEST/deutschland.pmtiles" --bbox=5.8,47.2,15.1,55.1
[ -f "$DEST/dach.pmtiles" ]        || pmtiles extract "https://build.protomaps.com/$BUILD" "$DEST/dach.pmtiles"        --bbox=5.8,45.8,17.2,55.1

# 3) Basemap-Assets (Schriften, Sprites) und Style für MapLibre – ohne diese rendert nichts offline
if [ ! -d "$DEST/assets/basemaps-assets" ]; then
  git clone --depth 1 https://github.com/protomaps/basemaps-assets "$DEST/assets/basemaps-assets"
fi
# MapLibre GL JS lokal ablegen (Version ggf. anpassen)
MLV="5.6.0"
curl -fsSL -o "$DEST/assets/maplibre-gl.js"  "https://unpkg.com/maplibre-gl@$MLV/dist/maplibre-gl.js"
curl -fsSL -o "$DEST/assets/maplibre-gl.css" "https://unpkg.com/maplibre-gl@$MLV/dist/maplibre-gl.css"
curl -fsSL -o "$DEST/assets/pmtiles.js"      "https://unpkg.com/pmtiles@4/dist/pmtiles.js"
# Basemap-Style-Generator (npm-Paket @protomaps/basemaps) erzeugt style.json; Alternative: fertige style.json
# aus docs.protomaps.com/basemaps/maplibre kopieren und "url" auf "pmtiles://../deutschland.pmtiles" setzen.

# 4) OSM-Rohdaten Deutschland (für Routing, POI-Extrakt, Nominatim)
[ -f "$DEST/germany-latest.osm.pbf" ] || curl -fL -o "$DEST/germany-latest.osm.pbf" https://download.geofabrik.de/europe/germany-latest.osm.pbf
curl -fsSL https://download.geofabrik.de/europe/germany-latest.osm.pbf.md5 | sed "s#germany-latest.osm.pbf#$DEST/germany-latest.osm.pbf#" | md5sum -c -

# 5) POI-Datenbank (SQLite) für das LLM: Wasser, Apotheken, Krankenhäuser, Tankstellen, Baumärkte, Werkstätten
#    benötigt osmium-tool und python3 mit pyosmium  (pip install osmium)
if command -v osmium >/dev/null 2>&1; then
  osmium tags-filter "$DEST/germany-latest.osm.pbf" \
    n/amenity=drinking_water,pharmacy,hospital,clinic,doctors,fuel,fire_station,police,shelter \
    n/shop=hardware,doityourself,electronics,agrarian,farm \
    n/craft=electrician,metal_construction,blacksmith \
    n/man_made=water_well,water_tower n/natural=spring \
    -o "$DEST/poi.osm.pbf" --overwrite
  python3 - "$DEST/poi.osm.pbf" "$DEST/poi.sqlite" <<'EOF'
import sys, sqlite3, osmium
src, dst = sys.argv[1], sys.argv[2]
con = sqlite3.connect(dst)
con.execute("DROP TABLE IF EXISTS poi")
con.execute("CREATE TABLE poi(id INTEGER PRIMARY KEY, lat REAL, lon REAL, kind TEXT, name TEXT, tags TEXT)")
class H(osmium.SimpleHandler):
    def node(self, n):
        t = dict(n.tags)
        kind = t.get("amenity") or t.get("shop") or t.get("craft") or t.get("man_made") or t.get("natural")
        con.execute("INSERT INTO poi VALUES(?,?,?,?,?,?)", (n.id, n.location.lat, n.location.lon, kind, t.get("name"), str(t)))
H().apply_file(src)
con.execute("CREATE INDEX idx_kind ON poi(kind)"); con.execute("CREATE INDEX idx_pos ON poi(lat,lon)")
con.commit(); print("POI:", con.execute("select count(*) from poi").fetchone()[0])
EOF
fi

# 6) Routing-Graph (GraphHopper, Java) – Import dauert auf einem PC 1–2 h, ca. 3 GB
GHV="10.0"
if [ ! -f "$DEST/routing/graphhopper-web-$GHV.jar" ]; then
  curl -fL -o "$DEST/routing/graphhopper-web-$GHV.jar" "https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/$GHV/graphhopper-web-$GHV.jar"
  curl -fL -o "$DEST/routing/config.yml" "https://raw.githubusercontent.com/graphhopper/graphhopper/$GHV/config-example.yml"
  sed -i "s#datareader.file:.*#datareader.file: $DEST/germany-latest.osm.pbf#; s#graph.location:.*#graph.location: $DEST/routing/graph-cache#" "$DEST/routing/config.yml"
fi
echo "Routing-Import starten mit:  java -Xmx8g -jar $DEST/routing/graphhopper-web-$GHV.jar import $DEST/routing/config.yml"
echo "Auf dem Pi später:           java -Xmx3g -jar graphhopper-web-$GHV.jar server config.yml   (Port 8989)"

# 7) Prüfsummen
( cd "$DEST" && sha256sum *.pmtiles *.pbf > MANIFEST.sha256 )
du -sh "$DEST"
