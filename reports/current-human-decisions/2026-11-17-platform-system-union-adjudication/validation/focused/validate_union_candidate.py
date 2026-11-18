#!/usr/bin/env python3
"""Bounded final generated-product checks and exact reuse of read-only impact evidence.
No authoritative workbook, ontology, assessment, repository, or clone file is written.
"""
import argparse,dataclasses,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from rdflib import Graph,Namespace,RDF,RDFS,OWL,URIRef,BNode
from rdflib.collection import Collection
from rdflib.compare import isomorphic
S=Namespace('http://www.w3.org/ns/sosa/');N=Namespace('http://www.w3.org/ns/ssn/');B=Namespace('http://purl.obolibrary.org/obo/');C=Namespace('https://www.commoncoreontologies.org/')
TERMS=(S.Platform,N.System)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,default=str)+'\n')
def check(x,msg):
 if not x:raise AssertionError(msg)
def clone(g):
 h=Graph()
 for t in g:h.add(t)
 return h
def expression(g,n):
 if isinstance(n,URIRef):return str(n)
 if (n,RDF.type,OWL.Restriction) in g:return {'some':str(g.value(n,OWL.onProperty)),'filler':str(g.value(n,OWL.someValuesFrom))}
 for p,k in ((OWL.intersectionOf,'and'),(OWL.unionOf,'or')):
  q=g.value(n,p)
  if q is not None:return {k:[expression(g,x) for x in Collection(g,q)]}
 raise AssertionError('Unexpected class expression')
def tree(g,n):
 seen=set();pending=[n]
 while pending:
  n=pending.pop()
  if n in seen:continue
  seen.add(n);pending.extend(o for _,o in g.predicate_objects(n) if isinstance(o,BNode))
 return {t for n in seen for t in g.triples((n,None,None))}
def remove(g,term):
 roots=list(g.objects(term,OWL.equivalentClass));check(len(roots)==1,'Incorrect existing equivalence count '+str(term));n=roots[0];g.remove((term,OWL.equivalentClass,n))
 for t in tree(g,n):g.remove(t)
