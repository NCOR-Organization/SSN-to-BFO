from pathlib import Path
import os, subprocess, tempfile, json, hashlib, re, time, sys
import rdflib, openpyxl, coms
SOURCE=Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO')
OUT=Path(__file__).resolve().parent
BASE='3376e1c74e846e40e6863ec8b1f1c255349aa2d3'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
ENV['PATH']='/opt/miniconda3/bin:'+ENV.get('PATH','')
CLONE=Path(tempfile.mkdtemp(prefix='ssn-platform-baseline-',dir='/tmp'))/'checkout'
commands=[['git','clone','--shared','--no-checkout',str(SOURCE),str(CLONE)],['git','-C',str(CLONE),'checkout','--detach',BASE]]
with (OUT/'clone.log').open('wb') as f:
 for cmd in commands:
  subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env=ENV,check=True)
def git(*args):return subprocess.check_output(['git','-C',str(CLONE),*args],env=ENV).decode()
def sha(b):return hashlib.sha256(b).hexdigest()
head=git('rev-parse','HEAD').strip();status=git('status','--porcelain=v1','--untracked-files=all')
assert head==BASE,(head,BASE)
assert not status,status
meta={'baseline':BASE,'clone':str(CLONE),'clone_commands':commands,'clean_head_verified':head,'status_before':status,'source_user_untracked_files_copied':False,'main_repository_modified':False,'git_optional_locks':'0','python':sys.executable,'scope':'Fresh detached offline local shared clone; not a registered worktree. Only committed baseline files are present.'}
(OUT/'clone-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
inputs=[]
for path in ['imports/sosa.ttl','imports/sosa-sampling.ttl','imports/ssn.ttl','imports/ssn-systems.ttl','imports/cco.ttl','mappings/SSN2BFO-COMS.xlsx','queries/source-classes-and-object-properties.rq']:
 p=CLONE/path; present=p.is_file()
 v={'path':path,'present':present,'tracked':subprocess.run(['git','-C',str(CLONE),'ls-files','--error-unmatch',path],env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0}
 if present:
  v['sha256']=sha(p.read_bytes())
  if p.suffix=='.ttl':
   g=rdflib.Graph().parse(p);v['rdf_triples']=len(g);v['owl_import_iris']=sorted(str(x) for x in g.objects(None,rdflib.OWL.imports))
 inputs.append(v)
deps={'runtime':{'python':sys.executable,'python_version':sys.version,'rdflib_version':rdflib.__version__,'rdflib_path':rdflib.__file__,'openpyxl_version':openpyxl.__version__,'openpyxl_path':openpyxl.__file__,'coms_path':coms.__file__},'declared_mapping_inputs':inputs,'missing_declared_mapping_inputs':[x['path'] for x in inputs if not x['present'] or not x['tracked']],'scope_note':'Declared current local source files, CCO dependency, workbook and source query verified. Remote/transitive imports are not independently fetched or repaired. Test-fixture evidence failures must be distinguished from absent pinned sources. Runtime COMS is the existing installed sibling-repository dependency.'}
(OUT/'dependency-inventory.json').write_text(json.dumps(deps,indent=2)+'\n')
assert not deps['missing_declared_mapping_inputs'],deps
print(json.dumps({'status':'canonical_make_check_started','clone':str(CLONE),'verified_clean_head':head,'raw_log':str(OUT/'make-check.log'),'declared_inputs_present':len(inputs)}),flush=True)
start=time.monotonic()
with (OUT/'make-check.log').open('wb') as f:
 proc=subprocess.run(['make','check'],cwd=CLONE,env=ENV,stdout=f,stderr=subprocess.STDOUT)
elapsed=time.monotonic()-start
raw=(OUT/'make-check.log').read_bytes();text=raw.decode('utf-8',errors='replace')
result={'command':['make','check'],'cwd':str(CLONE),'return_code':proc.returncode,'elapsed_seconds':elapsed,'test_summary':re.findall(r'^Ran \d+ tests? in [^\n]+',text,re.M),'outcome_summary':re.findall(r'^(?:OK|FAILED[^\n]*)$',text,re.M),'log':str(OUT/'make-check.log'),'log_sha256':sha(raw)}
(OUT/'make-check-result.json').write_text(json.dumps(result,indent=2)+'\n')
meta['status_after']=git('status','--porcelain=v1','--untracked-files=all');meta['head_after']=git('rev-parse','HEAD').strip()
(OUT/'clone-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
pattern=re.compile(r'^={70}\n(?P<kind>ERROR|FAIL): (?P<test>[^\n]+)\n-{70}\n(?P<body>.*?)(?=^={70}\n|^-{70}\nRan \d+ tests? in |\Z)',re.M|re.S)
failures=[]
for m in pattern.finditer(text):
 body=m.group('body').rstrip('\n')
 failures.append({'kind':m.group('kind'),'test':m.group('test'),'raw_traceback':body,'log_start_line':text[:m.start()].count('\n')+1,'log_end_line':text[:m.end()].count('\n')+1,'exception_or_final_message':next((line for line in reversed(body.splitlines()) if line.strip()),''),'raw_block_sha256':sha(m.group(0).encode())})
executed=[{'name':name,'outcome':outcome} for name,outcome in re.findall(r'^([^\n]+): (PASS|FAIL(?: \(\d+\))?)$',text,re.M) if not name.startswith('-') and name!='Validation suite']
inv={'baseline':BASE,'clone_metadata':meta,'canonical_result':result,'canonical_gate_passed':proc.returncode==0,'gate_statement':'make check was executed and '+('passed.' if proc.returncode==0 else 'did not pass. No exception is granted by this report.'),'failures':failures,'failure_block_counts':{k:sum(x['kind']==k for x in failures) for k in ('FAIL','ERROR')},'executed_gate_steps':executed,'dependency_inventory':str(OUT/'dependency-inventory.json'),'raw_log':str(OUT/'make-check.log'),'raw_log_sha256':sha(raw),'parser_provenance':'Same traceback-block parsing as Batch1 baseline/extract-failure-inventory.py; adapted only to this baseline/output directory and no redundant focused suites.','scope':'No repository, mapping, validator, test, or evidence repairs. No user-excluded files copied. All raw output preserved.'}
if 'Current publication assessment regression tests: FAIL' in text and len(executed)==2:
 inv['stages_not_reached']='All conditional validation stages after the current_* regression suite, Makefile compile prerequisite and final check recipe. Default smoke/ELK/HermiT report destinations printed in the summary are not evidence of those stages executing.'
 inv['shared_output_boundary']='Run stopped before default /tmp/ssn-to-bfo-validation-suite report-writing stages.'
else:
 inv['stages_not_reached']='Inspect executed_gate_steps and the raw canonical log before determining subsequent skipped stages.'
(OUT/'failure-inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
print(json.dumps({'status':'canonical_make_check_completed','result':result,'failure_block_counts':inv['failure_block_counts'],'status_after':meta['status_after'],'head_after':meta['head_after']}),flush=True)
