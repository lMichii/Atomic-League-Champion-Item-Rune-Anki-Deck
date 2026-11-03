"""Opt-in learning presentation shared by items, glossary and future card families.

Inline styles keep the published v4 note type/CSS byte-identical. Palette values
live here once, like the existing stat formatter; callers supply plain text only.
"""
import html
import re
from .v4 import format_stats

KEYWORDS = {
    'charm': ('charm', '#f39acb'),
    'suppression': ('suppression', '#d99be8'),
    'stun': ('stuns?', '#f3db75'),
    'root': ('roots?(?: / snare)?|snare', '#81d8a1'),
    'airborne': ('airborne|knock[ -]?ups?|knockbacks?', '#91d5ff'),
    'stasis': ('stasis', '#e3c776'),
    'grievous-wounds': ('grievous wounds', '#ff9999'),
    'silence': ('silence', '#c8b9ed'),
    'nearsight': ('nearsight', '#acbaff'),
    'on-hit': ('on[ -]hit', '#9bdacb'),
}
PATTERN = re.compile(r'(?<![a-zA-Z])(?:' + '|'.join('(?:'+p+')' for p,_ in KEYWORDS.values()) + r')(?![a-zA-Z])', re.I)
SECTION_LABELS = {'Cooldown','Can remove','Can do','Cannot remove','Limitations','Key difference','Use'}


def format_learning(value):
    """Highlight named mechanics only; preserve the existing damage/stat palette."""
    value=str(value or ''); parts=[]; last=0
    for match in PATTERN.finditer(value):
        parts.append(format_stats(value[last:match.start()]))
        key,color=next((key,color) for key,(pattern,color) in KEYWORDS.items() if re.fullmatch(pattern,match[0],re.I))
        parts.append(f'<span class="keyword keyword-{key}" style="color:{color};font-weight:600">'+html.escape(match[0])+'</span>')
        last=match.end()
    parts.append(format_stats(value[last:]))
    return ''.join(parts)


def render_sections(sections):
    """Compact optional sections, without HTML in authored learning text."""
    seen=set(); result=[]
    for section in sections:
        label=section['label']; text=section['text']
        if label not in SECTION_LABELS or label in seen or not isinstance(text,str) or not text.strip():
            raise ValueError('Invalid or duplicate learning section')
        seen.add(label)
        result.append('<div class="learning-section" style="margin:0 0 12px"><b style="color:#c9ad74">'+html.escape(label)+':</b><br>'+format_learning(text)+'</div>')
    if not result: raise ValueError('Learning sections cannot be empty')
    return ''.join(result)