def add(g,src,term):
 roots=list(src.objects(term,OWL.equivalentClass));check(len(roots)==1,'Incorrect candidate equivalence count '+str(term));n=roots[0];g.add((term,OWL.equivalentClass,n))
 for t in tree(src,n):g.add(t)
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--workbook',type=Path,required=True);p.add_argument('--intermediate-workbook',type=Path,required=True);p.add_argument('--impact',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=a.root.resolve();out=a.output.resolve();check(not out.is_relative_to(root),'Output must be external');out.mkdir(parents=True,exist_ok=True)
 sys.path.insert(0,str(root/'tools'));import current_semantic_generation as generation;import generate_mapping_from_coms as mapping;import current_semantic_validation as semantic
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();check(head=='3376e1c74e846e40e6863ec8b1f1c255349aa2d3','Unexpected HEAD')
 headbytes=subprocess.check_output(['git','show',head+':mappings/SSN2BFO-COMS.xlsx'],cwd=root)
 with tempfile.TemporaryDirectory(prefix='ssn-union-final-') as tmp:
  scratch=Path(tmp);headbook=scratch/'head.xlsx';headbook.write_bytes(headbytes)
  snapshots={};products={}
  for phase,book in [('head',headbook),('intermediate',a.intermediate_workbook),('candidate',a.workbook)]:snapshots[phase],products[phase]=generation._snapshot(root,book)
  save(out/'generation-counts.json',{phase:x['counts'] for phase,x in snapshots.items()})
  for k,n in [('GOVERNED_ROW_COUNT',108),('AUTHORITATIVE_AXIOM_COUNT',102),('ZERO_AXIOM_ROW_COUNT',6)]:check(all(x['counts'][k]==n for x in snapshots.values()),'Unexpected inventory change '+k)
  expressions={};deltas=[];candidate_graphs={k:Graph().parse(data=v.decode(),format='turtle') for k,v in products['candidate'].items()}
  expected_final={S.Platform:{'and':[{'or':[str(B.BFO_0000040),str(C.ont00000958)]},{'some':str(S.hosts),'filler':str(N.System)}]},N.System:{'and':[{'or':[str(B.BFO_0000040),str(C.ont00000958)]},{'some':str(N.implements),'filler':str(S.Procedure)}]}}
  for phase in ['head','intermediate','candidate']:
   g=Graph().parse(data=products[phase]['integrated'].decode(),format='turtle');expressions[phase]={str(t):expression(g,g.value(t,OWL.equivalentClass)) for t in TERMS}
   if phase=='candidate':check(all(expressions[phase][str(t)]==expected_final[t] for t in TERMS),'Wrong final expressions')
  for phase in ['head','intermediate']:
   for key,new in candidate_graphs.items():
    old=Graph().parse(data=products[phase][key].decode(),format='turtle');expected=clone(old)
    if key=='integrated':
     for term in TERMS:remove(expected,term);add(expected,new,term)
    elif key=='strict_bfo_mapping':
     for term in TERMS:remove(expected,term);check(not list(new.objects(term,OWL.equivalentClass)),'Mixed target remained in strict BFO')
    elif key=='cco_extension':
     for term in TERMS:check(not list(old.objects(term,OWL.equivalentClass)),'Unexpected prior CCO equivalence');add(expected,new,term)
    else:check(products[phase][key]==products['candidate'][key],'Alignment-core byte drift')
    check(isomorphic(expected,new),'Unrelated product graph change '+phase+'/'+key)
    deltas.append({'comparison':phase+'-to-candidate','product':key,'before_sha256':hashlib.sha256(products[phase][key]).hexdigest(),'after_sha256':hashlib.sha256(products['candidate'][key]).hexdigest(),'before_triples':len(old),'after_triples':len(new),'exact_approved_change':True,'byte_identical':products[phase][key]==products['candidate'][key]})
  _,again=generation._snapshot_uncached(root,a.workbook);check(again==products['candidate'],'Nondeterministic generation')
  save(out/'logical-delta.json',{'status':'PASS','expressions':expressions,'integrated_delta':'Exactly two equivalence replacements versus HEAD and exactly two versus preserved intermediate workbook.','modular_redistribution':'Exactly these two expressions move from strict-BFO to CCO-extension because their targets now contain CCO ICE.','products':deltas})
  print('Exact two-equivalence deltas against HEAD and intermediate; modular relocation; deterministic generation: PASS',flush=True)
  docs={}
  for key,data in products['candidate'].items():docs[key]=scratch/(key+'.ttl');docs[key].write_bytes(data)
  product_results={}
  for key in ['integrated','alignment_core','strict_bfo_mapping','cco_extension']:
   dest=scratch/(key+'-validation')
   if key=='integrated':r=mapping.run_candidate_hermit(docs[key],dest)
   elif key=='alignment_core':r=mapping.run_alignment_core_hermit(docs[key],dest)
   elif key=='strict_bfo_mapping':r=mapping.run_strict_bfo_hermit(docs[key],docs['alignment_core'],dest)
   else:r=mapping.run_cco_extension_hermit(docs[key],docs['strict_bfo_mapping'],docs['alignment_core'],dest)
   item=dataclasses.asdict(r);item['passed']=r.passed;save(out/(key+'-validation-result.json'),item);product_results[key]={'passed':r.passed,'owl2_dl_profile':r.profile_return_code==0,'named_unsatisfiable_classes':r.owl_nothing_count};check(r.passed,key+' profile/HermiT failed');print(key+': PASS; named unsats='+str(r.owl_nothing_count),flush=True)
  current_identity=semantic.graph_identity(candidate_graphs['integrated']);impact=json.loads((a.impact/'summary.json').read_text());prior=impact['variants']['both_union'];check(prior['candidate_mapping_graph_identity']==current_identity,'Cannot reuse non-identical impact graph')
  impact_inputs=json.loads((a.impact/'input-manifest.json').read_text())['inputs'];dependency_check={str(p):{'prior':impact_inputs[str(p)],'current':sha(root/p)} for p in mapping.CANDIDATE_CLOSURE_INPUTS};check(all(x['prior']==x['current'] for x in dependency_check.values()),'Pinned dependency change invalidates reuse')
  for rel in ['tools/current_semantic_validation.py','tools/generate_mapping_from_coms.py','tools/java/CurrentSemanticReasoner.java']:
   expected=next(x['sha256'] for x in json.loads((a.impact/'both_union-probe-result.json').read_text())['attempt']['execution_binding']['expected_inputs'] if x['path']==rel) if rel!='tools/generate_mapping_from_coms.py' else None
   if expected:check(expected==sha(root/rel),'Reasoner API drift '+rel)
  refs=['summary.json', 'input-manifest.json', 'both_union-probe-result.json', 'source-converse-result.json', 'supplemental-ice-roles-result.json', 'supplemental-intersections-both_union-result.json', 'distinct-platforms-both_union-result.json', 'assess_union_candidates.py', 'replay_focused_queries.py']
  reuse={'status':'EXACT_GRAPH_AND_DEPENDENCIES_MATCH','candidate_mapping_graph_identity':current_identity,'prior_graph_identity':prior['candidate_mapping_graph_identity'],'dependency_hashes':dependency_check,'evidence_files':[{'path':'reused-impact/'+r,'sha256':sha(a.impact/r)} for r in refs],'directly_reused_candidate_queries':58,'source_only_queries':4,'supporting_comparison_queries_across_all_variants':263,'directly_reused_aboxes':1,'qualified_reuse':'263 answers describe the broader comparison matrix, not 263 fresh candidate-only tests. Final both-union graph reuses 50 primary +3 role +5 intersection queries and the distinct-individual ABox; native-source proof contributes four queries. Other variants support the comparison only.','retained_known_conditional_conflicts':['ICE Sensor/Actuator/Sampler','Site and SDC Platform/System','Platform without hosted System','System without implemented Procedure','Occurrent Platform/System','ICE System with SystemCapability','Mixed material/ICE subsystem directions','ICE System bearing Function'],'not_new_named_class_unsatisfiability':True}
  save(out/'impact-evidence-reuse.json',reuse)
  summary={'status':'PASS','head':head,'workbook_hashes':{'head':hashlib.sha256(headbytes).hexdigest(),'intermediate':sha(a.intermediate_workbook),'candidate':sha(a.workbook)},'counts':{k:snapshots['candidate']['counts'][k] for k in ['GOVERNED_ROW_COUNT','AUTHORITATIVE_AXIOM_COUNT','ZERO_AXIOM_ROW_COUNT']},'two_approved_equivalence_replacements_only':True,'modular_redistribution_verified':True,'deterministic_generation':True,'product_validation':product_results,'product_hashes':{k:hashlib.sha256(v).hexdigest() for k,v in products['candidate'].items()},'reused_semantic_evidence':reuse,'repo_files_written':False}
  save(out/'summary.json',summary);print('Exact impact graph/dependency match: focused evidence reuse verified.',flush=True)
if __name__=='__main__':main()
