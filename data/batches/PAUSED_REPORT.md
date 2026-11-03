# Gesicherter Stand — 02.11.2026

**Pausiert auf ausdruecklichen Nutzerwunsch. Keine weitere Generierung ohne neue Anweisung.**

## Gesamtexport

486 eindeutige Karten: 136 freigegeben, 350 Entwuerfe. 762 Mediendateien.
APKG: build/staging/League_Anki_Gesamtstand_2026-11-02.apkg
SHA-256: 12cb86e4fe0c676bd5d526b418a8d3e9c512270d0f8df3a689cd67bdac5df560

## Fortschritt

74 von 173 Champions mit gespeicherten Karten; 99 noch ohne vollstaendigen Kartensatz.
In diesem Produktionslauf: 50 Champions / 304 Karten in sechs Batch-Exporten.
Die restlichen Karten stammen aus dem bestehenden freigegebenen Bestand und aelteren Entwuerfen.

| Batch | Fertige Champions | Karten |
| --- | ---: | ---: |
| efficient-03 | 9 | 54 |
| efficient-04 | 10 | 63 |
| efficient-05 | 10 | 60 |
| efficient-06 | 9 | 54 |
| efficient-07 | 3 | 18 |
| production-pilot-02 | 9 | 55 |

## Offene Arbeit

- Fehlgeschlagen, nicht exportiert: Aurelion Sol, Corki, Jayce. Validierungsfehler und Originalantworten sind gespeichert.
- Kindred: am Modell-Nutzungslimit gestoppt; Quellen und Fortschritt sind gespeichert.
- Im letzten geplanten Batch noch nicht bearbeitet: Kled, KogMaw, KSante, LeBlanc, LeeSin, Lillia.
- 89 weitere Champions sind noch nicht ausgewaehlt.
- 16 aktive Staging-Karten verwenden passende Icon-Fallbacks. Details stehen in PAUSED_STATUS.json und den Batch-QA-Berichten.
- Aeltere offene Medien-/Sichtpruefungen, etwa Aphelios-Animationen und passive visuelle Hinweise, bleiben bestehen.

## Fertige Champions nach Batch

- efficient-03: bard, belveth, brand, briar, camille, cassiopeia, chogath, diana, draven.
- efficient-04: drmundo, ekko, elise, evelynn, fiddlesticks, fiora, fizz, galio, gangplank, gnar.
- efficient-05: gragas, graves, gwen, hecarim, heimerdinger, hwei, illaoi, irelia, ivern, janna.
- efficient-06: jarvaniv, jax, jhin, kaisa, kalista, karthus, kassadin, katarina, kayle.
- efficient-07: kayn, kennen, khazix.
- production-pilot-02: aatrox, akali, akshan, alistar, ambessa, amumu, anivia, aurora, azir.

## Modellnutzung

Autorenmodus: 53 Versuche; 1 ohne Tokenbeleg (Nutzungslimit).
Verfuegbare Tokenwerte: {'cache_write_input_tokens': 0, 'cached_input_tokens': 58496, 'input_tokens': 1099403, 'output_tokens': 202625, 'reasoning_output_tokens': 4056}.
Keine neuen separaten KI-Verifier- oder KI-Medienpruefungen. Historische Aufrufe vor der Umstellung sind separat in production-pilot-02/report.json dokumentiert.
Das bestehende Autorenmodell wurde nicht herabgestuft. Fruehere kleinere Modelltests begruenden noch keine belastbare Qualitaetsempfehlung.

## Sicherung und Pruefung

- Urspruenglicher 100-Karten-Praefix unveraendert: True.
- Nutzerfreigaben, manuelle Texte, Medien und Reviewdaten bleiben erhalten. Keine Freigaben durch diesen Export.
- APKG-Datenbank, eindeutige IDs, 17 Felder und Medienreferenzen geprueft.
- V4-Design und einfache Vorwaertsvorlage unveraendert. Kein Import in die persoenliche Anki-Sammlung.
- Generierungsstatus und Import-/Reviewstatus bleiben getrennt.

Abschlusspruefung: 110 Tests erfolgreich, keine Fehler oder Skips. Echter temporaerer Anki-Import mit 486 Karten und Wiederimport ohne Duplikate; bestehender Lernfortschritt blieb erhalten. Alle 136 freigegebenen Notizen sind im Gesamtexport feld- und ID-identisch zum separaten freigegebenen Export.
