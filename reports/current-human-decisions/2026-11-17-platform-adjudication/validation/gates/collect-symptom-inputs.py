from pathlib import Path
import sys,json,hashlib
root=Path(sys.argv[1]).resolve(); sys.path.insert(0,str(root/'tests'));sys.path.insert(0,str(root/'tools'))
import test_modular_products as t
t.ModularProductTests.setUpClass()
try:
 result={'root':str(root),'actual_alignment_row_ids':sorted(x.row_id for x in t.ModularProductTests.selected),'expected_alignment_row_ids':sorted(t.EXPECTED_ROW_IDS),'actual_alignment_axiom_ids':sorted(x.axiom_id for x in t.ModularProductTests.selected),'expected_alignment_axiom_ids':sorted(t.EXPECTED_AXIOM_IDS),'evidence_note':'Read via unchanged test setup and constants to distinguish nondeterministic truncated set displays from substantive set changes.'}
finally:t.ModularProductTests.doClassCleanups()
print(json.dumps(result,indent=2))
