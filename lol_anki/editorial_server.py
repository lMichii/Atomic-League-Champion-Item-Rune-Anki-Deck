"""Loopback-only local review UI. Mutations require a session nonce and current revision."""
import base64
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
import urllib.parse
from .editorial import Editorial
from .editorial_media import variant_identity
from .editorial_export import EditorialExport
from .operations import project_operation,OperationBusy
from .io import atomic,canonical,digest,inside,read_json


def make_server(root,port=8765):
    editor=Editorial(root); editor.initialize(); editor.render(); nonce=secrets.token_urlsafe(32)
    workflow=EditorialExport(editor)
    # Keep the page and the action dispatcher from the same running code version.
    page=(Path(__file__).with_name('editorial_ui.html')).read_text(encoding='utf-8').replace('__NONCE__',nonce).encode()
    export_script=Path(__file__).with_name('editorial_export_ui.js').read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*a): pass
        def send(self,status,body,kind='application/json',filename=None):
            if not isinstance(body,bytes): body=canonical(body)
            self.send_response(status); self.send_header('Content-Type',kind+'; charset=utf-8')
            self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            if filename: self.send_header('Content-Disposition','attachment; filename="'+filename+'"')
            self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            try:
                if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}': return self.send(403,{'error':'Loopback host required'})
                path=urllib.parse.urlsplit(self.path).path
                if path=='/':
                    return self.send(200,page,'text/html')
                if path=='/editorial-export.js': return self.send(200,export_script,'text/javascript')
                if path=='/api/state':
                    with self.server.review_lock: return self.send(200,editor.state())
                query=urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
                if path=='/api/workflow': return self.send(200,{'proposals':workflow.list()})
                if path=='/api/proposal': return self.send(200,workflow.inspect(query['id'][0]))
                if path=='/api/proposal-file': return self.send(200,workflow.proposal_file(query['id'][0],query['file'][0]),'text/plain')
                if path=='/api/download':
                    name,blob=workflow.download(query['id'][0])
                    return self.send(200,blob,'application/octet-stream',filename=name)
                if path.startswith('/preview/'):
                    file=inside(editor.root/'build/editorial/workspaces',urllib.parse.unquote(path.removeprefix('/preview/')))
                    if file.suffix not in ('.html','.png','.jpg','.gif'): raise ValueError('Unsupported preview resource')
                    kind={'.html':'text/html','.png':'image/png','.jpg':'image/jpeg','.gif':'image/gif'}[file.suffix]
                    return self.send(200,file.read_bytes(),kind)
                return self.send(404,{'error':'Not found'})
            except OperationBusy as ex: self.send(409,{'error':str(ex)})
            except (ValueError,OSError,KeyError) as ex: self.send(400,{'error':str(ex)})
        def do_POST(self):
            origin=self.headers.get('Origin'); expected_origin=f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}' or self.headers.get('X-Review-Token')!=nonce or (origin and origin!=expected_origin): return self.send(403,{'error':'Local review session required'})
            if self.path!='/api/action' or self.headers.get_content_type()!='application/json': return self.send(400,{'error':'JSON review action required'})
            try: length=int(self.headers.get('Content-Length','0'))
            except ValueError: return self.send(400,{'error':'Invalid request length'})
            if not 0<length<=140*1024*1024: return self.send(413,{'error':'Request too large'})
            if not self.server.review_lock.acquire(blocking=False):
                return self.send(409,{'error':'Another review operation is running. Wait for it to finish, then retry.'})
            try:
                with project_operation(editor.root): self.dispatch(length)
            except OperationBusy as ex: self.send(409,{'error':str(ex)})
            except (ValueError,OSError,KeyError,TypeError,StopIteration) as ex: self.send(400,{'error':str(ex)})
            finally: self.server.review_lock.release()
        def dispatch(self,length):
                body=json.loads(self.rfile.read(length)); action=body['action']; key=body.get('id')
                request_id=body.get('request_id')
                request_hash=digest(canonical(body))
                if request_id:
                    previous=self.server.completed_requests.get(request_id)
                    if previous:
                        if previous['hash']!=request_hash: raise ValueError('Request identity reused with different changes')
                        return self.send(200,{'result':previous['result']})
                if action=='propose':
                    result=workflow.create(body.get('ids',[]))
                elif action=='apply-proposal':
                    result=workflow.apply(body['proposal_id'],body.get('accept_token',''),body.get('inspection_token',''),
                        body.get('reviewer',''),body.get('confirmed'),body.get('notes',''))
                elif action=='build-editorial':
                    result=workflow.build(body['proposal_id'],body.get('reviewer',''),body.get('notes',''))
                else:
                    record=editor.registry()['cards'][key]
                    if body.get('expected')!=digest(canonical(record)): raise ValueError('Stale review page; reload')
                    if action=='media-import':
                        extension=Path(body['filename']).suffix.lower()
                        if extension not in ('.png','.gif','.mp4','.webm'): raise ValueError('Upload PNG/GIF/MP4/WebM')
                        blob=base64.b64decode(body['bytes'],validate=True)
                        path=editor.root/'build/editorial/uploads'/(digest(blob)+extension); atomic(path,blob)
                        before_media_sha256=editor.effective(editor.registry()['cards'][key])[1]
                        card=editor.override_card(key)
                        target={'kind':'variant','identity':variant_identity(card)} if body.get('variant') else {'kind':'card','card_id':key}
                        target['role']=body.get('role','front')
                        result=editor.overrides.ingest(card,path,target,body['provenance'])
                        editor.audit_media_event(key,'media_import',body.get('reviewer',''),{
                            'before_media_sha256':before_media_sha256,'candidate_media_sha256':result['sha256'],
                            'source_sha256':result['source_sha256'],'override_id':result['id'],'role':result['target']['role'],
                            'candidate_review_status':result['review']['status']})
                    elif action=='override-approve':
                        record=editor.registry()['cards'][key]; before_media_sha256=editor.effective(record)[1]
                        before_override=editor.overrides.select(editor.override_card(key))
                        result=editor.overrides.approve(body['override_id'],editor.override_card(key),body['reviewer'],body.get('notes',''))
                        after_media_sha256=editor.effective(editor.registry()['cards'][key])[1]
                        after_override=editor.overrides.select(editor.override_card(key))
                        editor.audit_media_event(key,'override_approve',body['reviewer'],{
                            'before_media_sha256':before_media_sha256,'after_media_sha256':after_media_sha256,
                            'before_override_id':before_override['id'] if before_override else None,
                            'after_override_id':after_override['id'] if after_override else None,
                            'override_id':result['id'],'media_sha256':result['sha256'],
                            'source_sha256':result['source_sha256'],'matching_notes':result['review']['matching_notes']})
                    elif action=='approve-content-and-media':
                        result=editor.approve_content_and_media(key,body,body['expected'])
                    else: result=editor.mutate(key,action,body,body['expected'])
                    editor.render()
                if request_id:
                    if len(self.server.completed_requests)>=256: self.server.completed_requests.pop(next(iter(self.server.completed_requests)))
                    self.server.completed_requests[request_id]={'hash':request_hash,'result':result}
                self.send(200,{'result':result})
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.editor=editor; server.workflow=workflow; server.review_nonce=nonce; server.review_lock=threading.RLock()
    server.completed_requests={}
    return server


def serve(root,port=8765):
    server=make_server(root,port)
    print(f'Local editorial review: http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    finally: server.server_close()
