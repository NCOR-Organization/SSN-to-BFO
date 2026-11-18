from pathlib import Path
import sys,json,hashlib
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root/'tests'));sys.path.insert(0,str(root/'tools'))
import test_strict_bfo_mapping as t
t.StrictBfoMappingTests.setUpClass()
try:
 result={'root':str(root),'strict_rows':{v.row_id:{'axiom_id':v.axiom_id,'canonical_input':str(v.canonical_input)} for v in t.StrictBfoMappingTests.strict_selected},'expected_row_ids':sorted(t.EXPECTED_ROW_IDS),'expected_axiom_ids':sorted(t.EXPECTED_AXIOM_IDS),'strict_product_sha256':hashlib.sha256((root/'releases/current-ssn-sosa/ssn-sosa-bfo-mapping.ttl').read_bytes()).hexdigest(),'evidence_note':'Read unchanged test setup and fixed identity locks. No fixture modification.'}
finally:t.StrictBfoMappingTests.doClassCleanups()
print(json.dumps(result,indent=2))
