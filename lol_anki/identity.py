"""Frozen v1 identity contract: never include patch or prose in note identities."""
import hashlib
import re

MODEL_ID = 2042610311001
DECKS = {'root': 2042610312000, 'L0': 2042610312003,
         'L1': 2042610312001, 'L2': 2042610312002}


def stable_id(text, prefix):
    return prefix + int.from_bytes(hashlib.sha256(text.encode('utf-8')).digest()[:7], 'big') % 300_000_000_000


def guid(text):
    return hashlib.sha1(('lol-anki-pilot-v1:' + text).encode('utf-8')).hexdigest()[:14]


def new_key(kind, entity_id, concept, level):
    """Future items/runes use Riot numeric IDs, not display names or patch labels."""
    if kind not in ('champ', 'item', 'rune', 'term') or level not in ('L0', 'L1', 'L2', 'L3'):
        raise ValueError('Unknown entity kind or learning level')
    parts = (str(entity_id), concept)
    if any(not re.fullmatch(r'[a-z0-9_-]+', p) for p in parts):
        raise ValueError('Identity components must be stable lowercase tokens')
    return ':'.join((kind, *parts, level))
