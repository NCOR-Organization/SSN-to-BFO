#!/usr/bin/env python3
"""Run one distinct-ICE-Platforms ABox through the existing pinned local API.
python run_probe.py --root /path/to/checkout --output /tmp/new-external-dir
No retained ontology snapshot; all repository inputs are read-only.
"""
import argparse, hashlib, json, sys, tempfile
from pathlib import Path
from rdflib import Graph, OWL
HERE=Path(__file__).resolve().parent
EXPECTED_PRODUCT_SHA256='b78c7fde8d73c167ed2808947b4be2fdbdbe1ab8f9bb3a71c67725ccb6a89401'
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve();out=a.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
 sys.path.insert(0,str(root/'tools'));import generate_mapping_from_coms as mapping;import current_semantic_validation as semantic
 product=root/'SSN2BFO.ttl';assert semantic.sha256(product)==EXPECTED_PRODUCT_SHA256,'Not the exact approved final integrated product'
 graph=Graph()
 for path in mapping.CANDIDATE_CLOSURE_INPUTS:graph.parse(root/path,format='turtle')
 graph.parse(product,format='turtle')
 for t in list(graph.triples((None,OWL.imports,None))):graph.remove(t)
 for t in mapping.DL_PROFILE_DECLARATION_COMPLETION:graph.add(t)
 probe=HERE/'probe.ttl';graph.parse(probe,format='turtle')
 closure={'inputs':[semantic.fingerprint(root/x)for x in mapping.CANDIDATE_CLOSURE_INPUTS]+[semantic.fingerprint(product),semantic.fingerprint(probe)],'unresolved_imports':[],'closure_policy':'Established fixed pinned-local current-track closure and metadata declaration completion; one supplementary ABox with both distinct individuals typed Platform and ICE.'}
 with tempfile.TemporaryDirectory(prefix='ssn-distinct-ice-platforms-')as tmp:
  scratch=Path(tmp);helper=semantic.build_helper(scratch,scratch/'java');r=semantic.run_graph(graph,closure,'distinct-ice-platforms',scratch,scratch/'java',helper,timeout=180)
 (out/'result.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 passed=r['status']=='consistent'and r['reasoner_result']['owl2_dl_profile']
 summary={'status':'PASS'if passed else'FAIL','expected':'Two explicitly distinct ICE Platforms, outer hosts inner, are jointly consistent.','actual_consistency':r['status'],'owl2_dl_profile':r['reasoner_result']['owl2_dl_profile'],'integrated_product_sha256':semantic.sha256(product),'probe_sha256':semantic.sha256(probe),'driver_sha256':semantic.sha256(Path(__file__)),'pinned_dependency_sha256':{str(x):semantic.sha256(root/x)for x in mapping.CANDIDATE_CLOSURE_INPUTS},'asserted_distinctness':True,'both_individuals_explicitly_typed_platform_and_ice':True,'repository_files_modified':False,'no_other_tests_run':True}
 (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary),flush=True);assert passed
if __name__=='__main__':main()
