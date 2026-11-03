#!/usr/bin/env python3
"""Manifest der Riot-Medien in die bestehende Anki-Excel-Checkliste übernehmen.

Requires 'artifact_tool' (ChatGPT artifact environment). The independent
manifest.csv can always be opened in Excel/Sheets without this dependency.
"""
import argparse
import csv
from pathlib import Path


def run(workbook, manifest, out):
    from artifact_tool import Blob, SpreadsheetFile
    with Path(manifest).open('r', encoding='utf-8-sig', newline='') as f:
        records = list(csv.DictReader(f, delimiter=';'))
    root = Path(manifest).parent.resolve()
    from media_fetcher import slugify
    media = {(slugify(r['champion']), r['slot'].strip().upper()): r for r in records}
    wb = SpreadsheetFile.import_xlsx(Blob.load(str(workbook)))
    sheet = wb.worksheets.get_item('Anki-Karten')
    card_ids = sheet.get_range('A5:A2944').values
    headers = ['Media-Front lokal', 'Media-Poster lokal', 'Media-Video lokal',
               'Medienquelle-Version', 'Download vorhanden?', 'Medien nachgeprüft?']
    sheet.get_range('AH4:AM4').values = [headers]
    sheet.get_range('AH4:AM4').format = {'fill': '#276A78', 'font': {'bold': True, 'color': '#FFFFFF'},
                                         'row_height': 30, 'wrap_text': True}
    for c, width in {'AH': 40, 'AI': 35, 'AJ': 35, 'AK': 20, 'AL': 20, 'AM': 25}.items():
        sheet.get_range(f'{c}:{c}').format.column_width = width
    cols = ['N','O','X','Y','AF','AH','AI','AJ','AK','AL']
    previous = {col: sheet.get_range(f'{col}5:{col}2944').values for col in cols}
    changes = 0
    for i, data in enumerate(card_ids):
        card_id = str(data[0] or '')
        bits = card_id.split(':')
        if len(bits) < 4 or bits[0] != 'champ':
            continue
        champion = slugify(bits[1])
        level = bits[-1]
        slot = bits[2].upper()
        if level == 'L1':
            record = media.get((champion, 'P'))
            if not record: continue
            portrait = record.get('portrait_local', '')
            if portrait:
                previous['O'][i][0] = portrait
                previous['AH'][i][0] = portrait
                previous['AL'][i][0] = 'Ja'
            previous['X'][i][0] = record.get('riot_page') or previous['X'][i][0]
            previous['AK'][i][0] = record.get('ddragon_patch', '')
            previous['AF'][i][0] = 'Bild heruntergeladen · manuell prüfen' if portrait else 'Nicht verfügbar'
            changes += 1
            continue
        record = media.get((champion, slot))
        if not record: continue
        icon = record.get('icon_local') or ''
        video = record.get('video_local') or ''
        poster = record.get('poster_local') or ''
        front = record.get('front_local') or ''
        if icon: previous['O'][i][0] = icon
        if video: previous['N'][i][0] = video
        previous['X'][i][0] = record.get('riot_page') or previous['X'][i][0]
        previous['Y'][i][0] = record.get('video_source_url', '')
        previous['AF'][i][0] = record.get('media_status', '')
        previous['AH'][i][0] = front
        previous['AI'][i][0] = poster
        previous['AJ'][i][0] = video
        previous['AK'][i][0] = record.get('source_version', '')
        previous['AL'][i][0] = 'Ja' if front else 'Nein'
        changes += 1
    for col in cols:
        sheet.get_range(f'{col}5:{col}2944').values = previous[col]
    # Do NOT mark cards reviewed: media presence is not validation.
    sheet.get_range('AM5:AM2944').data_validation = {
        'rule': {'type':'list','values':['Nein','Ja','Prüfen']}}
    try:
        cat = wb.worksheets.get_item('Medienkatalog')
    except Exception:
        cat = wb.worksheets.add('Medienkatalog')
    cat_headers = ['Champion','Slot','Fähigkeit','Bevorzugtes Medium','Vorderseite (lokal)',
                   'Video (lokal)','Icon (lokal)','Status','Video-URL','Icon-URL',
                   'Riot-Seite','Patch','Korrektur nötig?']
    cat.get_range('A1:M1').values = [cat_headers]
    cat.get_range('A1:M1').format = {'fill':'#17344C','font':{'bold':True,'color':'#FFFFFF'},
                                     'row_height':32,'wrap_text':True}
    values = [[r.get(k, '') for k in ('champion','slot','ability_name','preferred_front',
              'front_local','video_local','icon_local','media_status','video_source_url',
              'icon_source_url','riot_page','ddragon_patch','needs_manual_review')]
              for r in records]
    if values: cat.get_range_by_indexes(1, 0, len(values), len(cat_headers)).values = values
    for col, w in {'A':19,'B':10,'C':25,'D':20,'E':44,'F':34,'G':34,'H':43,
                   'I':58,'J':58,'K':53,'L':16,'M':20}.items():
        cat.get_range(f'{col}:{col}').format.column_width = w
    cat.freeze_panes.freeze_rows(1)
    SpreadsheetFile.export_xlsx(wb).save(str(out))
    print(f'Excel aktualisiert: {out}\nVerknüpfte Karten: {changes} (Dateipfade relativ zu {root})')


def main():
    ap = argparse.ArgumentParser(description='media manifest.csv in LoL-Anki-Excel übernehmen')
    ap.add_argument('--workbook', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    run(Path(args.workbook), Path(args.manifest), Path(args.output))

if __name__ == '__main__':
    main()
