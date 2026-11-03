"""Run repository tests without requiring installation or unsafe Python path flags."""
import sys
from pathlib import Path
import unittest
import importlib.util
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
# Keep original tests' default temporary files inside the writable project too.
temp_root = ROOT/'build/tests/tmp'
temp_root.mkdir(parents=True,exist_ok=True)
tempfile.tempdir = str(temp_root)
# Optional isolated importer runtime; installed with requirements-anki-test.txt.
runtime = ROOT/'.cache/anki-runtime'
if runtime.exists():
    sys.path.insert(0,str(runtime))
suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
legacy = ROOT/'LoL_Anki_Riot_Medien_Fetcher/lol_anki_media_fetcher'
sys.path.insert(0,str(legacy))
if importlib.util.find_spec('PIL'):
    suite.addTests(unittest.defaultTestLoader.discover(str(legacy),pattern='test_media_fetcher.py',top_level_dir=str(legacy)))
result = unittest.TextTestRunner(verbosity=2).run(suite)
from lol_anki.io import write_json
write_json(ROOT/'build/reports/tests.json',{
    'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
    'skipped':len(result.skipped),'successful':result.wasSuccessful(),
    'skip_reasons':[reason for _,reason in result.skipped]})
raise SystemExit(not result.wasSuccessful())
