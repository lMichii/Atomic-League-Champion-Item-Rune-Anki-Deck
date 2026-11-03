"""Readable local excerpts for reviewing the archived Wiki snapshots."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
ROOT=Path(__file__).resolve().parents[1]

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.ignore=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.ignore+=1
        if tag in ('p','div','h2','h3','h4','li','tr'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.ignore-=1
    def handle_data(self,data):
        if not self.ignore: self.parts.append(data)

def main():
    access=json.loads((ROOT/'data/batch01/qa/source_access.json').read_text('utf-8'))
    for source in access:
        if source['provider']!='league_wiki' or source['status']!='retrieved': continue
        parser=Text(); parser.feed((ROOT/source['path']).read_text('utf-8'))
        text='\n'.join(re.sub(r'\s+',' ',line).strip() for line in ''.join(parser.parts).splitlines() if line.strip())
        output=ROOT/'build/batch01/wiki'/f'{source["champion"]}.txt'; output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(text,encoding='utf-8')
        print(source['champion'],output)

if __name__=='__main__': main()
