#!/usr/bin/env python3
"""Replay the retained final-union diagnostic queries against a generated product.
Uses the existing repository reasoner API and retained original probe builder.
All output is external. No external historical graph/workbook capture is required.
"""
import argparse,json,sys,tempfile
from pathlib import Path
from rdflib import Graph,Namespace,RDF,OWL
from assess_union_candidates import S,N,B,C,P,ICE,probes,define,some,query,save
HERE=Path(__file__).resolve().parent

def answers(path):return {x['id']:x['entailed'] for x in json.loads(path.read_text())['reasoner_result']['expectations']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--product',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve();out=a.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
 sys.path.insert(0,str(root/'tools'));import generate_mapping_from_coms as mapping;import current_semantic_validation as semantic
 product=a.product or root/'SSN2BFO.ttl';mg=Graph().parse(product,format='turtle');prior=json.loads((HERE/'summary.json').read_text())['variants']['both_union'];assert semantic.graph_identity(mg)==prior['candidate_mapping_graph_identity'],'Candidate graph differs from retained final-union graph'
 original_inputs=json.loads((HERE/'input-manifest.json').read_text())['inputs']
 for path in mapping.CANDIDATE_CLOSURE_INPUTS:assert semantic.sha256(root/path)==original_inputs[str(path)],'Pinned dependency drift'
 graph=Graph()
 for path in mapping.CANDIDATE_CLOSURE_INPUTS:graph.parse(root/path,format='turtle')
 graph+=mg
 for t in list(graph.triples((None,OWL.imports,None))):graph.remove(t)
 for t in mapping.DL_PROFILE_DECLARATION_COMPLETION:graph.add(t)
 closure={'inputs':[semantic.fingerprint(root/x) for x in mapping.CANDIDATE_CLOSURE_INPUTS]+[semantic.fingerprint(product)],'unresolved_imports':[],'closure_policy':'Established fixed pinned-local current-track generator closure and metadata declaration completion. Diagnostic replay only; not a publication slot.'}
 qgraph=Graph()
 for t in graph:qgraph.add(t)
 queries,_=probes(qgraph);sy=Namespace('http://www.w3.org/ns/ssn/systems/')
 for name,prop,target in [('ICESystem_SystemCapability',sy.hasSystemCapability,sy.SystemCapability),('ICESystem_AgentIn_Process',C.ont00001787,B.BFO_0000015),('ICESystem_BearerOf_Function',B.BFO_0000196,B.BFO_0000034)]:
  x=define(qgraph,name,[N.System,ICE,some(qgraph,prop,target)]);queries.append(query(name,x,OWL.Nothing))
 x=define(qgraph,'SystemAndProcedure',[N.System,S.Procedure]);queries.append(query('SystemAndProcedure-unsatisfiable',x,OWL.Nothing))
 for name,role in [('GDCSystem',N.System),('GDCPlatform',S.Platform)]:
  x=define(qgraph,name,[B.BFO_0000031,role]);queries.append(query(name+'-implies-ICE',x,ICE,True));queries.append(query(name+'-aboutness-required',x,B.BFO_0000001,True,'existential_subsumption',C.ont00001808))
 expected={}
 for f in ['both_union-probe-result.json','supplemental-ice-roles-result.json','supplemental-intersections-both_union-result.json']:expected.update(answers(HERE/f))
 assert len(queries)==len(expected)==58
 # Unlike original exploratory placeholders, replay uses the retained observed answers.
 for q in queries:q['expected_entailed']=expected[q['id']]
 results={}
 with tempfile.TemporaryDirectory(prefix='ssn-union-replay-') as tmp:
  scratch=Path(tmp)
  def run(g,c,name,queries=None):
   d=scratch/name;d.mkdir();helper=semantic.build_helper(d,d/'java');r=semantic.run_graph(g,c,name,d,d/'java',helper,queries=queries,timeout=180);save(out/(name+'-result.json'),r);assert r['status']=='consistent' and r['reasoner_result']['owl2_dl_profile'];return r
  r=run(qgraph,closure,'final-union-queries',queries);assert all(x['passed'] for x in r['reasoner_result']['expectations']);results['final_candidate_query_count']=58
  ab=Graph()
  for t in graph:ab.add(t)
  for t in [(P.outer,RDF.type,S.Platform),(P.inner,RDF.type,S.Platform),(P.inner,RDF.type,ICE),(P.outer,S.hosts,P.inner),(P.outer,OWL.differentFrom,P.inner)]:ab.add(t)
  r=run(ab,closure,'distinct-platform-abox');results['distinct_platform_abox']=r['status']
  sg,sc=semantic.load_exact_local_graph((Path('imports/sosa.ttl'),Path('imports/ssn.ttl')),root)
  for t in mapping.DL_PROFILE_DECLARATION_COMPLETION:sg.add(t)
  sq=[]
  for name,term,prop,filler in [('Platform',S.Platform,S.hosts,N.System),('System',N.System,N.implements,S.Procedure)]:
   x=P['Native'+name];sg.add((x,RDF.type,OWL.Class));sg.add((x,OWL.equivalentClass,some(sg,prop,filler)));sq.extend([query(name+'-native-converse',x,term,True),query(name+'-native-witness',term,filler,False,'existential_subsumption',prop)])
  r=run(sg,sc,'native-converses',sq);assert {x['id']:x['entailed'] for x in r['reasoner_result']['expectations']}==answers(HERE/'source-converse-result.json');results['native_query_count']=4
 save(out/'summary.json',{'status':'PASS','results':results,'replay_inputs_self_contained':True,'source_and_mapping_files_modified':False});print(json.dumps(results),flush=True)
if __name__=='__main__':main()
