from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile
from lol_anki.project import Project, ROOT
from lol_anki.io import read_json


@contextmanager
def sandbox_project():
    (ROOT/'build/tests').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT/'build/tests') as folder:
        original = Project()
        root = Path(folder)
        # Pilot-only tests need their pinned stores/snapshots, not every growing
        # champion archive, staging export, AI receipt and live review registry.
        paths=[original.path(k) for k in ('content','sources','lock')]
        paths += [ROOT/s['path'] for s in read_json(original.path('sources'))['snapshots']]
        for source in paths:
            target=root/source.relative_to(ROOT); target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        project = Project.__new__(Project)
        project.root = root
        project.config = original.config.copy()
        project.legacy = original.legacy
        project.fetcher = original.fetcher
        yield project
