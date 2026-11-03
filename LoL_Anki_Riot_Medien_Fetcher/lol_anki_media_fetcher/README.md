# LoL → Anki: Riot-Medien-Fetcher

Ein lokal ausführbares Werkzeug, um **offizielle Championbilder, Spell-Icons, Fähigkeit-Vorschaubilder und Videos** mit stabilen Namen für ein Anki-Deck zu sammeln. Der Export `manifest.csv` kann sofort in Excel oder Google Sheets geöffnet werden; `manifest.json` ist für den späteren APKG-Generator.

## Schnellstart (Windows, PowerShell)

1. ZIP entpacken und in den Projektordner wechseln.
2. **Python 3.10+** muss installiert sein. Für MP4-Videos außerdem **FFmpeg** mit `ffmpeg` im `PATH` (z. B. `winget install Gyan.FFmpeg`). Ohne FFmpeg bleiben Standbilder und Icons verfügbar.
3. Starten:

   ```powershell
   py media_fetcher.py --champions Ahri,Ezreal,Blitzcrank,Nautilus,Thresh,Locke --patch 16.21.1
   ```

   Die Ergebnisse landen im Ordner `output/`. Stelle vorher sicher, dass die CDNs erreichbar sind; das Skript benötigt **keinen Riot-API-Key**.

4. `output/manifest.csv` öffnen. Zum Bearbeiten der bisherigen Arbeitsmappe kannst du diese Datei zusammen mit der Excel-Datei in ChatGPT hochladen. Alternativ läuft `sync_excel.py` in einer Umgebung mit `artifact_tool`:

   ```powershell
   py sync_excel.py --workbook League_of_Legends_Anki_Tracker_mit_Medien_Pilot.xlsx --manifest output/manifest.csv --output League_Anki_mit_Medien.xlsx
   ```

   **Wichtig:** `sync_excel.py` braucht `artifact_tool`, das in der ChatGPT-Artefaktumgebung vorhanden ist, aber auf normalen PCs nicht unbedingt über pip erhältlich ist. Der Media-Fetcher selbst verwendet **ausschließlich die Python-Standardbibliothek**.

## Möglichkeiten

```powershell
# Nur Bilder, ohne größere Videodownloads
py media_fetcher.py --skip-videos

# GIFs statt MP4 (größere Dateien)
py media_fetcher.py --video-format gif

# Alle Champions aus dem gewählten DataDragon-Patch
py media_fetcher.py --champions all

# CommunityDragon zu einer festen Version statt latest abrufen
py media_fetcher.py --cdragon-version 16.21

# Nach einem Patch Update-Download erzwingen
py media_fetcher.py --patch latest --refresh

# Bereits vorhandene JSON-Daten und Mediendateien wiederverwenden
py media_fetcher.py --offline

# Automatische Tests (keine Internetverbindung erforderlich)
py -m unittest -v test_media_fetcher
```

## Wie es funktioniert

- **Riot Data Dragon (versionsgebunden):** Champion-Index, offizielle Championporträts, passive und aktive Spell-Icons.
- **CommunityDragon:** Die Riot-Client-Information `abilityVideoPath` und zugehörige Vorschaubilder. Video-Dateien selbst liegen auf Riots CloudFront.
- **P:** Icon als bevorzugte Vorderseite, damit visuell subtile Stack-Passives (z. B. Ezreal P) sinnvoll abgefragt werden.
- **Q/W/E/R:** Wenn möglich MP4 oder GIF (aus WebM); sonst Standbild aus Riot-Clip; sonst Fähigkeits-Icon. Eine Karte kann weiter ein Textprompt sein. *Das Medium wird vorgeschlagen, nicht didaktisch abgenommen.*
- **L1:** Championbild für Steckbrief. **L2:** Clip/Standbild/Icon je Fähigkeit. **L3:** Stats weiterhin manuell gegen das Wiki/Patch prüfen.
- **Keine doppelten Karten** entstehen durch dieses Werkzeug. Das entscheidet der nachgelagerte Anki-Generator mithilfe der Kartentyp-/Richtungs-Felder.

## Grenzen / Sicherheit

- `media_status` besagt nur, dass eine Datei technisch heruntergeladen oder konvertiert wurde, **nicht**, dass Animation und Inhalt zum aktuellen Patch passen. Das gilt besonders bei Reworks, Alternativ-Formen und alten Championvideos. Vor einem Anki-Export prüfen.
- Videos können mehr als eine Fähigkeit/Variante zeigen. Für manche Champions braucht die Datenbank zusätzliche Karten oder manuell ausgewählte Gameplay-Clips.
- Die CommunityDragon-URL `latest` ändert sich unabhängig von der gepinnten DataDragon-Version. Benutze für reproduzierbare Ergebnisse dieselbe CDragon-Version und ein archiviertes Manifest.
- Zum Download gelten die Bedingungen der Quellen. Für private Lernzwecke gedacht, **keine ausdrückliche Lizenz zur Veröffentlichung der Medien**.
- Die Datenbank enthält keine automatisch generierten Spielwert-Antworten. Riot-DDragon ist für exakte L3-Werte nicht allein zuverlässig.
- Bei `--offline` ohne vorherigen Mediencache gibt es eine klare Fehlermeldung; es werden keine erfundenen Dateien oder Download-Erfolge eingetragen.

## Ordner

```
output/
├── manifest.csv           # Bearbeitbarer Katalog
├── manifest.json          # Maschine-lesbar
├── media/
│   ├── champions/          # Porträts für L1
│   ├── abilities/          # Icons für L2 & L3
│   ├── posters/            # Standbilder für Clip-Fallback
│   └── videos/             # Konvertierte MP4/GIFs
└── cache/
    ├── ddragon/           # Patchgebundene Metadaten
    ├── cdragon/           # Fähigkeitspfade / Riot-Kurzbeschreibungen
    └── webm/              # Originalvideos
```

## Quellen

- https://developer.riotgames.com/docs/lol
- https://communitydragon.org/docs/assets
- https://www.leagueoflegends.com/de-de/champions/locke/
- https://wiki.leagueoflegends.com/en-us/
