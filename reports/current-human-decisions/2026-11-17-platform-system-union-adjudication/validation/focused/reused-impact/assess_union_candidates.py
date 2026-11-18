#!/usr/bin/env python3
"""Read-only, bounded candidate graph diagnostics using existing repository APIs.
No workbook/governance or repository files are written. Scratch execution graphs are
reproducible and temporary; compact result records and this driver are retained.
"""
import argparse,copy,hashlib,json,sys,tempfile
from pathlib import Path
from rdflib import Graph,Namespace,URIRef,BNode,RDF,RDFS,OWL
from rdflib.collection import Collection
S=Namespace('http://www.w3.org/ns/sosa/'); N=Namespace('http://www.w3.org/ns/ssn/'); B=Namespace('http://purl.obolibrary.org/obo/'); C=Namespace('https://www.commoncoreontologies.org/'); P=Namespace('urn:platform-system-union-probe:')
ICE=C.ont00000958; MATERIAL=B.BFO_0000040; CONT=B.BFO_0000002; OCC=B.BFO_0000003

def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,default=str)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clone(g):
 r=Graph()
 for t in g:r.add(t)
 return r

def logical(g,kind,items):
 x=BNode();head=BNode();g.add((x,RDF.type,OWL.Class));g.add((x,kind,head));Collection(g,head,items);return x

def some(g,prop,target):
 x=BNode();g.add((x,RDF.type,OWL.Restriction));g.add((x,OWL.onProperty,prop));g.add((x,OWL.someValuesFrom,target));return x

def complement(g,target):
 x=BNode();g.add((x,RDF.type,OWL.Class));g.add((x,OWL.complementOf,target));return x

def define(g,name,terms):
 x=P[name];g.add((x,RDF.type,OWL.Class));g.add((x,OWL.equivalentClass,logical(g,OWL.intersectionOf,terms)));return x

def replace_base(g,term,base):
 eq=list(g.objects(term,OWL.equivalentClass));assert len(eq)==1
 head=g.value(eq[0],OWL.intersectionOf);parts=list(Collection(g,head));assert len(parts)==2
 expected=CONT if term==S.Platform else MATERIAL;assert parts[0]==expected
 target=logical(g,OWL.unionOf,[MATERIAL,ICE]) if base=='union' else CONT
 g.set((head,RDF.first,target))

def query(identifier,subject,obj,expected=False,kind='class_subsumption',predicate=None):
 q={'id':identifier,'kind':kind,'subject':str(subject),'object':str(obj),'expected_entailed':expected}
 if predicate:q['predicate']=str(predicate)
 return q

