#!/usr/bin/env python3
"""Bounded Deployment diagnostic, reusing established current-track APIs.
All output is written only to the explicitly external --output directory.
This is an adjudication validation driver, not repository validation infrastructure.
"""
import argparse,dataclasses,hashlib,json,sys
from pathlib import Path
from rdflib import Graph,Namespace,RDF,RDFS,OWL,BNode,URIRef
from rdflib.collection import Collection
from rdflib.compare import isomorphic
HERE=Path(__file__).resolve().parent
N=Namespace('http://www.w3.org/ns/ssn/'); C=Namespace('https://www.commoncoreontologies.org/'); B=Namespace('http://purl.obolibrary.org/obo/')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,default=str)+'\n')
def check(v,message):
 if not v:raise AssertionError(message)
def expression(g,n):
 if isinstance(n,URIRef):return str(n)
 if (n,RDF.type,OWL.Restriction) in g:return {'some':str(g.value(n,OWL.onProperty)),'filler':str(g.value(n,OWL.someValuesFrom))}
 items=g.value(n,OWL.intersectionOf)
 check(items is not None,'Unexpected Deployment class expression')
 return {'and':[expression(g,x) for x in Collection(g,items)]}
def tree(g,root):
 seen=set();pending=[root]
 while pending:
  n=pending.pop()
  if n in seen:continue
  seen.add(n)
  pending.extend(o for p,o in g.predicate_objects(n) if isinstance(o,BNode))
 return set(t for n in seen for t in g.triples((n,None,None)))
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--workbook',type=Path,required=True);p.add_argument('--baseline-workbook',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=a.root.resolve();out=a.output.resolve();check(not out.is_relative_to(root),'Validation output must be external to repository');out.mkdir(parents=True,exist_ok=False)
 sys.path.insert(0,str(root/'tools'))
 import current_semantic_generation as generation
 import generate_mapping_from_coms as mapping
 import current_semantic_validation as semantic
 before,oldproducts=generation._snapshot(root,a.baseline_workbook)
 after,products=generation._snapshot(root,a.workbook)
 save(out/'generation-snapshots.json',{'baseline':before,'candidate':after})
 for k,n in [('GOVERNED_ROW_COUNT',108),('AUTHORITATIVE_AXIOM_COUNT',102),('ZERO_AXIOM_ROW_COUNT',6)]:check(before['counts'][k]==after['counts'][k]==n,'Unexpected inventory change: '+k)
 oldexpression={'and':[str(C.ont00000228),{'some':str(N.deployedSystem),'filler':str(N.System)},{'some':str(N.deployedOnPlatform),'filler':str(B.BFO_0000040)}]}
 newexpression={'and':oldexpression['and'][:2]}
 paths={};deltas=[]
 for phase,docs in [('baseline',oldproducts),('candidate',products)]:
  (out/phase).mkdir();paths[phase]={}
  for key,data in docs.items():
   path=out/phase/(key+'.ttl');path.write_bytes(data);paths[phase][key]=path
 for key,data in products.items():
  old=Graph().parse(data=oldproducts[key].decode(),format='turtle');new=Graph().parse(data=data.decode(),format='turtle')
  if key in ['integrated','cco_extension']:
   olds=list(old.objects(N.Deployment,OWL.equivalentClass));news=list(new.objects(N.Deployment,OWL.equivalentClass));check(len(olds)==len(news)==1,key+': incorrect equivalence count')
   check(expression(old,olds[0])==oldexpression,key+': unexpected baseline Deployment expression')
   check(expression(new,news[0])==newexpression,key+': unexpected candidate Deployment expression')
   expected=Graph()
   for t in old:expected.add(t)
   expected.remove((N.Deployment,OWL.equivalentClass,olds[0]))
   for t in tree(old,olds[0]):expected.remove(t)
   expected.add((N.Deployment,OWL.equivalentClass,news[0]))
   for t in tree(new,news[0]):expected.add(t)
   check(isomorphic(expected,new),key+': unrelated RDF change')
  else:check(oldproducts[key]==data,key+': expected byte identity')
  deltas.append({'product':key,'baseline_sha256':sha(paths['baseline'][key]),'candidate_sha256':sha(paths['candidate'][key]),'baseline_triples':len(old),'candidate_triples':len(new),'only_approved_axiom_replacement':True,'byte_identical':oldproducts[key]==data})
 _,again=generation._snapshot_uncached(root,a.workbook);check(again==products,'Deterministic generation failed')
 save(out/'product-deltas.json',deltas);print('Exact one-equivalence replacement, stable inventory and deterministic generation: PASS',flush=True)
 validations={}
 def run(key,phase):
  pp=paths[phase];dest=out/phase/(key+'-validation')
  if key=='integrated':r=mapping.run_candidate_hermit(pp[key],dest)
  elif key=='alignment_core':r=mapping.run_alignment_core_hermit(pp[key],dest)
  elif key=='strict_bfo_mapping':r=mapping.run_strict_bfo_hermit(pp[key],pp['alignment_core'],dest)
  else:r=mapping.run_cco_extension_hermit(pp[key],pp['strict_bfo_mapping'],pp['alignment_core'],dest)
  record=dataclasses.asdict(r);record['passed']=r.passed;validations[phase+'/'+key]=record;save(out/phase/(key+'-validation-result.json'),record)
  print(phase+'/'+key+': '+('PASS' if r.passed else 'FAIL')+'; unsatisfiable named classes='+str(r.owl_nothing_count),flush=True)
  check(r.passed,phase+'/'+key+': profile/HermiT failed')
 run('integrated','baseline')
 for key in ['integrated','alignment_core','strict_bfo_mapping','cco_extension']:run(key,'candidate')
 probe_results={}
 for phase in ['baseline','candidate']:
  ev=out/phase/'entailment';ev.mkdir();build=out/phase/'java';record=validations[phase+'/integrated']
  graph=Graph().parse(record['profile_graph_path'],format='turtle');baseline_size=len(graph);graph.parse(HERE/'probe-definitions.ttl',format='turtle')
  queries=json.loads((HERE/(phase+'-queries.json')).read_text());save(out/phase/'entailment-queries.json',queries)
  closure={'inputs':[semantic.fingerprint(root/p) for p in mapping.CANDIDATE_CLOSURE_INPUTS]+[semantic.fingerprint(paths[phase]['integrated'])], 'unresolved_imports':[],'closure_policy':'Existing complete pinned-local generator closure and established metadata declaration completion; no source/logical axiom removed. Fresh-name conservative definitions support focused entailment queries. Not a publication execution slot.','removed_logical_axioms':0,'profile_declaration_completion_count':record['profile_declaration_completion_count'],'probe_triples':len(graph)-baseline_size,'triples':len(graph)}
  helper=semantic.build_helper(ev,build);check(helper['status']=='ready','Existing pinned Java helper unavailable')
  result=semantic.run_graph(graph,closure,'deployment-'+phase,ev,build,helper,queries=queries,timeout=180)
  probe_results[phase]=result;save(out/phase/'entailment-result.json',result)
  payload=result.get('reasoner_result',{});check(result.get('status')=='consistent',phase+': probe graph inconsistency/profile failure');check(payload.get('owl2_dl_profile') is True,phase+': probe profile failure');check(len(payload.get('expectations',[]))==len(queries),phase+': incomplete probe results');check(all(x['passed'] for x in payload['expectations']),phase+': unexpected entailment')
  print(phase+': all '+str(len(queries))+' focused entailment probes PASS',flush=True)
 summary={'status':'PASS','baseline_workbook_sha256':sha(a.baseline_workbook),'candidate_workbook_sha256':sha(a.workbook),'counts':{k:after['counts'][k] for k in ['GOVERNED_ROW_COUNT','AUTHORITATIVE_AXIOM_COUNT','ZERO_AXIOM_ROW_COUNT']},'logical_delta':{'removed':'EquivalentClasses(ssn:Deployment ObjectIntersectionOf(cco:PlannedAct ObjectSomeValuesFrom(ssn:deployedSystem ssn:System) ObjectSomeValuesFrom(ssn:deployedOnPlatform bfo:MaterialEntity)))','added':'EquivalentClasses(ssn:Deployment ObjectIntersectionOf(cco:PlannedAct ObjectSomeValuesFrom(ssn:deployedSystem ssn:System)))'},'product_deltas':deltas,'deterministic_generation':True,'product_validation':{k:{'passed':v['passed'],'named_unsatisfiable_classes':v['owl_nothing_count'],'profile_return_code':v['profile_return_code']} for k,v in validations.items()},'focused_entailments':{k:v['reasoner_result']['expectations'] for k,v in probe_results.items()},'interpretation':'Platform witness is necessary in baseline; candidate permits a satisfiable Deployment with no deployedOnPlatform fillers. Native universal restrictions and inverse relationships are retained.'}
 save(out/'summary.json',summary);print(json.dumps(summary,default=str),flush=True)
if __name__=='__main__':main()
