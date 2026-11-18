"""Classify exact observed diagnostic differences; no gate/fixture changes."""
from pathlib import Path
import ast,collections,difflib,hashlib,json
OUT=Path(__file__).resolve().parent
r=json.loads((OUT/'canonical-gate-comparison.raw.json').read_text());b=json.loads((OUT/'baseline/failure-inventory.json').read_text());c=json.loads((OUT/'candidate-gate/failure-inventory.json').read_text())
BR=Path(b['canonical_result']['cwd']);CR=Path(c['canonical_result']['cwd']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roots=sorted({str(BR),str(CR),'/private'+str(BR),'/private'+str(CR)},key=len,reverse=True)
def norm(s):
 for p in roots:s=s.replace(p,'<CHECKOUT>')
 return s
bm={(v['kind'],v['test']):v for v in b['failures']};cm={(v['kind'],v['test']):v for v in c['failures']}
assert set(bm)==set(cm),{'new':list(set(cm)-set(bm)),'resolved':list(set(bm)-set(cm))}
transition_path='reports/current-semantic-workbook/transitions/9f891d92-ae02-4a2d-872b-7e4fc3468cf7.json';tr=json.loads((CR/transition_path).read_text())
workbook_pair=(tr['old_workbook_sha256'],tr['new_workbook_sha256']);projection_pair=(tr['old_semantic_projection_sha256'],tr['new_semantic_projection_sha256']);diff_path='reports/coms-vs-pre-coms-legacy-diff.md';diff_pair=(sha(BR/diff_path),sha(CR/diff_path))
assert sha(BR/'mappings/SSN2BFO-COMS.xlsx')==workbook_pair[0] and sha(CR/'mappings/SSN2BFO-COMS.xlsx')==workbook_pair[1]
report_diff=''.join(difflib.unified_diff((BR/diff_path).read_text().splitlines(True),(CR/diff_path).read_text().splitlines(True),fromfile='baseline',tofile='candidate'))
input_delta=None
for case in r['cases']:
 key=(case['kind'],case['test']);bt=norm(bm[key]['raw_traceback']);ct=norm(cm[key]['raw_traceback']);name=case['test'].split(' ',1)[0]
 if bt==ct:
  case.update(classification='Identical preexisting failure',explanation='Complete traceback equality after exact checkout-root substitution only.');continue
 pair=None;explanation=None
 if name in {'test_a_exact_original_workbook_preserves_sufficiency','test_b_authenticated_d_only_transition_preserves_sufficiency'}:
  pair=workbook_pair;explanation='Both runs compare immutable inheritance-sufficiency evidence with the current workbook and stop at the same stale historical hash expectation. Only the actual workbook hash changes according to the approved Platform transition; later assertions are not reached.'
 elif name=='test_maintained_live_workbook_resolves_to_immutable_decision_snapshot':
  pair=projection_pair;explanation='Both runs fail the same hardcoded historical semantic-projection hash. Candidate projection changes only according to the authenticated Platform semantic transition; immutable history and applicability checks precede this failure.'
 elif name=='test_four_documentary_bindings_retain_exact_history_and_live_report':
  pair=diff_pair;explanation='Both runs fail the same obsolete generated legacy-comparison report hash. Exact report diff adds only the approved Platform expression difference and adjusts corresponding common/removed/added totals; no other mapping difference is introduced.'
 if pair:
  assert pair[0] in bt and bt.replace(pair[0],pair[1])==ct,(name,case['normalized_diff'])
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation=explanation,approved_hash_change={'baseline':pair[0],'candidate':pair[1]});continue
 if name=='test_queue_complete_and_rationales_separate_documentation_from_approval':
  assert bt.replace('AssertionError: 68 != 69','AssertionError: 67 != 69')==ct
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation='The unchanged queue test expects 69 unresolved terms. The baseline already has 68; approved Platform finalization leaves 67. Both stop at this same stale count assertion; later alternative-count and final-summary assertions remain masked.');continue
 if name=='test_live_assessment_summary_matches_actual_records':
  assert '(23, 0, 68, 68, 16, 5, 2)' in bt and '(24, 0, 67, 67, 17, 5, 2)' in ct
  expected=bt.replace('(23, 0, 68, 68, 16, 5, 2)','(24, 0, 67, 67, 17, 5, 2)').replace('\n23\n','\n24\n')
  assert expected==ct,(name,case['normalized_diff'])
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation='The same unchanged policy prose reports 17 final / 74 unreviewed / 10 formal mappings. Expected live counts change from 23/68/16 to 24/67/17 through the sole authorized Platform finalization. No stale policy prose was repaired.');continue
 if name=='test_whole_suite_inputs_bind_retained_and_nested_decision_dependencies':
  def parse(s):
   line=next(x for x in s.splitlines() if x.startswith('AssertionError: '));a,z=line[len('AssertionError: '):].split(' not found in ',1);return ast.literal_eval(a),ast.literal_eval(z),s.replace(line,'<SET_ASSERTION>')
  missing_b,set_b,prefix_b=parse(bt);missing_c,set_c,prefix_c=parse(ct);assert missing_b==missing_c and prefix_b==prefix_c
  added=sorted(set_c-set_b);removed=sorted(set_b-set_c);assert not removed and len(added)==7,(added,removed)
  overlay=json.loads((OUT/'candidate-gate-clone.json').read_text())['overlay_hashes'];assert all(x in overlay for x in added)
  input_delta={'missing_member':missing_b,'baseline_count':len(set_b),'candidate_count':len(set_c),'added':added,'removed':removed,'missing_member_exists_in_both_checkouts':(BR/missing_b).is_file() and (CR/missing_c).is_file()}
  case.update(classification='Changed diagnostic attributable to approved data; preexisting failing case',explanation='The same historical sampling assessment-before dependency is absent from both computed whole-suite input sets, although its file exists in both checkouts. Parsed complete sets add exactly 7 Platform decision/transition/snapshot inputs and remove none. Python set display order is immaterial; no missing-dependency repair is claimed.',approved_input_set_delta=input_delta);continue
 raise AssertionError('Unaccounted diagnostic change: '+name+'\n'+case['normalized_diff'])