def probes(g):
 expressions={}; queries=[]
 def add(name,terms):
  expressions[name]=define(g,name,terms);queries.append(query('unsat:'+name,expressions[name],OWL.Nothing));return expressions[name]
 for role in (S.Platform,N.System,S.Sensor,S.Actuator,S.Sampler):
  label=str(role).rsplit('/',1)[-1]
  for name,typ in [('ICE',ICE),('Material',MATERIAL),('Site',B.BFO_0000029),('SpatialRegion',B.BFO_0000006),('Immaterial',B.BFO_0000141),('SpecificallyDependentContinuant',B.BFO_0000020),('Occurrent',OCC)]:
   if role in (S.Sensor,S.Actuator,S.Sampler) and name not in ('ICE','Material'):continue
   add(label+'_'+name,[role,typ])
 add('Material_ICE',[MATERIAL,ICE]);add('Site_ICE',[B.BFO_0000029,ICE]);add('Site_Material',[B.BFO_0000029,MATERIAL])
 add('Platform_NoHostedSystem',[S.Platform,complement(g,some(g,S.hosts,N.System))])
 add('System_NoImplementedProcedure',[N.System,complement(g,some(g,N.implements,S.Procedure))])
 pi=logical(g,OWL.intersectionOf,[S.Platform,ICE]);si=logical(g,OWL.intersectionOf,[N.System,ICE])
 add('Platform_Hosts_ICEPlatform',[S.Platform,some(g,S.hosts,pi)])
 add('ICEPlatform_Hosts_ICEPlatform',[S.Platform,ICE,some(g,S.hosts,pi)])
 add('MaterialPlatform_Hosts_ICEPlatform',[S.Platform,MATERIAL,some(g,S.hosts,pi)])
 add('ICEPlatform_Hosts_ICESystem',[S.Platform,ICE,some(g,S.hosts,si)])
 add('MaterialPlatform_Hosts_ICESystem',[S.Platform,MATERIAL,some(g,S.hosts,si)])
 add('ICEPlatform_Hosts_Sensor',[S.Platform,ICE,some(g,S.hosts,S.Sensor)])
 add('ICESystem_Implements_Procedure',[N.System,ICE,some(g,N.implements,S.Procedure)])
 add('ICEEntity_Implements_Procedure',[ICE,some(g,N.implements,S.Procedure)])
 add('ICESystem_HasSubSystem_ICESystem',[N.System,ICE,some(g,N.hasSubSystem,si)])
 add('MaterialSystem_HasSubSystem_ICESystem',[N.System,MATERIAL,some(g,N.hasSubSystem,si)])
 add('ICESystem_HasSubSystem_MaterialSystem',[N.System,ICE,some(g,N.hasSubSystem,logical(g,OWL.intersectionOf,[N.System,MATERIAL]))])
 for role,prop,filler in [(S.Platform,S.hosts,N.System),(N.System,N.implements,S.Procedure)]:
  label=str(role).rsplit('/',1)[-1]
  q=query(label+'-witness-required',role,filler,True,'existential_subsumption',prop);queries.append(q)
  x=P[label+'Reverse'];g.add((x,RDF.type,OWL.Class));g.add((x,OWL.equivalentClass,some(g,prop,filler)));queries.append(query(label+'-source-converse',x,role,True))
 for role in (S.Platform,N.System,S.Sensor,S.Actuator,S.Sampler):
  label=str(role).rsplit('/',1)[-1]
  queries.append(query(label+'-material',role,MATERIAL))
  queries.append(query(label+'-continuant',role,CONT,True))
 return queries,expressions

