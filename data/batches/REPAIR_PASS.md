# Einzelreparaturen - Abschluss 03.11.2026

Alle elf zuvor gescheiterten Champions sind gespeichert. Keine automatischen Freigaben.

71 neue Karten; insgesamt 1089 eindeutige Karten fuer alle 173 Champions des gespeicherten Inventars.
136 freigegeben / 953 Entwuerfe. Anki-Importstatus wird durch Generierung/Export nicht gesetzt.

Export: `build/staging/League_Anki_Gesamtstand_Reparaturen_2026-11-03.apkg`
SHA-256: `fa9f3e1ffec5fde0cbfb6d0a31f1e41ff496afe5052f23dd5451a94817377420`

| Champion | Karten | GIF / Icon / Portrait |
| --- | ---: | --- |
| corki | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| jayce | 9 | {'icon': 8, 'portrait': 1} |
| kled | 7 | {'gif': 4, 'icon': 2, 'portrait': 1} |
| ksante | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| nunu | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| senna | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| sylas | 6 | {'gif': 3, 'icon': 2, 'portrait': 1} |
| zed | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| zeri | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| zoe | 6 | {'gif': 4, 'icon': 1, 'portrait': 1} |
| aurelionsol | 7 | {'gif': 3, 'icon': 3, 'portrait': 1} |

## Bestaetigte Korrekturen

- Corki: ungueltiges redundantes Quellenzitat entfernt; Lerntexte unveraendert.
- Jayce: sechs Q/W/E-Eintraege als Hammer-/Kanonen-Varianten klassifiziert; Lerntexte unveraendert.
- Kled: identische W-Abschnitte aus identischer Quellvorlage zusammengefuehrt; anschliessend ein Autorenaufruf.
- K’Sante: topic_placeholder aus aktiven Quellen entfernt. Detailmechanik (65% HP-Schwelle ohne Aenderung des Maximum-HP-Stats) nach ausdruecklicher Nutzerentscheidung massgeblich; ungenaue Kurzfassung als Quellenqualitaets-Hinweis. Kein offener Gameplay-Konflikt. Kartentexte und Counterplay unveraendert.
- Nunu: echte Wiki-Ueberschrift Absolute Zero samt unmittelbarem Kontext zusaetzlich belegt; Lerntexte unveraendert.
- Sylas: sechs ungueltige Championnamen im Formkontext entfernt; Texte und IDs unveraendert.

Alle Originalantworten, Fehlversuche und ausdruecklichen Nutzerbestaetigungen bleiben erhalten. Keine weiteren Modellaufrufe fuer diese manuellen Korrekturen.

## Medien und QA

- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:q:totheskies:transformmercuryhammer:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:q:shockblast:transformmercurycannon:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:w:lightningfield:transformmercuryhammer:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:w:hypercharge:transformmercurycannon:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:e:thunderingblow:transformmercuryhammer:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:ability_variant:e:accelerationgate:transformmercurycannon:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- jayce: {'code': 'icon_fallback', 'id': 'champ:jayce:r:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- kled: {'code': 'icon_fallback', 'id': 'champ:kled:ability_variant:q:pocketpistol:dismounted:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- ksante: {'code': 'source_unavailable', 'message': 'HTTP Error 404: Not Found', 'url': 'https://www.leagueoflegends.com/en-us/champions/k-sante/'}
- sylas: {'code': 'icon_fallback', 'id': 'champ:sylas:e:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- aurelionsol: {'code': 'source_unavailable', 'message': 'HTTP Error 404: Not Found', 'url': 'https://www.leagueoflegends.com/en-us/champions/aurelion-sol/'}
- aurelionsol: {'code': 'icon_fallback', 'id': 'champ:aurelionsol:r:recognize:L2', 'message': 'No confidently matched animation; icon retained'}
- aurelionsol: {'code': 'icon_fallback', 'id': 'champ:aurelionsol:ability_variant:r:theskiesdescend:fallingstar:recognize:L2', 'message': 'No confidently matched animation; icon retained'}

Die vollstaendigen Findings bleiben in den Champion-QA-Dateien und im strukturierten Bericht. Medien-Decoding wurde geprueft; keine GUI-/Mobil-Playback- oder aktuelle Live-Client-Pruefung behauptet.

## Verifikation

117 Tests ausgefuehrt: 116 bestanden, ein optionaler Browsertest uebersprungen. Ein frueherer Lauf hatte einen einzelnen Fehler im Concurrent-Review-Test; isolierter Wiederholungstest und anschliessender vollstaendiger Lauf bestanden ohne Abschwaechung des Tests.
Alle bisherigen 1018 Notizen samt IDs, GUIDs, vollstaendigen Feldern und Medienbytes sowie v4-Modelle unveraendert. Freigegebene Stores bytegleich; Original-100-Karten-Praefix unveraendert.
Echter temporaerer Anki-Import und Wiederimport: 1089 Karten, keine Duplikate; Lernfortschritt bei bestehenden UND neu hinzugefuegten Karten erhalten.

## Modellnutzung

11 Autorenaufrufe - genau einer je Champion. Keine separaten Verifier-/KI-Medienaufrufe. Keine weiteren KI-Aufrufe fuer die bestaetigten Korrekturen.
Verfuegbare Tokens: {'cache_write_input_tokens': 0, 'cached_input_tokens': 0, 'input_tokens': 244183, 'output_tokens': 48671, 'reasoning_output_tokens': 736}. Nicht ausgewiesene Modellidentitaet/Kosten werden nicht geschaetzt.

## Alle neuen Karten-IDs

- `champ:aurelionsol:ability_variant:r:theskiesdescend:fallingstar:recognize:L2`
- `champ:aurelionsol:e:recognize:L2`
- `champ:aurelionsol:overview:L1`
- `champ:aurelionsol:p:recognize:L2`
- `champ:aurelionsol:q:recognize:L2`
- `champ:aurelionsol:r:recognize:L2`
- `champ:aurelionsol:w:recognize:L2`
- `champ:corki:e:recognize:L2`
- `champ:corki:overview:L1`
- `champ:corki:p:recognize:L2`
- `champ:corki:q:recognize:L2`
- `champ:corki:r:recognize:L2`
- `champ:corki:w:recognize:L2`
- `champ:jayce:ability_variant:e:accelerationgate:transformmercurycannon:recognize:L2`
- `champ:jayce:ability_variant:e:thunderingblow:transformmercuryhammer:recognize:L2`
- `champ:jayce:ability_variant:q:shockblast:transformmercurycannon:recognize:L2`
- `champ:jayce:ability_variant:q:totheskies:transformmercuryhammer:recognize:L2`
- `champ:jayce:ability_variant:w:hypercharge:transformmercurycannon:recognize:L2`
- `champ:jayce:ability_variant:w:lightningfield:transformmercuryhammer:recognize:L2`
- `champ:jayce:overview:L1`
- `champ:jayce:p:recognize:L2`
- `champ:jayce:r:recognize:L2`
- `champ:kled:ability_variant:q:pocketpistol:dismounted:recognize:L2`
- `champ:kled:e:recognize:L2`
- `champ:kled:overview:L1`
- `champ:kled:p:recognize:L2`
- `champ:kled:q:recognize:L2`
- `champ:kled:r:recognize:L2`
- `champ:kled:w:recognize:L2`
- `champ:ksante:e:recognize:L2`
- `champ:ksante:overview:L1`
- `champ:ksante:p:recognize:L2`
- `champ:ksante:q:recognize:L2`
- `champ:ksante:r:recognize:L2`
- `champ:ksante:w:recognize:L2`
- `champ:nunu:e:recognize:L2`
- `champ:nunu:overview:L1`
- `champ:nunu:p:recognize:L2`
- `champ:nunu:q:recognize:L2`
- `champ:nunu:r:recognize:L2`
- `champ:nunu:w:recognize:L2`
- `champ:senna:e:recognize:L2`
- `champ:senna:overview:L1`
- `champ:senna:p:recognize:L2`
- `champ:senna:q:recognize:L2`
- `champ:senna:r:recognize:L2`
- `champ:senna:w:recognize:L2`
- `champ:sylas:e:recognize:L2`
- `champ:sylas:overview:L1`
- `champ:sylas:p:recognize:L2`
- `champ:sylas:q:recognize:L2`
- `champ:sylas:r:recognize:L2`
- `champ:sylas:w:recognize:L2`
- `champ:zed:e:recognize:L2`
- `champ:zed:overview:L1`
- `champ:zed:p:recognize:L2`
- `champ:zed:q:recognize:L2`
- `champ:zed:r:recognize:L2`
- `champ:zed:w:recognize:L2`
- `champ:zeri:e:recognize:L2`
- `champ:zeri:overview:L1`
- `champ:zeri:p:recognize:L2`
- `champ:zeri:q:recognize:L2`
- `champ:zeri:r:recognize:L2`
- `champ:zeri:w:recognize:L2`
- `champ:zoe:e:recognize:L2`
- `champ:zoe:overview:L1`
- `champ:zoe:p:recognize:L2`
- `champ:zoe:q:recognize:L2`
- `champ:zoe:r:recognize:L2`
- `champ:zoe:w:recognize:L2`
