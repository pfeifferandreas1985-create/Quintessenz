<#
.SYNOPSIS
    Erzeugt eigene ZIM-Dateien mit zimit (Website-Kopien) und mwoffliner (Wikipedia-Themenauszuege).
    Braucht Docker Desktop (laufend). Ausgabe nach D:\DoomsdayBox\zim\eigene\ - auf C:\stage bauen, dann verschieben (HDD-Regel).
.HINWEIS
    zimit laedt komplette Websites - je Seite 1-6 Stunden. Nacheinander laufen lassen, nicht parallel.
    Rechtlich: Elektronik-Kompendium und mikrocontroller.net sind urheberrechtlich geschuetzt; die Kopie ist als
    Privatkopie fuer den eigenen Gebrauch zulaessig, darf aber nicht weitergegeben werden -> zim\eigene\privat\.
.BEISPIEL
    .\zimit_jobs.ps1 -Job elektronik-kompendium
    .\zimit_jobs.ps1 -Job alle
#>
param(
    [string]$Job = "alle",
    [string]$Stage = "C:\stage\zim-eigene",
    [string]$Ziel = "D:\DoomsdayBox\zim\eigene"
)
$ErrorActionPreference = "Continue"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Host "docker fehlt - Docker Desktop installieren und starten" -ForegroundColor Red; exit 1 }
docker info 2>$null | Out-Null; if ($LASTEXITCODE -ne 0) { Write-Host "Docker laeuft nicht - Docker Desktop starten" -ForegroundColor Red; exit 1 }
New-Item -ItemType Directory -Force -Path "$Stage\privat", "$Stage\frei" | Out-Null

# --- zimit: Website -> ZIM  (Name, URL, Ordner, Seitenlimit, zusaetzliche Optionen) ---
$Sites = @(
    @{ Name="elektronik-kompendium"; Url="https://www.elektronik-kompendium.de/"; Ordner="privat"; Limit=20000;
       Extra=@("--scopeType","host","--exclude",".*(forum|shop|impressum|datenschutz).*") }
    @{ Name="mikrocontroller-net";   Url="https://www.mikrocontroller.net/articles/Hauptseite"; Ordner="privat"; Limit=6000;
       Extra=@("--scopeType","prefix","--include","https://www.mikrocontroller.net/articles/.*") }   # nur das Wiki, nicht das Forum
    @{ Name="darc-lehrgang";         Url="https://www.darc.de/der-club/referate/ajw/lehrgang-ta/"; Ordner="frei"; Limit=3000;
       Extra=@("--scopeType","prefix") }
    @{ Name="meshtastic-docs";       Url="https://meshtastic.org/docs/"; Ordner="frei"; Limit=3000;
       Extra=@("--scopeType","prefix") }
    @{ Name="akvopedia";             Url="https://akvopedia.org/wiki/Main_Page"; Ordner="frei"; Limit=8000;
       Extra=@("--scopeType","host") }
)

# --- mwoffliner: Wikipedia-DE-Auszuege nach Kategorie, mit Bildern (Themen-ZIMs fuer Bestimmung) ---
$Themen = @(
    @{ Name="wikipedia_de_pilze";        Kategorien="Kategorie:Pilze,Kategorie:Speisepilz,Kategorie:Giftpilz" }
    @{ Name="wikipedia_de_wildpflanzen"; Kategorien="Kategorie:Wildgemüse,Kategorie:Heilpflanze,Kategorie:Giftpflanze,Kategorie:Essbare_Pflanze" }
    @{ Name="wikipedia_de_elektrotechnik"; Kategorien="Kategorie:Elektrotechnik,Kategorie:Elektronik,Kategorie:Antriebstechnik" }
)

function Run-Zimit($s) {
    $out = Join-Path $Stage $s.Ordner
    Write-Host "`n=== zimit: $($s.Name) -> $out ===" -ForegroundColor Cyan
    $args = @("run","--rm","-v","${out}:/output","ghcr.io/openzim/zimit","zimit",
              "--seeds",$s.Url,"--name",$s.Name,"--pageLimit",$s.Limit,"--workers","4","--timeout","90",
              "--title",$s.Name,"--description","Offline-Kopie fuer DoomsdayBox","--zim-lang","deu") + $s.Extra
    & docker @args
    Add-Content "D:\DoomsdayBox\LOGBUCH.md" "| $(Get-Date -f 'yyyy-MM-dd HH:mm') | zimit $($s.Name) | Exit $LASTEXITCODE |"
}
function Run-Mwoffliner($t) {
    $out = Join-Path $Stage "frei"
    Write-Host "`n=== mwoffliner: $($t.Name) ===" -ForegroundColor Cyan
    # Artikelliste aus Kategorien erzeugen (rekursiv 1 Ebene) - mwoffliner erwartet eine Datei mit Titeln
    $list = Join-Path $out "$($t.Name).txt"
    $titles = foreach ($k in $t.Kategorien -split ",") {
        $u = "https://de.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=$([uri]::EscapeDataString($k))&cmlimit=500&cmnamespace=0&format=json"
        try { (Invoke-RestMethod $u -Headers @{ "User-Agent"="ai-ark-ddbox" }).query.categorymembers.title } catch { }
    }
    $titles | Sort-Object -Unique | Set-Content $list -Encoding utf8
    Write-Host "  $($titles.Count) Artikel"
    & docker run --rm -v "${out}:/output" ghcr.io/openzim/mwoffliner mwoffliner `
        --mwUrl=https://de.wikipedia.org --adminEmail=lokal@example.invalid --articleList="/output/$($t.Name).txt" `
        --outputDirectory=/output --customZimTitle=$t.Name --format=nopdf --format=nodet --webp
    Add-Content "D:\DoomsdayBox\LOGBUCH.md" "| $(Get-Date -f 'yyyy-MM-dd HH:mm') | mwoffliner $($t.Name) | Exit $LASTEXITCODE, $($titles.Count) Artikel |"
}

foreach ($s in $Sites)  { if ($Job -eq "alle" -or $Job -eq $s.Name) { Run-Zimit $s } }
foreach ($t in $Themen) { if ($Job -eq "alle" -or $Job -eq $t.Name) { Run-Mwoffliner $t } }

Write-Host "`nErgebnisse liegen in $Stage. Nach Pruefung (zimcheck -C) sequentiell nach $Ziel verschieben:" -ForegroundColor Green
Write-Host "  robocopy `"$Stage`" `"$Ziel`" /E /MOV /COPY:DAT /R:2 /W:5"
