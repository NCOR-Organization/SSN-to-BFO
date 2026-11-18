from pathlib import Path
import os,subprocess,json,hashlib,re,time
OUT=Path(__file__).parent/'candidate-gate';OUT.mkdir(exist_ok=True)
ROOT=Path((OUT.parent/'candidate-root.txt').read_text().strip())
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1');ENV['PATH']='/opt/miniconda3/bin:'+ENV.get('PATH','')
sha=lambda b:hashlib.sha256(b).hexdigest()
paths=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT,env=ENV).decode().split('\0')[:-1]
paths+=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT,env=ENV).decode().split('\0')[:-1]
meta={'root':str(ROOT),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,env=ENV).decode().strip(),'input_files':{p:sha((ROOT/p).read_bytes()) for p in paths},'excluded_user_files_copied':False}
(OUT/'input-manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
bindings={}
for name in ['coverage','rationale-proposals','human-review']:
 report=ROOT/'reports/current-assessment/v2'/('current-ssn-sosa-'+name+'.json')
 binding=json.loads(report.read_text())['binding']
 assert all(sha((ROOT/p).read_bytes())==h for p,h in binding['input_sha256'].items()), 'Stale report binding: '+name
 bindings[name]=binding['content_sha256']
(OUT/'report-binding-preflight.json').write_text(json.dumps({'status':'PASS','bindings':bindings},indent=2)+'\n')
start=time.monotonic()
with (OUT/'make-check.log').open('wb') as f:r=subprocess.run(['make','check'],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT)
raw=(OUT/'make-check.log').read_bytes();text=raw.decode(errors='replace')
result={'command':['make','check'],'cwd':str(ROOT),'return_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'test_summary':re.findall(r'^Ran \d+ tests? in [^\n]+',text,re.M),'outcome_summary':re.findall(r'^(?:OK|FAILED[^\n]*)$',text,re.M),'log_sha256':sha(raw)}
(OUT/'make-check-result.json').write_text(json.dumps(result,indent=2)+'\n')
pattern=re.compile(r'^={70}\n(?P<kind>ERROR|FAIL): (?P<test>[^\n]+)\n-{70}\n(?P<body>.*?)(?=^={70}\n|^-{70}\nRan \d+ tests? in |\Z)',re.M|re.S)
failures=[{'kind':m.group('kind'),'test':m.group('test'),'raw_traceback':m.group('body').rstrip('\n'),'log_start_line':text[:m.start()].count('\n')+1,'log_end_line':text[:m.end()].count('\n')+1,'raw_block_sha256':sha(m.group(0).encode())} for m in pattern.finditer(text)]
executed=[{'name':name,'outcome':outcome} for name,outcome in re.findall(r'^([^\n]+): (PASS|FAIL(?: \(\d+\))?)$',text,re.M) if not name.startswith('-') and name!='Validation suite']
inv={'canonical_result':result,'canonical_gate_passed':r.returncode==0,'gate_statement':'make check was executed and '+('passed.' if r.returncode==0 else 'did not pass. No exception is granted.'),'failures':failures,'failure_block_counts':{k:sum(x['kind']==k for x in failures) for k in ('FAIL','ERROR')},'executed_gate_steps':executed,'stages_not_reached':'Determine from raw log; if stopped in current_* tests, later validation stages and Makefile compile/check recipe were not reached.'}
(OUT/'failure-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
print(json.dumps({'result':result,'counts':inv['failure_block_counts']},indent=2),flush=True)

changes=[]
for path,expected in meta['input_files'].items():
 q=ROOT/path; actual=sha(q.read_bytes()) if q.is_file() else None
 if actual!=expected:changes.append({'path':path,'before':expected,'after':actual})
(OUT/'input-preservation.json').write_text(json.dumps({'changes':changes,'unchanged':not changes},indent=2)+'\n')
assert not changes,changes