counts=collections.Counter(x['classification'] for x in r['cases'])
r.update(status='CANONICAL MAKE CHECK DID NOT PASS; ALL DIAGNOSTICS ACCOUNTED FOR',classification_counts=dict(counts),newly_failing_cases=[],resolved_failing_cases=[],demonstrated_unexplained_regressions=[],approved_data_evidence={'transition':{'path':transition_path,'sha256':sha(CR/transition_path)},'workbook':{'baseline':workbook_pair[0],'candidate':workbook_pair[1]},'projection':{'baseline':projection_pair[0],'candidate':projection_pair[1]},'legacy_report':{'path':diff_path,'baseline':diff_pair[0],'candidate':diff_pair[1],'exact_diff':report_diff},'whole_suite_input_delta':input_delta},normalization_policy='Only exact checkout roots and their macOS private aliases are substituted. No hash/count/transition content is normalized away. All 7 substantive differences are individually proved against approved workbook/assessment/transition/generated-report inputs. Complete printed input sets are parsed and compared independently of display order.',baseline_reused=False,both_runs_fresh_at_expected_baseline=True,stage_boundary_evidence='canonical-stage-boundary.json',gate_caveat='make check was freshly executed on both baseline and candidate and did not pass. No gate, hook, or release waiver is granted by this comparison. No validators, tests, historical evidence or mappings were repaired by the comparison.')
assert r['candidate_input_files_changed_during_gate']==[]
(OUT/'canonical-gate-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['baseline_failure_counts','candidate_failure_counts','classification_counts','newly_failing_cases','demonstrated_unexplained_regressions']},indent=2))
