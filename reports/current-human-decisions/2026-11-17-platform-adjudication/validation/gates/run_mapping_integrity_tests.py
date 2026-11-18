#!/usr/bin/env python3
"""Run exactly the six requested existing test files; no modifications."""
import argparse,hashlib,json,os,sys,time,unittest
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);os.chdir(root)
files=['test_coms_row_identity.py','test_generate_mapping_from_coms.py','test_product_dispositions.py','test_modular_products.py','test_strict_bfo_mapping.py','test_cco_extension.py']
def hashes():return {f:hashlib.sha256((root/'tests'/f).read_bytes()).hexdigest() for f in files}
before=hashes();start=time.monotonic();suite=unittest.TestSuite();loader=unittest.TestLoader()
for f in files:suite.addTests(loader.discover(str(root/'tests'),pattern=f))
result=unittest.TextTestRunner(verbosity=2,buffer=False).run(suite)
summary={'root':str(root),'files':files,'test_files_sha256_before':before,'test_files_sha256_after':hashes(),'tests_run':result.testsRun,'failures':[{'test':test.id(),'traceback':trace} for test,trace in result.failures],'errors':[{'test':test.id(),'traceback':trace} for test,trace in result.errors],'skipped':[{'test':test.id(),'reason':why} for test,why in result.skipped],'unexpected_successes':[test.id() for test in result.unexpectedSuccesses],'expected_failures':[{'test':test.id(),'traceback':trace} for test,trace in result.expectedFailures],'passed':result.wasSuccessful(),'elapsed_seconds':time.monotonic()-start}
assert summary['test_files_sha256_after']==before
(out/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['root','tests_run','passed','elapsed_seconds']},indent=2),flush=True)
sys.exit(0 if result.wasSuccessful() else 1)
