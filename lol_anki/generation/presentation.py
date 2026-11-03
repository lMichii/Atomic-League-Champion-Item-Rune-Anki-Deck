"""Card-facing draft projection. QA and asset provenance never become learning prose.

Draft previews share the same current-patch v4 template and source links as exports.
"""
import copy
import re
from ..v4 import QFMT,AFMT,render_fields,CURRENT_PATCH

QA_MARKER = re.compile(
    r'\b(?:inferred|supported|unsupported|unverified|unapproved|verified|confirmed|tentative|uncertain|confidence|metadata|provenance|review|proposal|draft|citation|evidence|verification|inference|QA|Wiki|Riot|CommunityDragon)\b'
    r'|\b(?:editorial review|source packet|source evidence|source support|attached (?:clip|frames)|factual risk|QA review)\b',re.I)
CARD_TEXT_FIELDS=('champion','ability','front_hint','question','answer','counterplay','build_focus','visual_cue_description')


def check_learning_text(text):
    if QA_MARKER.search(text):
        raise ValueError('Internal QA marker in card-facing text; put status/inference/evidence in structured metadata')


def check_learning_row(row):
    for key in CARD_TEXT_FIELDS:
        check_learning_text(row.get(key,''))


def version_fields(packet):
    """Do not interpret an asset version or a proposed patch name as verification."""
    versions=packet['versions']
    verified=versions.get('verified_game_patch')
    evidence=versions.get('game_patch_evidence',[])
    if not isinstance(verified,str) or not verified.strip() or not evidence:
        verified=None
    return {'asset_version':versions['ddragon'],'verified_game_patch':verified,
            'game_patch_evidence':evidence if verified else []}


def learning_fields(card,folder,used):
    row=copy.deepcopy(card['row'])
    check_learning_row(row)
    row['patch']=CURRENT_PATCH
    row['review_status']=''
    fields,tags=render_fields(row,folder,used)
    fields['Review']=''
    return fields,tags


def draft_templates():
    return QFMT,AFMT
