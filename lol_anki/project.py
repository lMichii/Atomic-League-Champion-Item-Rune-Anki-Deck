from pathlib import Path
import tomllib
from .io import inside, read_json

ROOT = Path(__file__).resolve().parents[1]


class Project:
    def __init__(self, root=ROOT, profile='pilot'):
        self.root = Path(root).resolve()
        if profile not in ('pilot','batch01','editorial'):
            raise ValueError('Unknown production profile')
        filename = {'pilot':'pipeline.toml','batch01':'pipeline.batch01.toml','editorial':'pipeline.editorial.toml'}[profile]
        self.config = tomllib.loads((self.root/filename).read_text('utf-8'))
        self.legacy = inside(self.root, self.config['legacy_root'])
        self.fetcher = inside(self.root, self.config['legacy_fetcher'])

    def path(self, key):
        return inside(self.root, self.config[key])

    def content(self):
        return read_json(self.path('content'))

    def sources(self):
        return read_json(self.path('sources'))

    @property
    def media_roots(self):
        return [self.legacy, *[inside(self.root,p) for p in self.config.get('additional_media_roots',[])]]

    def media_root_for(self, row):
        if row['media_type']=='none':
            return self.legacy
        matches = [root for root in self.media_roots if inside(root,row['media_path']).is_file()]
        if len(matches)!=1:
            raise ValueError(f"Missing or ambiguous media: {row['media_path']}")
        return matches[0]

    def media_paths(self, used):
        return [p for root in self.media_roots for p in (root/'media').rglob('*') if p.is_file() and p.name in used]