def main():
 a=argparse.ArgumentParser();a.add_argument('--root',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 root=args.root.resolve();out=args.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=True)
 sys.path.insert(0,str(root/'tools'));import generate_mapping_from_coms as mapping;import current_semantic_validation as semantic
 original=Graph().parse(root/'SSN2BFO.ttl');before={str(x):sha(root/x) for x in [*mapping.CANDIDATE_CLOSURE_INPUTS,Path('SSN2BFO.ttl'),Path('mappings/SSN2BFO-COMS.xlsx')]};save(out/'input-manifest.json',{'inputs':before,'driver_sha256':sha(Path(__file__)),'closure_policy':'Same fixed local source/CCO/BFO closure and declaration completion as existing current-track generator diagnostics; no logical source axiom removed. SKOS metadata import directives remain a separate packaging concern.','exploratory_query_convention':'For exploratory unsatisfiability and materiality questions, expected_entailed=false is the API placeholder, not an assertion that every answer should be false. Report actual entailed answers; placeholder passed flags are not the assessment verdict.'})
 variants={'current':{},'platform_union':{'Platform':'union'},'system_union':{'System':'union'},'both_union':{'Platform':'union','System':'union'},'system_continuant':{'System':'continuant'}};summary={}
 with tempfile.TemporaryDirectory(prefix='ssn-union-diagnostic-') as tmp:
  scratch=Path(tmp)
  for key,changes in variants.items():
   g=clone(original)
   for term,base in changes.items():replace_base(g,S.Platform if term=='Platform' else N.System,base)
   doc=scratch/(key+'.ttl');g.serialize(destination=doc,format='turtle')
   pr=mapping.run_candidate_hermit(doc,scratch/(key+'-product'))
   import dataclasses
   pd=dataclasses.asdict(pr);pd['passed']=pr.passed;save(out/(key+'-product-result.json'),pd)
   print(key+': unaugmented product profile='+str(pr.profile_return_code==0)+'; named unsats='+str(pr.owl_nothing_count),flush=True)
   if not pr.passed:summary[key]={'product_pass':False,'product_result':pd};continue
   closuregraph=Graph().parse(pr.profile_graph_path,format='turtle')
   closure={'inputs':[semantic.fingerprint(root/x) for x in mapping.CANDIDATE_CLOSURE_INPUTS]+[semantic.fingerprint(root/'SSN2BFO.ttl')],'unresolved_imports':[],'candidate_change':changes,'candidate_mapping_graph_identity':semantic.graph_identity(g),'closure_policy':'Established complete pinned-local generator closure and metadata declaration completion. Diagnostic only, no publication execution slot.','removed_logical_axioms':0}
   qgraph=clone(closuregraph);queries,expressions=probes(qgraph);dest=scratch/(key+'-queries');dest.mkdir();build=dest/'java';helper=semantic.build_helper(dest,build)
   result=semantic.run_graph(qgraph,closure,'union-'+key,dest,build,helper,queries=queries,timeout=180);save(out/(key+'-probe-result.json'),result)
   payload=result.get('reasoner_result',{});assert result['status']=='consistent' and payload['owl2_dl_profile']
   answers={x['id']:x['entailed'] for x in payload['expectations']};sat={name:not answers['unsat:'+name] for name in expressions}
   # Explicit role-filler ABox, in addition to existential class-expression probes.
   abox=clone(closuregraph)
   for t in [(P.outer,RDF.type,S.Platform),(P.inner,RDF.type,S.Platform),(P.inner,RDF.type,ICE),(P.outer,S.hosts,P.inner)]:abox.add(t)
   abdest=scratch/(key+'-abox');abdest.mkdir();abbuild=abdest/'java';abhelper=semantic.build_helper(abdest,abbuild)
   ar=semantic.run_graph(abox,closure,'abox-'+key,abdest,abbuild,abhelper,timeout=180);save(out/(key+'-abox-result.json'),ar)
   assert ar['status'] in ('consistent','inconsistent') and ar['reasoner_result']['owl2_dl_profile']
   summary[key]={'product_pass':pr.passed,'named_unsatisfiable_classes':pr.owl_nothing_count,'owl2_dl_profile':payload['owl2_dl_profile'],'probe_query_count':len(queries),'satisfiable_intersections':sat,'entailments':{k:v for k,v in answers.items() if not k.startswith('unsat:')},'explicit_abox_status':ar['status'],'candidate_mapping_graph_identity':semantic.graph_identity(g),'changes':changes}
   print(key+': '+str(len(queries))+' diagnostic answers; ICE inner-Platform ABox '+ar['status'],flush=True)
  sg,sc=semantic.load_exact_local_graph((Path('imports/sosa.ttl'),Path('imports/ssn.ttl')),root)
  for t in mapping.DL_PROFILE_DECLARATION_COMPLETION:sg.add(t)
  sq=[]
  for name,term,prop,filler in [('Platform',S.Platform,S.hosts,N.System),('System',N.System,N.implements,S.Procedure)]:
   x=P['Native'+name];sg.add((x,RDF.type,OWL.Class));sg.add((x,OWL.equivalentClass,some(sg,prop,filler)));sq.extend([query(name+'-native-converse',x,term,True),query(name+'-native-witness',term,filler,False,'existential_subsumption',prop)])
  dest=scratch/'source';dest.mkdir();build=dest/'java';helper=semantic.build_helper(dest,build);sr=semantic.run_graph(sg,sc,'native-converses',dest,build,helper,queries=sq,timeout=180);save(out/'source-converse-result.json',sr)
  assert sr['status']=='consistent' and all(x['passed'] for x in sr['reasoner_result']['expectations'])
  summary['source_converses']=sr['reasoner_result']['expectations']
 assert all(sha(root/x)==v for x,v in before.items()),'Repository inputs changed during execution'
 save(out/'summary.json',{'status':'COMPLETE','read_only':True,'baseline':'Current uncommitted Platform Continuant adjudication preserved','variants':summary,'product_variants':len(variants),'source_query_count':4,'total_probe_queries':sum(v.get('probe_query_count',0) for v in summary.values() if isinstance(v,dict)),'explicit_abox_cases':len(variants),'interpretation_note':'Named-class satisfiability does not imply every intersection or role-filler combination is satisfiable. ICE is not treated as a material information bearer.'})
 print('All diagnostics complete; repository input hashes unchanged.',flush=True)
if __name__=='__main__':main()
