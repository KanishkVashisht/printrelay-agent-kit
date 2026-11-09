#!/usr/bin/env python3
"""partsforagents: advice, FDM job requests, tracking and feedback. No payment or print commands."""
import argparse, hashlib, json, os, re, sys, urllib.request, urllib.error, urllib.parse, uuid
from pathlib import Path
BASE='https://partsforagents.com'
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
 headers={'User-Agent':'PrintRelay/0.8 (+https://partsforagents.com)','Accept':'application/json'}
 if not public:headers['Authorization']='Bearer '+key
 if body is not None:headers['Content-Type']=content_type
 if idem:headers['Idempotency-Key']=idem
 req=urllib.request.Request(BASE+path,data=body,headers=headers,method=method)
 try:
  with urllib.request.build_opener(NoRedirect).open(req,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as error:
  text=error.read(8192).decode('utf-8','replace');raise RuntimeError(f'API returned {error.code}: {text}') from None
 except (TimeoutError,urllib.error.URLError):raise RuntimeError('Network outcome is uncertain. Read the saved request/order before retrying when a read is available. Feedback has no public lookup: replay its IDENTICAL saved body and SAME key to obtain the receipt. Never generate a replacement key automatically.') from None
def request_id(value):
 if not isinstance(value,str) or not re.fullmatch(r'req_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',value):raise ValueError('Invalid request ID.')
 return value
def order_id(value):
 if not isinstance(value,str) or not re.fullmatch(r'ord_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',value):raise ValueError('Invalid order ID.')
 return value
def fingerprint(value):
 if not isinstance(value,str) or not re.fullmatch(r'[a-f0-9]{64}',value):raise ValueError('Fingerprint must be 64 lowercase hexadecimal characters.')
 return value
def idempotency_key(value):
 if not re.fullmatch(r'[A-Za-z0-9._:-]{8,100}',value):raise ValueError('Idempotency key must be 8–100 letters, digits, dots, underscores, colons or hyphens.')
 return value
def json_file(path):
 body=json.loads(Path(path).read_text())
 if not isinstance(body,dict):raise ValueError('JSON file must contain one object.')
 return body
def feedback_body(body):
 allowed={'category','message','consent','agent_name','context_path'}
 if set(body)-allowed:raise ValueError('Only documented feedback fields are accepted; omit credentials, CAD and private customer/payment details.')
 if body.get('category') not in ('bug','docs','feature','ordering','pricing','other'):raise ValueError('Choose a documented feedback category.')
 if body.get('consent') is not True:raise ValueError('Feedback requires consent:true for non-sensitive product feedback.')
 for name,limit in (('message',4000),('agent_name',80),('context_path',240)):
  if name not in body and name!='message':continue
  value=body.get(name)
  if not isinstance(value,str) or not value.strip() or len(value.encode('utf-16-le'))//2>limit or re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]',value):raise ValueError(name+' must be bounded nonempty plain text; omit empty optional fields.')
 if 'context_path' in body:
  path=body['context_path'].strip()
  if not re.fullmatch(r'/[A-Za-z0-9_./-]*',path) or path.startswith('//') or any(part in ('.','..') for part in path.split('/')):raise ValueError('context_path must be a same-site pathname without query, fragment, IDs, secrets or dot segments.')
 if re.search(r'\b(?:pr_key_[a-f0-9]{64}|(?:sk|rk)_(?:live|test)_[A-Za-z0-9]+|Bearer\s+[A-Za-z0-9._~+/-]{16,})\b','\n'.join(str(body.get(name,'')) for name in ('message','agent_name','context_path')),re.I):raise ValueError('Remove credentials from feedback.')
 return body

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
 for name in ('list','capabilities','production-capabilities','example','orders'):sub.add_parser(name)
 for name in ('get','quotes','jobs','preflight','specifications'):
  p=sub.add_parser(name);p.add_argument('request_id',type=request_id)
 p=sub.add_parser('advice',help='Free public guidance; no key or CAD needed.')
 p.add_argument('--topic',choices=['getting_started','mesh','fdm','materials','fits','sls','costs']);p.add_argument('--process');p.add_argument('--material')
 for name in ('analyze','estimate'):
  p=sub.add_parser(name);p.add_argument('request_id',type=request_id);p.add_argument('--fingerprint',required=True,type=fingerprint)
 for name in ('order-status','cancel-order','fulfillment'):
  p=sub.add_parser(name);p.add_argument('order_id',type=order_id)
 p=sub.add_parser('feedback',help='Submit non-sensitive product feedback publicly, with no account key.')
 p.add_argument('--json-file',required=True,help='category, message, consent:true; optional agent_name/context_path.')
 p.add_argument('--idempotency-key',required=True,type=idempotency_key,help='Save and reuse with identical JSON after uncertainty.')
 p=sub.add_parser('order',help='Submit a NONBINDING job/review request now; an accepted offer and payment instructions follow review.')
 p.add_argument('--json-file',required=True,help='Exact request/spec, order_type and acknowledge_nonbinding:true; see SKILL.md.')
 p.add_argument('--idempotency-key',required=True,type=idempotency_key,help='Save and reuse with identical JSON after uncertainty.')
 p=sub.add_parser('upload');p.add_argument('file');p.add_argument('--email',required=True);p.add_argument('--material',choices=['PLA','PETG','PA12'],required=True);p.add_argument('--quantity',type=int,required=True);p.add_argument('--units',choices=['mm','inch'],required=True);p.add_argument('--country',required=True);p.add_argument('--postal-code',required=True);p.add_argument('--speed',choices=['standard','fastest'],default='standard');p.add_argument('--notes',default='');p.add_argument('--idempotency-key',required=True,type=idempotency_key);p.add_argument('--consent',action='store_true',required=True,help='Confirm the owner authorized intake upload.')
 p=sub.add_parser('specification');p.add_argument('request_id',type=request_id);p.add_argument('--json-file',required=True)
 p=sub.add_parser('compare');p.add_argument('request_id',type=request_id);p.add_argument('--fingerprint',required=True,type=fingerprint);p.add_argument('--providers',nargs='+',choices=['craftcloud','treatstock','xometry','jlc3dp','pcbway'],required=True);p.add_argument('--allow-provider-upload',action='store_true',required=True,help='Confirm owner authorized CAD upload to each named provider.')
 args=parser.parse_args(argv)
 if args.command in ('capabilities','production-capabilities','example'):result=call({'capabilities':'/api/capabilities','production-capabilities':'/api/production-capabilities','example':'/examples/calibration-cube-20mm.preflight.json'}[args.command],public=True)
 elif args.command=='feedback':result=call('/api/feedback','POST',json.dumps(feedback_body(json_file(args.json_file)),ensure_ascii=False).encode(),idem=args.idempotency_key,public=True)
 elif args.command=='advice':
  query=urllib.parse.urlencode({k:getattr(args,k) for k in ('topic','process','material') if getattr(args,k) is not None});result=call('/api/advice'+('?' + query if query else ''),public=True)
 elif args.command=='list':result=call('/api/v1/requests')
 elif args.command=='orders':result=call('/api/v1/orders')
 elif args.command in ('order-status','cancel-order','fulfillment'):
  result=call('/api/v1/orders/'+args.order_id+{'order-status':'','cancel-order':'/cancel','fulfillment':'/fulfillment'}[args.command],'POST' if args.command=='cancel-order' else 'GET')
 elif args.command in ('analyze','estimate'):
  result=call('/api/v1/requests/'+args.request_id+('/advice' if args.command=='analyze' else '/estimate')+'?'+urllib.parse.urlencode({'spec_fingerprint':args.fingerprint}))
 elif args.command=='order':
  body=json_file(args.json_file)
  if body.get('acknowledge_nonbinding') is not True:raise ValueError('Order JSON must explicitly acknowledge_nonbinding:true. This records a review request only, with no charge, supplier submission or printing.')
  request_id(body.get('request_id',''));fingerprint(body.get('spec_fingerprint',''))
  if body.get('order_type') not in ('dfm_review','quotation','manufacturing'):raise ValueError('order_type must be dfm_review, quotation or manufacturing.')
  if 'idempotency_key' in body:raise ValueError('Use --idempotency-key; do not include it in the REST JSON body.')
  result=call('/api/v1/orders','POST',json.dumps(body).encode(),idem=args.idempotency_key)
 elif args.command in ('get','quotes','jobs','preflight','specifications'):
  suffix={'get':'','quotes':'/quotes','jobs':'/quote-jobs','preflight':'/preflight','specifications':'/specification'}[args.command];result=call('/api/v1/requests/'+args.request_id+suffix)
 elif args.command=='upload':
  fields={'email':args.email,'material':args.material,'quantity':args.quantity,'units':args.units,'country':args.country,'postal_code':args.postal_code,'desired_speed':args.speed,'notes':args.notes,'consent':'true'}
  body,ctype,sha=multipart(args.file,fields);result=call('/api/v1/requests','POST',body,ctype,args.idempotency_key)
  if result.get('file_sha256')!=sha:raise RuntimeError('Server file hash mismatch. Stop and inspect the request before any comparison.')
 elif args.command=='specification':
  body=json_file(args.json_file);result=call('/api/v1/requests/'+args.request_id+'/specification','PUT',json.dumps(body).encode())
 else:result=call('/api/v1/requests/'+args.request_id+'/quote-jobs','POST',json.dumps({'spec_fingerprint':args.fingerprint,'providers':args.providers,'allow_provider_upload':True}).encode())
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 try:main()
 except (ValueError,RuntimeError,OSError) as error:print(json.dumps({'error':{'code':'client_error','message':str(error)},'retry_automatically':False}),file=sys.stderr);sys.exit(1)
