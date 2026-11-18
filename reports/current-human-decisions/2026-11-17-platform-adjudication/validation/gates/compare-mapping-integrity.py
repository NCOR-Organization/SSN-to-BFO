"""Bounded external baseline/candidate diagnosis; no repository writes."""
from pathlib import Path
import ast,collections,difflib,hashlib,json,os,subprocess
OUT=Path(__file__).resolve().parent
B=json.loads((OUT/'baseline-integrity/results.json').read_text());C=json.loads((OUT/'candidate-integrity/results.json').read_text())
SB=json.loads((OUT/'baseline-symptom-inputs.json').read_text());SC=json.loads((OUT/'candidate-symptom-inputs.json').read_text())
TB=json.loads((OUT/'baseline-strict-symptom.json').read_text());TC=json.loads((OUT/'candidate-strict-symptom.json').read_text())
root=Path(C['root']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roots=sorted({B['root'],C['root'],'/private'+B['root'],'/private'+C['root']},key=len,reverse=True)
def norm(s):
 for p in roots:s=s.replace(p,'<CHECKOUT>')
 return s
bm={(k,x['test']):x for k in ['failures','errors'] for x in B[k]};cm={(k,x['test']):x for k in ['failures','errors'] for x in C[k]}
assert B['test_files_sha256_before']==B['test_files_sha256_after']==C['test_files_sha256_before']==C['test_files_sha256_after']
platform='urn:uuid:b4508c03-1b79-4f53-b525-d5db6d80c7cb'
strict_changes={p:{'before':TB['strict_rows'].get(p),'after':TC['strict_rows'].get(p)} for p in TB['strict_rows'].keys()|TC['strict_rows'].keys() if TB['strict_rows'].get(p)!=TC['strict_rows'].get(p)}
assert set(strict_changes)=={platform};assert TB['strict_rows'].keys()==TC['strict_rows'].keys();assert TB['expected_axiom_ids']==TC['expected_axiom_ids']
assert {x['axiom_id'] for x in TB['strict_rows'].values()}==set(TB['expected_axiom_ids'])
assert SB['actual_alignment_row_ids']==SC['actual_alignment_row_ids'];assert SB['expected_alignment_row_ids']==SC['expected_alignment_row_ids']
product_delta=Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO/reports/current-human-decisions/2026-11-17-platform-adjudication/validation/focused/results-v3/product-deltas.json')
pd=next(x for x in json.loads(product_delta.read_text()) if x['product']=='strict_bfo_mapping')
assert pd['only_approved_axiom_replacement'] and pd['baseline_sha256']==TB['strict_product_sha256'] and pd['candidate_sha256']==TC['strict_product_sha256']
old_transition='bd69b546-6ef2-4704-8f05-325ec9bc1862';new_transition='9f891d92-ae02-4a2d-872b-7e4fc3468cf7'
cases=[]
for key in sorted(bm.keys()|cm.keys()):
 b=bm.get(key);c=cm.get(key);bt=norm(b['traceback']) if b else '';ct=norm(c['traceback']) if c else ''
 case={'test':key[1],'kind':key[0],'baseline_case_failed':b is not None,'candidate_case_failed':c is not None,'baseline_traceback':b['traceback'] if b else None,'candidate_traceback':c['traceback'] if c else None,'normalized_tracebacks_identical':bool(b and c and bt==ct),'normalized_diff':''.join(difflib.unified_diff(bt.splitlines(True),ct.splitlines(True),fromfile='baseline',tofile='candidate'))}
 if b and c and bt==ct:
  case.update(classification='Identical preexisting failure',explanation='Complete traceback equality after exact checkout-root substitution only.')
 elif b and c and key[1]=='test_modular_products.ModularProductTests.test_exact_selection_identity_lock_and_distribution':
  assert bt.split('AssertionError:')[0]==ct.split('AssertionError:')[0]
  case.update(classification='Identical preexisting failure; set display order only',explanation='Both complete selected and expected RowID sets were independently read through unchanged test setup and are exactly equal across baseline/candidate; only the abbreviated Python set display differs.',evidence=['baseline-symptom-inputs.json','candidate-symptom-inputs.json'])
 elif b and c and old_transition in bt and bt.replace(old_transition,new_transition)==ct:
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation='The test still requires transition58481ff2-4e56-4931-a3d4-383357b16561. Baseline has the approved Deployment transition; candidate has the approved Platform successor. No other traceback content changes.',approved_change={'baseline_transition':old_transition,'candidate_transition':new_transition})
 elif b and c and key[1]=='test_generate_mapping_from_coms.ComsAuthorityMigrationTests.test_current_generation_context_preserves_raw_baseline_and_exact_delta':
  assert bt.replace('AssertionError: 8 != 3','AssertionError: 9 != 3')==ct
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation='The cumulative historical-to-current removed-axiom inventory rises from8 to9 because the original Platform equivalence is replaced once. Both fail the same hardcoded expectation3. The authenticated Platform transition and focused product-delta proof establish exactly one newly replaced equivalence.')
 elif c and not b and key[1]=='test_strict_bfo_mapping.StrictBfoMappingTests.test_exact_selection_identity_lock_and_distribution':
  case.update(classification='Newly failing fixture attributable to approved mapping data',explanation='The unchanged fixed axiom-ID set still contains the old Platform axiom. Baseline matches that set; candidate replaces exactly Platform axiom 480ce325… with 863a5596…, with all 19 RowIDs and 18 other canonical inputs unchanged. This is an approved-expression consequence, not an unexplained mapping regression.',evidence=['baseline-strict-symptom.json','candidate-strict-symptom.json'])
 elif c and not b and key[1]=='test_strict_bfo_mapping.StrictBfoMappingTests.test_processed_row_and_audit_order_do_not_affect_strict_bfo_output':
  assert TC['strict_product_sha256'] in ct and TB['strict_product_sha256'] in ct
  case.update(classification='Newly failing fixture attributable to approved mapping data',explanation='All preceding row/axiom-order and byte-determinism comparisons pass. The final assertion hardcodes the old strict-BFO product SHA 676b3162…; the approved Platform replacement yields 2e29952e…. Focused graph-delta validation confines the product difference to this one approved equivalence.',source_location='tests/test_strict_bfo_mapping.py:527')
 elif c and not b and key[1]=='test_strict_bfo_mapping.RawStrictBfoGuardTests.test_current_context_preserves_baseline_strict_axioms_and_bytes':
  assert 'line 660' in ct and 'read_bytes(), baseline_bytes' in ct
  case.update(classification='Newly failing fixture attributable to approved mapping data',explanation='The test requires working-tree strict-BFO bytes to equal the unchanged HEAD version. The approved Platform mapping necessarily changes those bytes. The prior HEAD-hash assertion passes; the focused product-delta proof and both current/HEAD hashes establish only the authorized equivalence replacement.',source_location='tests/test_strict_bfo_mapping.py:660')
 else:case.update(classification='Inconclusive; requires review',explanation='This case is not covered by an exact verified baseline or approved-data comparison.')
 cases.append(case)
