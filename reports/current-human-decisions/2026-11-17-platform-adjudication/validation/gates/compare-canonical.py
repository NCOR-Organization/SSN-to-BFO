from pathlib import Path
import ast, collections, difflib, hashlib, json, re
ROOT=Path(__file__).parent
B=json.loads((ROOT/'baseline/failure-inventory.json').read_text())
C=json.loads((ROOT/'candidate-gate/failure-inventory.json').read_text())
M=json.loads((ROOT/'candidate-gate/input-manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roots=[B['canonical_result']['cwd'],C['canonical_result']['cwd']]
roots+=['/private'+p for p in roots if p.startswith(('/tmp/','/var/'))]
roots=sorted(set(roots),key=len,reverse=True)
def normalize(t):
 for p in roots:t=t.replace(p,'<CHECKOUT>')
 return t
bm={(x['kind'],x['test']):x for x in B['failures']};cm={(x['kind'],x['test']):x for x in C['failures']}
assert len(bm)==len(B['failures']);assert len(cm)==len(C['failures'])
new=sorted(cm.keys()-bm.keys());resolved=sorted(bm.keys()-cm.keys());cases=[]
for key in sorted(bm.keys()|cm.keys()):
 b=bm.get(key);c=cm.get(key);bn=normalize(b['raw_traceback']) if b else '';cn=normalize(c['raw_traceback']) if c else ''
 v={'kind':key[0],'test':key[1],'baseline_failed':b is not None,'candidate_failed':c is not None,'baseline_log_line':b['log_start_line'] if b else None,'candidate_log_line':c['log_start_line'] if c else None,'baseline_raw_block_sha256':b['raw_block_sha256'] if b else None,'candidate_raw_block_sha256':c['raw_block_sha256'] if c else None,'normalized_tracebacks_identical':bool(b and c and bn==cn),'normalized_diff':''.join(difflib.unified_diff([line+'\n' for line in bn.splitlines()],[line+'\n' for line in cn.splitlines()],fromfile='baseline',tofile='candidate'))}
 if b and c and bn==cn:
  v.update(classification='Identical preexisting failure',explanation='Complete traceback equality after exact checkout-root normalization only.')
 else:v.update(classification='Pending bounded cause review',explanation='Do not infer regression or approved-data exception from failure name alone.')
 cases.append(v)
files_changed=[]
for path,h in M['input_files'].items():
 p=Path(M['root'])/path
 now=sha(p) if p.is_file() else None
 if now!=h:files_changed.append({'path':path,'before':h,'after':now})
report={'status':'CANONICAL MAKE CHECK DID NOT PASS; DIFFERENCE REVIEW PENDING','baseline_commit':B['baseline'],'baseline_result':B['canonical_result'],'candidate_result':C['canonical_result'],'baseline_failure_counts':B['failure_block_counts'],'candidate_failure_counts':C['failure_block_counts'],'new_failing_cases':[{'kind':x[0],'test':x[1]} for x in new],'resolved_failing_cases':[{'kind':x[0],'test':x[1]} for x in resolved],'matched_failure_case_count':len(bm.keys()&cm.keys()),'exact_normalized_traceback_matches':sum(x['normalized_tracebacks_identical'] for x in cases),'normalization_policy':'Only the two exact checkout roots and their macOS /private aliases are replaced. No hashes, counts, transition IDs, exceptions, messages, set contents or other data are suppressed.','baseline_input_state':B['clone_metadata'],'candidate_input_manifest':str(ROOT/'candidate-gate/input-manifest.json'),'candidate_input_manifest_sha256':sha(ROOT/'candidate-gate/input-manifest.json'),'candidate_input_files_changed_during_gate':files_changed,'raw_logs':{'baseline':{'path':str(ROOT/'baseline/make-check.log'),'sha256':sha(ROOT/'baseline/make-check.log')},'candidate':{'path':str(ROOT/'candidate-gate/make-check.log'),'sha256':sha(ROOT/'candidate-gate/make-check.log')}},'executed_stages':{'baseline':B['executed_gate_steps'],'candidate':C['executed_gate_steps']},'stages_not_reached':'Both stop in the current_* unittest suite if their executed_stages show only Turtle parse and current publication assessment regression tests. All later conditional validation stages, the Makefile compile prerequisite and the final check recipe are not reached. Printed default report destinations do not establish execution.','gate_caveat':'make check was executed and did not pass. No waiver is created by this analysis. No tests, validators, mappings, assessments or authentication requirements were changed by the comparison.','cases':cases}
(ROOT/'canonical-gate-comparison.raw.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['baseline_failure_counts','candidate_failure_counts','new_failing_cases','resolved_failing_cases','matched_failure_case_count','exact_normalized_traceback_matches','candidate_input_files_changed_during_gate']},indent=2))
for v in cases:
 if v['classification']=='Pending bounded cause review':print('\n'+v['test']+'\n'+v['normalized_diff'][:5000])
