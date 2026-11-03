"""Archive public source pages and record ordinary HTTP failures transparently."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lol_anki.cache import Cache
from lol_anki.io import atomic,write_json
cache=Cache(ROOT/'.cache/http',offline='--offline' in sys.argv,retries=1,timeout=12)
results=[]
for name in ('Caitlyn','Ashe','Jinx','Leona','Lux','Morgana'):
    for provider,url in [('riot_page',f'https://www.leagueoflegends.com/en-us/champions/{name.lower()}/'),('league_wiki',f'https://wiki.leagueoflegends.com/en-us/{name}')]:
        try:
            blob,meta=cache.get(url,'html')
            path=ROOT/'data/batch01/sources/raw'/f'{meta["sha256"]}.html'
            atomic(path,blob)
            result={'champion':name,'provider':provider,'url':url,'status':'retrieved',**meta,'path':path.relative_to(ROOT).as_posix()}
        except (OSError,ValueError) as ex:
            result={'champion':name,'provider':provider,'url':url,'status':'unavailable','error':str(ex)}
        results.append(result)
        print(name,provider,result['status'],flush=True)
write_json(ROOT/'data/batch01/qa/source_access.json',results)
