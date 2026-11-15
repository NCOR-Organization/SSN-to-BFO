#!/usr/bin/env python3
"""Bounded exact candidate validation using existing COMS and HermiT APIs.
Writes only under --output. Does not install, alter governance, or normalize axioms.
"""
import argparse, dataclasses, hashlib, json, os, sys
from pathlib import Path
ROOT=Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO')
sys.path.insert(0,str(ROOT/'tools'))
from rdflib import Graph,Namespace,RDF,RDFS,OWL
from rdflib.compare import isomorphic
import current_semantic_generation as generation
import generate_mapping_from_coms as mapping
import current_semantic_validation as semantic

S=Namespace('http://www.w3.org/ns/sosa/')
N=Namespace('http://www.w3.org/ns/ssn/')
C=Namespace('https://www.commoncoreontologies.org/')
E=Namespace('urn:observed-property-adjudication-probe:')
EXPECTED={(S.observedProperty,RDFS.domain,S.Observation),(S.observedProperty,RDFS.range,S.ObservableProperty)}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,default=str)+'\n')
def check(ok,msg):
    if not ok:raise AssertionError(msg)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workbook',type=Path,required=True)
    parser.add_argument('--baseline-workbook',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    evidence=out/'entailment'; evidence.mkdir()
    before,previous=generation._snapshot(ROOT,args.baseline_workbook)
    after,products=generation._snapshot(ROOT,args.workbook)
    save(out/'generation-snapshots.json',{'before':before,'after':after})
    check(after['counts']['GOVERNED_ROW_COUNT']==108,'Expected108 rows')
    check(after['counts']['AUTHORITATIVE_AXIOM_COUNT']==102,'Expected102 OWL assertions')
    check(after['counts']['ZERO_AXIOM_ROW_COUNT']==6,'Expected6 blanks')
    product_paths={}
    diffs=[]
    for key,data in products.items():
        path=out/(key+'.ttl');path.write_bytes(data);product_paths[key]=path
        old=Graph().parse(data=previous[key].decode(),format='turtle')
        new=Graph().parse(data=data.decode(),format='turtle')
        expected=Graph()
        for t in old:expected.add(t)
        if key in ('integrated','alignment_core'):
            for t in EXPECTED:
                check(t not in old,f'{key}: typing axiom unexpectedly already present')
                expected.add(t)
            check(isomorphic(new,expected),f'{key}: unexpected logical/product delta')
        else:check(previous[key]==data,f'{key}: unexpected byte change')
        check(not list(new.objects(S.observedProperty,RDFS.subPropertyOf)),f'{key}: unexpected observedProperty superproperty')
        diffs.append({'product':key,'path':str(path),'before_sha256':hashlib.sha256(previous[key]).hexdigest(),'after_sha256':sha(path),'before_triples':len(old),'after_triples':len(new),'only_approved_typing_delta':True})
    # Independent render, not a cached result, must be byte identical.
    _,again=generation._snapshot_uncached(ROOT,args.workbook)
    check(again==products,'Candidate generation is not deterministic')
    save(out/'product-deltas.json',diffs)
    print('Exact approved axiom delta and deterministic candidate rendering: PASS',flush=True)
    runners={
        'integrated':lambda:mapping.run_candidate_hermit(product_paths['integrated'],out/'integrated-validation'),
        'alignment_core':lambda:mapping.run_alignment_core_hermit(product_paths['alignment_core'],out/'core-validation'),
        'strict_bfo_mapping':lambda:mapping.run_strict_bfo_hermit(product_paths['strict_bfo_mapping'],product_paths['alignment_core'],out/'strict-validation'),
        'cco_extension':lambda:mapping.run_cco_extension_hermit(product_paths['cco_extension'],product_paths['strict_bfo_mapping'],product_paths['alignment_core'],out/'cco-validation'),
    }
    results={}
    for key,run in runners.items():
        result=run();record=dataclasses.asdict(result);record['passed']=result.passed
        results[key]=record;save(out/(key+'-validation-result.json'),record)
        print(key+': '+('PASS' if result.passed else 'FAIL')+', named unsatisfiable classes='+str(result.owl_nothing_count),flush=True)
        check(result.passed,f'{key}: profile/HermiT failure; see retained result')
    graph=Graph().parse(results['integrated']['profile_graph_path'],format='turtle')
    # First assertion is entirely untyped. The second probe separately tests FOI correlation.
    graph.add((E.o,S.observedProperty,E.p))
    graph.add((E.o2,S.observedProperty,E.p2))
    graph.add((E.o2,S.hasFeatureOfInterest,E.feature))
    queries=[]
    def q(identifier,kind,s,o,expected,predicate=None):
        value={'id':identifier,'kind':kind,'subject':str(s),'object':str(o),'expected_entailed':expected}
        if predicate is not None:value['predicate']=str(predicate)
        queries.append(value)
    q('domain-classifies-untyped-subject','class_assertion',E.o,S.Observation,True)
    q('range-classifies-untyped-object','class_assertion',E.p,S.ObservableProperty,True)
    q('no-has-input-superproperty','object_property_subsumption',S.observedProperty,C.ont00001921,False)
    q('no-has-input-edge','object_property_assertion',E.o,E.p,False,C.ont00001921)
    q('same-feature-property-not-established','object_property_assertion',E.p2,E.feature,False,N.isPropertyOf)
    q('same-feature-inverse-not-established','object_property_assertion',E.feature,E.p2,False,N.hasProperty)
    for term in (S.Observation,S.ObservableProperty,S.Sensor,N.Stimulus):
        q(str(term).rsplit('/',1)[-1]+'-satisfiable','class_subsumption',term,OWL.Nothing,False)
    q('Observation-PlannedAct-preserved','class_subsumption',S.Observation,C.ont00000228,True)
    q('sensor-agent-preserved','object_property_subsumption',S.madeBySensor,C.ont00001833,True)
    q('inverse-sensor-agent-preserved','object_property_subsumption',S.madeObservation,C.ont00001787,True)
    save(out/'queries.json',queries)
    closure={'inputs':[semantic.fingerprint(ROOT/p) for p in mapping.CANDIDATE_CLOSURE_INPUTS]+[semantic.fingerprint(product_paths['integrated'])],
        'unresolved_imports':[],'closure_policy':'Existing generator exact available pinned-local closure, with only its established metadata declaration completion; no logical axiom removed. ABox probes added for focused entailment tests, not a publication execution slot.',
        'removed_logical_axioms':0,'profile_declaration_completion_count':results['integrated']['profile_declaration_completion_count'],
        'probe_triples':3,'triples':len(graph)}
    toolchain=semantic.build_helper(evidence,out/'java')
    check(toolchain['status']=='ready','Existing pinned Java helper did not build')
    result=semantic.run_graph(graph,closure,'observedproperty-typing',evidence,out/'java',toolchain,queries=queries,timeout=120)
    payload=result.get('reasoner_result',{})
    check(result.get('status')=='consistent',f'Entailment fixture failed: {result.get("status")}')
    check(payload.get('owl2_dl_profile') is True,'Entailment fixture OWL 2 DL failure')
    check(len(payload.get('expectations',[]))==len(queries),'Incomplete entailment answers')
    check(all(x['passed'] for x in payload['expectations']),'Unexpected entailment result')
    summary={'status':'PASS','workbook_sha256':sha(args.workbook),'baseline_workbook_sha256':sha(args.baseline_workbook),
        'owl2_dl':'PASS all four products','hermit':'PASS all four products','named_unsatisfiable_classes':{k:v['owl_nothing_count'] for k,v in results.items()},
        'entailment_tests':payload['expectations'],'deterministic_generation':True,'product_deltas':diffs,
        'counts':{k:after['counts'][k] for k in ('GOVERNED_ROW_COUNT','AUTHORITATIVE_AXIOM_COUNT','ZERO_AXIOM_ROW_COUNT')}}
    save(out/'summary.json',summary)
    print('All '+str(len(queries))+' focused HermiT entailment checks PASS',flush=True)
    print(json.dumps(summary,default=str),flush=True)

if __name__=='__main__':main()
