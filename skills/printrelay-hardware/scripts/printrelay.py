#!/usr/bin/env python3
"""Small agent client. No supplier ordering or payment commands exist."""
import argparse, hashlib, json, os, re, sys, urllib.request, urllib.error, uuid
from pathlib import Path
BASE='https://printrelay.kva1.chatgpt.site'
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self, req, fp, code, msg, headers, newurl):
  raise RuntimeError('Unexpected API redirect; credential not forwarded.')
def call(path,method='GET',body=None,content_type='application/json',idem=None,public=False):
 key=''
 if not public:
  key=os.environ.get('PRINTRELAY_API_KEY','');key_file=os.environ.get('PRINTRELAY_API_KEY_FILE','')
  if key_file:
   if key:raise ValueError('Set only one of PRINTRELAY_API_KEY_FILE or PRINTRELAY_API_KEY.')
   from bootstrap_key import prepare
   key=prepare(key_file,resume=True)
 if not key and not public:raise ValueError('Set PRINTRELAY_API_KEY securely in the environment.')
 headers={'User-Agent':'PrintRelay/0.3 (+https://printrelay.kva1.chatgpt.site)','Accept':'application/json'}
 if not public:headers['Authorization']='Bearer '+key
 if body is not None:headers['Content-Type']=content_type
 if idem:headers['Idempotency-Key']=idem
 req=urllib.request.Request(BASE+path,data=body,headers=headers,method=method)
 try:
  with urllib.request.build_opener(NoRedirect).open(req,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as error:
  text=error.read(8192).decode('utf-8','replace');raise RuntimeError(f'API returned {error.code}: {text}') from None
 except (TimeoutError,urllib.error.URLError):raise RuntimeError('Network outcome is uncertain. Read the request status; retry an upload only with the SAME idempotency key.') from None
def request_id(value):
 if not re.fullmatch(r'req_[a-f0-9-]{36}',value):raise ValueError('Invalid request ID.')
 return value
def multipart(file_path,fields):
 path=Path(file_path);data=path.read_bytes()
 if not 0<len(data)<=10*1024*1024:raise ValueError('CAD must be nonempty and at most10MiB.')
 if path.suffix.lower() not in ('.stl','.step','.stp','.obj','.3mf'):raise ValueError('Unsupported CAD extension.')
 filename=re.sub(r'[^A-Za-z0-9._ -]','_',path.name)
 boundary='PrintRelay'+uuid.uuid4().hex;chunks=[]
 for name,value in fields.items():chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
 chunks.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode(),data,f'\r\n--{boundary}--\r\n'.encode()])
 return b''.join(chunks),'multipart/form-data; boundary='+boundary,hashlib.sha256(data).hexdigest()
def main(argv=None):
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 for name in ('list','capabilities','example'):sub.add_parser(name)
 for name in ('get','quotes','jobs','preflight','specifications'):
  p=sub.add_parser(name);p.add_argument('request_id',type=request_id)
 p=sub.add_parser('upload');p.add_argument('file');p.add_argument('--email',required=True);p.add_argument('--material',choices=['PLA','PETG','PA12'],required=True);p.add_argument('--quantity',type=int,required=True);p.add_argument('--units',choices=['mm','inch'],required=True);p.add_argument('--country',required=True);p.add_argument('--postal-code',required=True);p.add_argument('--speed',choices=['standard','fastest'],default='standard');p.add_argument('--notes',default='');p.add_argument('--idempotency-key',required=True);p.add_argument('--consent',action='store_true',required=True,help='Confirm the owner authorized intake upload.')
 p=sub.add_parser('specification');p.add_argument('request_id',type=request_id);p.add_argument('--json-file',required=True)
 p=sub.add_parser('compare');p.add_argument('request_id',type=request_id);p.add_argument('--fingerprint',required=True);p.add_argument('--providers',nargs='+',choices=['craftcloud','treatstock','xometry','jlc3dp','pcbway'],required=True);p.add_argument('--allow-provider-upload',action='store_true',required=True,help='Confirm owner authorized CAD upload to each named provider.')
 args=parser.parse_args(argv)
 if args.command in ('capabilities','example'):result=call('/api/capabilities' if args.command=='capabilities' else '/examples/calibration-cube-20mm.preflight.json',public=True)
 elif args.command=='list':result=call('/api/v1/requests')
 elif args.command in ('get','quotes','jobs','preflight','specifications'):
  suffix={'get':'','quotes':'/quotes','jobs':'/quote-jobs','preflight':'/preflight','specifications':'/specification'}[args.command];result=call('/api/v1/requests/'+args.request_id+suffix)
 elif args.command=='upload':
  fields={'email':args.email,'material':args.material,'quantity':args.quantity,'units':args.units,'country':args.country,'postal_code':args.postal_code,'desired_speed':args.speed,'notes':args.notes,'consent':'true'}
  body,ctype,sha=multipart(args.file,fields);result=call('/api/v1/requests','POST',body,ctype,args.idempotency_key)
  if result.get('file_sha256')!=sha:raise RuntimeError('Server file hash mismatch. Stop and inspect the request before any comparison.')
 elif args.command=='specification':
  body=json.loads(Path(args.json_file).read_text());result=call('/api/v1/requests/'+args.request_id+'/specification','PUT',json.dumps(body).encode())
 else:result=call('/api/v1/requests/'+args.request_id+'/quote-jobs','POST',json.dumps({'spec_fingerprint':args.fingerprint,'providers':args.providers,'allow_provider_upload':True}).encode())
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 try:main()
 except (ValueError,RuntimeError,OSError) as error:print(json.dumps({'error':{'code':'client_error','message':str(error)},'retry_automatically':False}),file=sys.stderr);sys.exit(1)
