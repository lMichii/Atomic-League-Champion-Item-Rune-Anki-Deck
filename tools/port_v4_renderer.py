"""One-time mechanical extraction of the frozen v4 renderer; no legacy edits."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT/'LoL_Anki_Pilot_Project_v4_English/build_deck.py').read_text('utf-8')
module = source.split('\ndef build():')[0]
module = module.replace("ROOT=Path(__file__).resolve().parent", "ROOT=Path(__file__).resolve().parents[1]/'LoL_Anki_Pilot_Project_v4_English'")
module = module.replace('def media_file(p):', 'def media_file(p, root=ROOT):').replace('path=ROOT/str(p)', 'path=root/str(p)').replace('if MEDIA.resolve() not in path.resolve().parents:', 'if (root/\'media\').resolve() not in path.resolve().parents:')
module = module.replace('def render_media(r, used):', 'def render_media(r, used, root=ROOT):').replace("fname=media_file(r['media_path']);", "fname=media_file(r['media_path'], root);")
start = source.index("            used.add(media_file(r['icon_path']))")
end = source.index('            # Anki csum', start)
body = source[start:end]
body = '\n'.join(line[8:] for line in body.splitlines())
body = body.replace('front=render_media(r,used)', 'front=render_media(r,used,root)')
module += '\n\ndef render_fields(r, root, used):\n    media_file = lambda p: globals()["media_file"](p, root)\n'+body+'\n    return flds, tags\n'
module = module.replace('"""LoL Anki Pilot Builder (stdlib only). Run: python build_deck.py\nEdit cards.csv and keep stable IDs to update notes on re-import.\n"""', '"""Frozen v4 visual/wording renderer, mechanically ported from the legacy builder.\nSee tools/port_v4_renderer.py. Preserve CSS, field order and template count.\n"""')
(ROOT/'lol_anki/v4.py').write_text(module, encoding='utf-8')
print('Ported v4 renderer without changing its visual contract.')
