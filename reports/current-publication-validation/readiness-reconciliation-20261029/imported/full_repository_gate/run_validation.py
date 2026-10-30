"""Create-once external receipts for this diagnostic continuation; stop on first failure."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO')
sys.path.insert(0, str(ROOT / 'tools'))
import current_publication_readiness as readiness

COMMANDS = {'isolated_builder': ['python',
                      '-B',
                      '-m',
                      'unittest',
                      '-v',
                      'tests.test_sosa_2023_release_runtime.Sosa2023ReleaseRuntimeTests.test_current_builder_remains_byte_locked'],
 'focused_authority': ['python',
                       '-B',
                       '-m',
                       'unittest',
                       '-f',
                       '-v',
                       'tests.test_sosa_2023_release_runtime',
                       'tests.test_sosa_2023_release_manifest',
                       'tests.test_sosa_2023_release_archive',
                       'tests.test_sosa_2023_release_rehearsal'],
 'focused_custody': ['python',
                     '-B',
                     '-m',
                     'unittest',
                     '-f',
                     '-v',
                     'tests.test_current_semantic_validation',
                     'tests.test_current_semantic_invocation',
                     'tests.test_current_semantic_schema',
                     'tests.test_current_semantic_retry',
                     'tests.test_current_portable_execution_evidence',
                     'tests.test_current_retained_evidence',
                     'tests.test_current_retained_evidence_integration'],
 'focused_current_builders': ['python',
                              '-B',
                              '-m',
                              'unittest',
                              '-f',
                              '-v',
                              'tests.test_release_contract',
                              'tests.test_build_release',
                              'tests.test_release_archive',
                              'tests.test_release_rehearsal'],
 'focused_sosa_builder': ['python', '-B', '-m', 'unittest', '-f', '-v', 'tests.test_sosa_2023_build_release'],
 'focused_sosa_status': ['python',
                         '-B',
                         '-m',
                         'unittest',
                         '-f',
                         '-v',
                         'tests.test_sosa_2023_mapping_status',
                         'tests.test_current_cross_track_preservation'],
 'live_preservation': ['python', '-B', 'tools/current_publication_preservation.py'],
 'canonical_make_check': ['make', 'check'],
 'separate_compile': ['make', 'compile'],
 'fresh_readiness': ['python', '-B', 'tools/current_publication_readiness.py']}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def head(): return subprocess.check_output(['git','--no-optional-locks','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def inputs(): return {p:sha(ROOT/p) for p in sorted(readiness.validation_inputs(ROOT))}
def write_new(path, obj):
 with path.open('x') as stream: json.dump(obj,stream,indent=2,sort_keys=True); stream.write('\n')

def main():
 if (OUT/'STOP.json').exists(): raise RuntimeError('Validation already stopped at first failure')
 name=sys.argv[1]; command=list(COMMANDS[name]); log=OUT/(name+'.log'); receipt=OUT/(name+'.command.json')
 if log.exists() or receipt.exists(): raise RuntimeError('Refusing to overwrite execution')
 command[0]=sys.executable if command[0]=='python' else shutil.which(command[0])
 before_head=head(); before_inputs=inputs(); own_sha=sha(__file__)
 started=datetime.now(timezone.utc).isoformat(); timer=time.monotonic()
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
 env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
 print(json.dumps({'started':name,'command':command,'log':str(log)}),flush=True)
 with log.open('xb') as stream:
  result=subprocess.run(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
 after_head=head(); after_inputs=inputs()
 drift=sorted(p for p in before_inputs.keys()|after_inputs.keys() if before_inputs.get(p)!=after_inputs.get(p))
 document={'name':name,'command':command,'cwd':str(ROOT),'started_at_utc':started,
 'completed_at_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-timer,
 'returncode':result.returncode,'head_before':before_head,'head_after':after_head,
 'input_sha256_before':before_inputs,'input_sha256_after':after_inputs,'input_drift':drift,
 'log':str(log),'log_sha256':sha(log),'recorder':{'path':str(Path(__file__)),'sha256':own_sha},
 'executable':{'path':str(Path(command[0]).resolve()),'sha256':sha(Path(command[0]).resolve())},
 'scope':'External actual execution record; does not replace historical receipts or grant checkpoint/readiness authority.'}
 errors=[]
 if drift: errors.append('validation input drift')
 if before_head!=after_head: errors.append('HEAD changed')
 if sha(__file__)!=own_sha: errors.append('recorder changed')
 document['integrity_errors']=errors
 write_new(receipt,document)
 failed=result.returncode!=0 or errors
 if failed:
  write_new(OUT/'STOP.json',{'first_failure':name,'returncode':result.returncode,'integrity_errors':errors,'receipt':str(receipt)})
 print(json.dumps({'completed':name,'returncode':result.returncode,'integrity_errors':errors,'elapsed_seconds':document['elapsed_seconds']}),flush=True)
 return result.returncode or (1 if errors else 0)
if __name__=='__main__': raise SystemExit(main())
