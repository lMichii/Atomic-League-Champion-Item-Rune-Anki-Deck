"""Configurable model adapter. No Riot retrieval, media processing or card mutation."""
import json
import base64
import logging
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from ..io import atomic, canonical, digest, read_json, write_json
from .contracts import schema_check

LOG=logging.getLogger(__name__)


class ModelError(RuntimeError): pass


class AIClient:
    def __init__(self, config, folder, offline=False):
        self.config=config; self.folder=Path(folder); self.offline=offline

    def generate(self, task, instructions, data, schema, validate=None, images=()):
        request={'task':task,'instructions':instructions,'data':data,'schema':schema,
                 'provider':self.config['provider'],'model':self.config.get('model',''),
                 'images_sha256':[digest(Path(p).read_bytes()) for p in images]}
        fingerprint=digest(canonical(request))
        folder=self.folder/fingerprint
        folder.mkdir(parents=True,exist_ok=True)
        write_json(folder/'request.json',request)
        def check(value):
            schema_check(value,schema)
            if validate: validate(value)
        if (folder/'accepted.json').exists():
            value=read_json(folder/'accepted.json'); check(value)
            receipt=read_json(folder/'receipt.json')
            if receipt['output_sha256']!=digest(canonical(value)):
                raise ModelError('Cached AI output hash mismatch')
            return value,receipt
        if self.offline: raise ModelError('Offline AI response not available: '+fingerprint)
        previous=sorted((p for p in folder.glob('attempt-*') if p.name.split('-')[-1].isdigit()),
                        key=lambda p:int(p.name.split('-')[-1]))
        offset=max((int(p.name.split('-')[-1]) for p in previous),default=0)
        # A provider quota stop produces no card and must not consume its repair
        # allowance when the user resumes after their usage window resets.
        quota_terms=('usage limit','quota','rate limit','too many requests')
        consumed=sum(not ((p/'error.json').exists() and any(t in read_json(p/'error.json')['message'].casefold() for t in quota_terms)) for p in previous)
        remaining=self.config['max_total_attempts']-consumed if 'max_total_attempts' in self.config else self.config['attempts']
        if remaining<=0: raise ModelError('Persistent model-attempt budget exhausted: '+fingerprint)
        errors=[read_json(p/'error.json')['message'] for p in previous if (p/'error.json').exists()]
        validation_errors=[read_json(p/'error.json')['message'] for p in previous
                           if (p/'error.json').exists() and read_json(p/'error.json')['type']=='ValueError']
        for retry in range(1,min(self.config['attempts'],remaining)+1):
            attempt=offset+retry
            attempt_dir=folder/f'attempt-{attempt}'; attempt_dir.mkdir(exist_ok=True)
            repair={'validation_errors':validation_errors[-1:]} if validation_errors else {}
            prompt=instructions+'\n\nINPUT DATA (JSON):\n'+json.dumps({'evidence_and_draft':data,**repair},ensure_ascii=False)
            atomic(attempt_dir/'prompt.txt',prompt.encode())
            write_json(attempt_dir/'schema.json',schema)
            try:
                if self.config['provider']=='codex':
                    value,metadata=self._codex(prompt,attempt_dir,images)
                elif self.config['provider']=='openai':
                    value,metadata=self._openai(prompt,schema,attempt_dir,images)
                else: raise ModelError('Unknown AI provider; choose codex or openai')
                write_json(attempt_dir/'response.json',value)
                write_json(attempt_dir/'metadata.json',metadata)
                check(value)
                receipt={'request_sha256':fingerprint,'output_sha256':digest(canonical(value)),
                         'provider':self.config['provider'],'configured_model':self.config.get('model',''),
                         'attempts':attempt,'execution_attempts':retry,'prior_errors':errors,'metadata':metadata}
                write_json(folder/'accepted.json',value); write_json(folder/'receipt.json',receipt)
                return value,receipt
            except (OSError,ValueError,ModelError,subprocess.TimeoutExpired) as ex:
                message=str(ex)[:1800]
                errors.append(message); write_json(attempt_dir/'error.json',{'type':type(ex).__name__,'message':message})
                if isinstance(ex,ValueError): validation_errors.append(message)
                LOG.warning('AI %s attempt %d (try %d/%d this execution) failed: %s',task,attempt,retry,self.config['attempts'],message)
                if self.config.get('stop_on_usage_limit') and any(term in message.casefold() for term in quota_terms):
                    raise ModelError('Provider usage limit: '+message)
                if retry<self.config['attempts']: time.sleep(min(2**(retry-1),4))
        raise ModelError(f'AI {task} failed after {self.config["attempts"]} attempts this execution; inspect {folder}')

    def _codex(self,prompt,folder,images=()):
        executable=shutil.which(self.config.get('executable','codex'))
        if not executable: raise ModelError('Codex CLI unavailable; configure provider or install/login once')
        work=folder/'isolated-work'; work.mkdir(exist_ok=True)
        output=folder/'model-output.json'
        command=[executable,'exec','--ephemeral','--ignore-user-config','--skip-git-repo-check',
                 '-c','project_doc_max_bytes=0',
                 '--sandbox','read-only','--cd',str(work.resolve()),'--color','never','--json',
                 '--output-schema',str((folder/'schema.json').resolve()),
                 '--output-last-message',str(output.resolve())]
        if self.config.get('model'): command+=['--model',self.config['model']]
        for path in images: command+=['--image',str(Path(path).resolve())]
        command+=['-']
        result=subprocess.run(command,input=prompt,capture_output=True,text=True,encoding='utf-8',
                              timeout=self.config['timeout_seconds'])
        # No keys/tokens are ever read. Keep only public session events and bounded diagnostics.
        atomic(folder/'events.jsonl',result.stdout.encode())
        atomic(folder/'stderr.txt',result.stderr[-16000:].encode())
        if result.returncode: raise ModelError('Codex invocation failed: '+result.stderr[-1200:])
        events=[]
        for line in result.stdout.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: continue
        tool_items=[e for e in events if e.get('item',{}).get('type') not in (None,'agent_message','reasoning','plan')]
        if tool_items: raise ModelError('AI provider attempted tool use; generation must consume only the evidence packet')
        if not output.exists(): raise ModelError('Codex did not return a structured result')
        value=read_json(output)
        version=subprocess.run([executable,'--version'],capture_output=True,text=True,timeout=10).stdout.strip()
        usage=[e.get('usage') for e in events if e.get('type')=='turn.completed']
        return value,{'runtime_version':version,'usage':usage,'ephemeral':True,'tool_items':0,
                      'resolved_model':self.config.get('model') or 'runtime_default_not_reported',
                      'image_inputs':len(images)}

    def _openai(self,prompt,schema,folder,images=()):
        key=os.environ.get(self.config.get('api_key_env','OPENAI_API_KEY'))
        if not key: raise ModelError('Configured API key environment variable is missing')
        if not self.config.get('model'): raise ModelError('Set ai.model for the OpenAI provider')
        endpoint=self.config.get('endpoint','https://api.openai.com/v1/responses')
        if endpoint!='https://api.openai.com/v1/responses':
            raise ModelError('OpenAI adapter only sends credentials to the official Responses endpoint')
        content=[{'type':'input_text','text':prompt}]
        for path in images:
            content.append({'type':'input_image','image_url':'data:image/png;base64,'+base64.b64encode(Path(path).read_bytes()).decode()})
        body={'model':self.config['model'],'input':[{'role':'user','content':content}],'store':False,
              'max_output_tokens':self.config['max_output_tokens'],
              'text':{'format':{'type':'json_schema','name':'champion_draft','strict':True,'schema':schema}}}
        req=urllib.request.Request(endpoint,data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req,timeout=self.config['timeout_seconds']) as response:
                raw=json.loads(response.read(2*1024*1024))
        except urllib.error.HTTPError as ex:
            raise ModelError(f'OpenAI HTTP {ex.code}; response body omitted to avoid credential disclosure') from ex
        write_json(folder/'api-response.json',raw)
        if raw.get('status') not in ('completed',None): raise ModelError('API response was incomplete')
        content=[c for o in raw.get('output',[]) for c in o.get('content',[]) if c.get('type')=='output_text']
        if not content: raise ModelError('API refusal or missing structured text')
        return json.loads(''.join(c['text'] for c in content)),{'model':raw.get('model'),'response_id':raw.get('id'),'usage':raw.get('usage')}