assert not any(x['classification'].startswith('Inconclusive') for x in cases),cases
module=ast.parse((root/'tests/test_cco_extension.py').read_text());cls=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name=='CcoExtensionTests');blocked=[n.name for n in cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
assert len(blocked)==11
snapshot=json.loads((OUT/'candidate-integrity-clone.json').read_text());changes=[p for p,h in snapshot['overlay_hashes'].items() if sha(root/p)!=h];assert not changes
out={'status':'MAPPING-INTEGRITY SUITES DID NOT PASS; ALL DIAGNOSTICS ACCOUNTED FOR','baseline':{'tests_run':B['tests_run'],'failures':len(B['failures']),'errors':len(B['errors']),'elapsed_seconds':B['elapsed_seconds'],'exit_code':1},'candidate':{'tests_run':C['tests_run'],'failures':len(C['failures']),'errors':len(C['errors']),'elapsed_seconds':C['elapsed_seconds'],'exit_code':1},'new_failing_cases':[k[1] for k in sorted(cm.keys()-bm.keys())],'resolved_failing_cases':[k[1] for k in sorted(bm.keys()-cm.keys())],'classification_counts':dict(collections.Counter(x['classification'] for x in cases)),'exact_normalized_traceback_matches':sum(x['normalized_tracebacks_identical'] for x in cases),'demonstrated_unexplained_regressions':[],'test_files_byte_identical':True,'candidate_snapshot_bytes_changed_during_run':changes,'strict_identity_delta':strict_changes,'strict_product_delta_evidence':{'path':product_delta.relative_to('/Users/alecsculley/Documents/GitHub/SSN-to-BFO').as_posix(),'sha256':sha(product_delta),'delta':pd},'blocked_tests':{'class':'test_cco_extension.CcoExtensionTests','count':len(blocked),'methods':blocked,'reason':'Same class setup failure on baseline/candidate: latest semantic transition differs from a hardcoded historical transition; these11methods did not execute and are not11additional failure records.'},'normalization_policy':'Only exact checkout roots and macOS private aliases. One abbreviated set-print difference is accepted only after comparing complete actual/expected sets. No hash, count, transition, exception, or semantic data suppressed.','raw_evidence':{p:sha(OUT/p) for p in ['baseline-integrity.log','candidate-integrity.log','baseline-integrity/results.json','candidate-integrity/results.json','baseline-symptom-inputs.json','candidate-symptom-inputs.json','baseline-strict-symptom.json','candidate-strict-symptom.json']},'cases':cases,'gate_caveat':'Neither mapping-integrity suites nor canonical gate is waived or represented as passing. The3newly surfaced approved-data fixtures were not edited; the authorization permitted only the assessment-count test correction.'}
(OUT/'mapping-integrity-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['baseline','candidate','classification_counts','new_failing_cases','demonstrated_unexplained_regressions']},indent=2))
