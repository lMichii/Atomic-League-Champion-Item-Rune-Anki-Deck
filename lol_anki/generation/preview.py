"""Standalone HTML fronts/backs using the exact frozen v4 templates and CSS."""
import html
import re
from pathlib import Path
from ..io import atomic
from ..v4 import CSS
from .presentation import learning_fields,draft_templates


def page_name(card):
    if card.get('learning_unit') or card.get('entity_kind') in ('item','term'):
        return re.sub(r'[^a-z0-9-]+','-',card['id'].casefold()).strip('-')+'.html'
    return card['row']['slot'].lower().replace('-','overview')+'.html'


def template(text,fields):
    pattern=re.compile(r'{{([#^])(\w+)}}(.*?){{/\2}}',re.S)
    while pattern.search(text):
        text=pattern.sub(lambda m:m[3] if bool(fields.get(m[2]))==(m[1]=='#') else '',text)
    return re.sub(r'{{(\w+)}}',lambda m:fields.get(m[1],''),text)


def create_previews(cards,folder):
    folder=Path(folder); output=folder/'previews'; output.mkdir(exist_ok=True)
    used=set(); links=[]
    front_template,back_template=draft_templates()
    for card in cards:
        fields,_=learning_fields(card,folder,used)
        # Text-only model fields are escaped for the standalone HTML document.
        for key in ('Champion','Ability','Slot','Level','Patch','Priority','Review','Riot','Wiki'):
            fields[key]=html.escape(fields[key],quote=True)
        front=template(front_template,fields)
        back=template(back_template,{**fields,'FrontSide':front})
        name=page_name(card)
        page='<!doctype html><html lang="en"><head><meta charset="utf-8"><base href="../media/"><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+CSS+'</style></head><body class="card">'
        page+='<nav aria-label="Preview controls" style="padding:10px"><button onclick="document.getElementById(\'front\').hidden=!document.getElementById(\'front\').hidden;document.getElementById(\'back\').hidden=!document.getElementById(\'back\').hidden">Show answer / front</button></nav>'
        page+='<main id="front">'+front+'</main><main id="back" hidden>'+back+'</main></body></html>'
        atomic(output/name,page.encode())
        label=card['row']['slot']+' · '+card['row']['ability']
        if card.get('entity_kind') in ('item','term'):
            label=card['row']['level']+' · '+(card['row']['champion'] if card['entity_kind']=='item' else card['row']['ability'])
        links.append(f'<li><a target="card" href="{name}">{html.escape(label)}</a></li>')
    count='Six' if len(cards)==6 else str(len(cards))
    title='Item prototype' if any(c.get('entity_kind')=='item' for c in cards) else 'Unapproved champion drafts'
    page_title='Item prototype' if title=='Item prototype' else 'Unapproved champion draft preview'
    index='<!doctype html><html lang="en"><meta charset="utf-8"><title>'+page_title+'</title><body style="background:#101317;color:#e8e8e8;font-family:Arial"><h1>'+title+'</h1><p>'+count+' cards only. No approved store or APKG was changed. <a style="color:#bfb5a5" href="../qa.json">Open structured QA</a> · <a style="color:#bfb5a5" href="../QA.md">Open QA report</a></p><nav><ul>'+''.join(links)+'</ul></nav><iframe title="v4 card preview" name="card" src="'+page_name(cards[0])+'" style="width:100%;height:850px;border:1px solid #363c43"></iframe></body></html>'
    if title=='Item prototype':
        index=index.replace('No approved store or APKG was changed.', 'Separate test package; approved content stores are unchanged.')
    atomic(output/'index.html',index.encode())
    return sorted(used)
