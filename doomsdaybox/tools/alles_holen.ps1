<#
.SYNOPSIS
    Holt den gesamten Wissensbestand der DoomsdayBox aus dem Netz. Ein Befehl, vier Phasen.

.BESCHREIBUNG
    Läuft nacheinander:
      1. zim       Kiwix-Archive (Wikipedia, Fachforen, Lehrbücher, Gutenberg) — rund 360 GB
      2. maps      Karten, Ortsdatenbank, Routing-Rohdaten                     — rund 210 GB
      3. models    Sprachmodelle für den Pi                                    — rund 27 GB
      4. software  ARM64-Programme, Pi OS, Python-Pakete                       — rund 1 GB

    Jede Phase ist fortsetzbar: abbrechen, Rechner neu starten, Befehl erneut aufrufen.
    Angefangene Dateien werden an der Abbruchstelle weitergeladen, fertige übersprungen.
    Jede Datei wird gegen die offizielle Prüfsumme geprüft und ins Manifest eingetragen.

    Rechne mit mehreren Tagen. Bei 50 Mbit/s sind 600 GB rund 27 Stunden reine Ladezeit,
    einzelne Spiegel drosseln aber deutlich stärker.

.BEISPIEL
    .\alles_holen.ps1
    .\alles_holen.ps1 -Ziel E:\DoomsdayBox -Ark E:\AI-ARK
    .\alles_holen.ps1 -Phasen zim,maps -Prio 2
#>
[CmdletBinding()]
param(
    # Wohin die Wissensbasis geschrieben wird.
    [string]$Ziel = 'D:\DoomsdayBox',
    # Wo die großen Modelle liegen; die Pi-Modelle werden von dort kopiert statt neu geladen.
    [string]$Ark = 'D:\AI-ARK',
    # Welche Phasen laufen sollen.
    [string[]]$Phasen = @('zim', 'maps', 'models', 'software'),
    # 1 = nur das Wichtigste, 2 = Standard, 3 = alles (Vorgabe).
    [int]$Prio = 3
)

$ErrorActionPreference = 'Stop'
$Werkzeuge = $PSScriptRoot
$py = (Get-Command python -ErrorAction SilentlyContinue) ?? (Get-Command python3 -ErrorAction SilentlyContinue)
if (-not $py) { throw 'Python nicht gefunden. Installieren: winget install Python.Python.3.12' }

# Laufwerk prüfen: FAT32 kann keine Dateien über 4 GB, die Wikipedia allein ist größer.
$laufwerk = (Split-Path -Qualifier (Resolve-Path -LiteralPath (Split-Path $Ziel -Parent) -ErrorAction SilentlyContinue)) `
            ?? (Split-Path -Qualifier $Ziel)
$fs = (Get-Volume -DriveLetter $laufwerk.TrimEnd(':') -ErrorAction SilentlyContinue).FileSystem
if ($fs -match '^FAT') { throw "$laufwerk ist $fs formatiert. Dateien über 4 GB sind dort unmöglich. exFAT oder NTFS nehmen." }

New-Item -ItemType Directory -Path $Ziel -Force | Out-Null
Write-Host "DoomsdayBox: Wissensbestand holen" -ForegroundColor Cyan
Write-Host "  Ziel   $Ziel   ($fs)"
Write-Host "  Phasen $($Phasen -join ', ')   Priorität bis $Prio`n"

$start = Get-Date
foreach ($phase in $Phasen) {
    Write-Host "── Phase $phase ──────────────────────────────" -ForegroundColor Cyan
    & $py.Source (Join-Path $Werkzeuge 'ddbox_fetch.py') $phase --root $Ziel --ark $Ark --max-prio $Prio
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Phase $phase endete mit Code $LASTEXITCODE. Befehl später erneut aufrufen, es wird fortgesetzt." -ForegroundColor Yellow
    }
}

$dauer = (Get-Date) - $start
$gb = [math]::Round((Get-ChildItem $Ziel -Recurse -File -ErrorAction SilentlyContinue |
                     Measure-Object Length -Sum).Sum / 1GB, 1)
Write-Host "`nFertig nach $([math]::Round($dauer.TotalHours,1)) h. Bestand: $gb GB in $Ziel" -ForegroundColor Green
Write-Host "Prüfen:  python `"$Werkzeuge\ddbox_fetch.py`" verify --root `"$Ziel`""
Write-Host "Logbuch: $Ziel\LOGBUCH.md"
