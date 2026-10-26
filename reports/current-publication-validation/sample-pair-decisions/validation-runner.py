"""Retain fresh, input-bound checks for the two approved Sample decisions only.
This ledger supplements, and never replaces, the historical full-gate ledger.
"""
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'))
import current_publication_readiness as readiness
PYTHON=str(Path(sys.executable).resolve())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def inputs():
    paths=readiness.validation_inputs(ROOT)
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'reports/current-human-decisions/2026-10-25-sample-pair').iterdir() if p.is_file())
    paths.update(str(p.relative_to(ROOT)) for p in ROOT.glob('reports/current-ssn-sosa-*.json'))
    paths.add(str(Path(__file__).relative_to(ROOT)))
    return {p:sha(ROOT/p) for p in sorted(paths)}
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def run(spec):
    name,args,expected=spec
    command=[PYTHON,'-B',*args] if args[0]!='git' else args
    head=git('rev-parse','HEAD'); before=inputs(); start=now(); log=OUT/(name+'.log')
    with log.open('w') as stream:
        result=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=stream,stderr=subprocess.STDOUT)
    after=inputs(); path=str(log.relative_to(ROOT)); tool=Path(command[0]) if Path(command[0]).is_absolute() else Path(__import__('shutil').which(command[0])).resolve()
    entry={'name':name,'command':command,'head':head,'expected_head':'c3f9b05593727bd13854bf1830cc09b4a653b41f','final_head':git('rev-parse','HEAD'),
        'expected_input_sha256':before,'input_sha256':before,'input_sha256_after':after,'input_drift':[p for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)],
        'started_at_utc':start,'completed_at_utc':now(),'execution_status':'completed','returncode':result.returncode,'expected_returncode':expected,
        'tool_identity':{'path':str(tool.resolve()),'sha256':sha(tool)},'log':path,'log_sha256':sha(log),'result_artifacts':{path:sha(log)}}
    entry['passed_as_expected']=entry['returncode']==expected and not entry['input_drift'] and entry['head']==entry['expected_head']==entry['final_head']
    (OUT/(name+'-command.json')).write_text(json.dumps(entry,indent=2,sort_keys=True)+'\n')
    print(name, 'PASS' if entry['passed_as_expected'] else 'FAIL', 'exit',result.returncode,flush=True)
    return entry
focused=['tests.test_current_assessment','tests.test_current_identity_reporting','tests.test_current_publication_preservation','tests.test_current_publication_readiness','tests.test_current_semantic_invocation','tests.test_current_semantic_validation','tests.test_current_source_identity','tests.test_current_semantic_schema','tests.test_current_semantic_retry']
sosa=['tests.test_check_sosa_next_mapping','tests.test_sosa_2023_mapping_status','tests.test_sosa_2023_publication_metadata','tests.test_sosa_2023_release_rendering','tests.test_sosa_2023_ro_mapping','tests.test_sosa_2023_ro_source_version','tests.test_sosa_next_products','tests.test_sosa_source_version']
checks=[
 ('focused-publication-tests',['-m','unittest','-v',*focused],0),
 ('coms-integration-tests',['-m','unittest','-v','tests.test_coms_framework_integration','tests.test_coms_row_identity','tests.test_generate_mapping_from_coms'],0),
 ('sosa-2023-nonregression-tests',['-m','unittest','-v',*sosa],0),
 ('assessment',['tools/current_assessment.py'],0),
 ('source_identity',['tools/current_source_identity.py'],0),
 ('generation_freshness',['tools/check_coms_mapping.py','--check-only'],0),
 ('preservation',['tools/current_publication_preservation.py'],0),
 ('historical-semantic-custody',['tools/current_semantic_validation.py','--read-historical'],0),
 ('all-final-gate',['tools/current_assessment.py','--require-final'],1),
 ('publication-readiness',['tools/current_publication_readiness.py'],1),
 ('static-compilation',['-c',"from pathlib import Path; paths=sorted(p for p in Path('.').rglob('*.py') if not any(x in p.parts for x in ('.git','.cache','__pycache__'))); [compile(p.read_bytes(),str(p),'exec') for p in paths]; print(f'PASS: compiled {len(paths)} Python files in memory')"],0),
 ('git-diff-check',['git','diff','--check'],0),
]
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool: results=list(pool.map(run,checks))
    ledger={'schema_version':1,'scope':'Sample-pair decision milestone checks; not a replacement or re-certification of the historical full repository gate. Nonzero all-final/readiness gates are expected remaining blockers.','commands':results,'all_passed_as_expected':all(r['passed_as_expected'] for r in results)}
    (OUT/'commands.json').write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
    raise SystemExit(0 if ledger['all_passed_as_expected'] else 1)
