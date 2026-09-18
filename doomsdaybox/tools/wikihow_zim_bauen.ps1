<#
.SYNOPSIS
    Baut aus beiden wikiHow-Crawls ein einziges ZIM-Archiv.

.BESCHREIBUNG
    Der erste Durchgang (16.09., 4 Arbeiter) lief 8,5 Stunden sauber und wurde dann von
    de.wikihow.com per HTTP 429 ausgebremst; er brachte 13.824 Seiten. Der zweite Durchgang
    (17./18.09., 1 Arbeiter, 4 Sekunden Pause) holt die restlichen 8.448 Adressen nach.

    Beide Durchgänge haben ihre Seiten als WARC-Dateien abgelegt. warc2zim liest beide Sätze
    zusammen und schreibt ein ZIM daraus. Doppelte Adressen werden dabei einmal übernommen.

    Voraussetzung: Durchgang 2 ist fertig (Container wikihow_de_lauf2 beendet).

.BEISPIEL
    .\zim_bauen.ps1
    .\zim_bauen.ps1 -Ziel D:\DoomsdayBox\zim\eigene
#>
[CmdletBinding()]
param(
    [string]$Basis = 'C:\stage\zim-eigene\wikihow_de',
    [string]$Ziel  = 'D:\DoomsdayBox\zim\eigene',
    [string]$Name  = 'wikihow_de_eigen_2026-09',
    # Nur prüfen, was gefunden wird, nichts bauen.
    [switch]$Probe
)

$ErrorActionPreference = 'Stop'

# --- WARC-Verzeichnisse beider Läufe einsammeln ---------------------------------
$warcOrdner = Get-ChildItem $Basis -Recurse -Filter '*.warc.gz' -ErrorAction SilentlyContinue |
    Group-Object { $_.Directory.FullName } |
    ForEach-Object {
        [pscustomobject]@{
            Pfad   = $_.Name
            Anzahl = $_.Count
            GB     = [math]::Round((($_.Group | Measure-Object Length -Sum).Sum) / 1GB, 1)
        }
    }

if (-not $warcOrdner) { throw "Keine WARC-Dateien unter $Basis gefunden." }

Write-Host "Gefundene WARC-Bestände:" -ForegroundColor Cyan
$warcOrdner | ForEach-Object { Write-Host ("  {0,3} Dateien  {1,5} GB  {2}" -f $_.Anzahl, $_.GB, $_.Pfad) }

# warc_lauf1 ist die Sicherheitskopie des ersten Laufs; das Original liegt noch im
# .tmp-Verzeichnis. Beide zu nehmen hiesse jede Seite doppelt einzulesen.
$nehmen = $warcOrdner | Where-Object { $_.Pfad -notmatch '\\warc_lauf1$' }
if (-not ($warcOrdner | Where-Object { $_.Pfad -match '\.tmpvtd7jt36' })) {
    # Originalverzeichnis von Lauf 1 ist weg, dann die Sicherheitskopie nehmen
    $nehmen = $warcOrdner | Where-Object { $_.Pfad -match '\\warc_lauf1$' -or $_.Pfad -notmatch '\\warc_lauf1$' }
}
Write-Host "`nVerwendet werden:" -ForegroundColor Cyan
$nehmen | ForEach-Object { Write-Host ("  {0,3} Dateien  {1,5} GB  {2}" -f $_.Anzahl, $_.GB, $_.Pfad) }
$gesamt = ($nehmen | Measure-Object GB -Sum).Sum
Write-Host ("  zusammen {0} GB" -f [math]::Round($gesamt, 1))

if ($Probe) { Write-Host "`nProbelauf, nichts gebaut." -ForegroundColor Yellow; exit 0 }

# --- Noch ein laufender Crawl? --------------------------------------------------
$laeuft = docker ps --format '{{.Names}}' | Where-Object { $_ -like 'wikihow*' }
if ($laeuft) { throw "Container $laeuft läuft noch. Erst abwarten, sonst fehlen Seiten." }

# --- Container-Pfade vorbereiten -------------------------------------------------
# WICHTIG: docker mit Container-Pfaden (/daten) nur aus PowerShell aufrufen.
# Git-Bash schreibt /daten in C:\Program Files\Git\daten um, dann bricht der Lauf ab.
New-Item -ItemType Directory -Path $Ziel -Force | Out-Null
$rel = $nehmen | ForEach-Object { '/daten/' + ($_.Pfad.Substring($Basis.Length).TrimStart('\') -replace '\\', '/') }

$args = @(
    'run', '--rm',
    '-v', "${Basis}:/daten",
    '-v', "${Ziel}:/ausgabe",
    'ghcr.io/openzim/zimit:latest',
    'warc2zim',
    '--name', $Name,
    '--title', 'wikiHow (Deutsch)',
    '--description', 'Deutschsprachige wikiHow-Anleitungen, Stand 09/2026 (CC BY-NC-SA)',
    '--language', 'deu',
    '--creator', 'wikiHow',
    '--publisher', 'Eigenarchiv DoomsdayBox',
    '--output', '/ausgabe',
    '--zim-file', "$Name.zim"
) + $rel

Write-Host "`nBaue ZIM, das dauert bei $([math]::Round($gesamt)) GB etwa eine Stunde ..." -ForegroundColor Cyan
Write-Host "docker $($args -join ' ')" -ForegroundColor DarkGray
$start = Get-Date
& docker @args
if ($LASTEXITCODE -ne 0) { throw "warc2zim endete mit Code $LASTEXITCODE" }

$datei = Join-Path $Ziel "$Name.zim"
if (Test-Path $datei) {
    $gb = [math]::Round((Get-Item $datei).Length / 1GB, 2)
    $dauer = [math]::Round(((Get-Date) - $start).TotalMinutes)
    Write-Host "`nFertig: $datei ($gb GB, $dauer min)" -ForegroundColor Green
    Write-Host "Weiter mit:" -ForegroundColor Cyan
    Write-Host "  zimcheck -A `"$datei`""
    Write-Host "  kiwix-manage D:\DoomsdayBox\zim\library.xml add `"$datei`""
    Write-Host "  Prüfsumme in D:\DoomsdayBox\zim\MANIFEST.sha256 nachtragen"
} else {
    throw "ZIM wurde nicht geschrieben."
}
