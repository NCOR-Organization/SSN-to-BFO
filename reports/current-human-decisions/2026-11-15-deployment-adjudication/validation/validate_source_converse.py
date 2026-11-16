#!/usr/bin/env python3
"""Pure source-only Deployment converse probe; all output external."""
from pathlib import Path
import sys,json,hashlib
from rdflib import Graph,Namespace,RDF,RDFS,OWL,BNode
ROOT=Path('/Users/alecsculley/Documents/GitHub/SSN-to-BFO')
OUT=Path(__file__).resolve().parent/'source-converse-validation'
OUT.mkdir(exist_ok=False)
sys.path.insert(0,str(ROOT/'tools'))
import generate_mapping_from_coms as mapping
import current_semantic_validation as semantic
N=Namespace('http://www.w3.org/ns/ssn/');E=Namespace('urn:deployment-source-converse-probe:')
g=Graph()
for p in mapping.SOURCE_IMPORTS:g.parse(ROOT/p,format='turtle')
removed_imports=list(g.triples((None,OWL.imports,None)))
for t in removed_imports:g.remove(t)
assert not list(g.objects(N.Deployment,OWL.equivalentClass))
assert (N.deployedSystem,OWL.inverseOf,N.hasDeployment) in g
assert any(g.value(x,OWL.onProperty)==N.hasDeployment and g.value(x,OWL.allValuesFrom)==N.Deployment for x in g.objects(N.System,RDFS.subClassOf))
g.serialize(OUT/'source-only-closure.ttl',format='turtle')
completed=[]
for t in mapping.DL_PROFILE_DECLARATION_COMPLETION:
 if t not in g:g.add(t);completed.append(tuple(map(str,t)))
r=BNode();g.add((r,RDF.type,OWL.Restriction));g.add((r,OWL.onProperty,N.deployedSystem));g.add((r,OWL.someValuesFrom,N.System));g.add((E.DeploysSystem,RDF.type,OWL.Class));g.add((E.DeploysSystem,OWL.equivalentClass,r))
g.serialize(OUT/'source-only-profile-probe.ttl',format='turtle')
queries=[{'id':'native-inverse-universal-entails-converse','kind':'class_subsumption','subject':str(E.DeploysSystem),'object':str(N.Deployment),'expected_entailed':True},{'id':'source-does-not-require-a-system-witness','kind':'existential_subsumption','subject':str(N.Deployment),'predicate':str(N.deployedSystem),'object':str(N.System),'expected_entailed':False}]
(OUT/'queries.json').write_text(json.dumps(queries,indent=2)+'\n')
closure={'inputs':[semantic.fingerprint(ROOT/p) for p in mapping.SOURCE_IMPORTS],'unresolved_imports':[],'closure_policy':'Exactly four pinned current SSN/SOSA source ontologies; no workbook or mapping product and no BFO/CCO ontology. Imports expanded from fixed local source list then directives removed. Established metadata declarations added. One fresh conservative named existential definition for source-only converse query.','removed_logical_axioms':0,'removed_import_directives':[tuple(map(str,t)) for t in removed_imports],'declaration_completion':completed,'triples':len(g)}
(OUT/'closure-manifest.json').write_text(json.dumps(closure,indent=2)+'\n')
ev=OUT/'evidence';ev.mkdir();helper=semantic.build_helper(ev,OUT/'java');assert helper['status']=='ready'
result=semantic.run_graph(g,closure,'deployment-source-converse',ev,OUT/'java',helper,queries=queries,timeout=120)
(OUT/'result.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
payload=result.get('reasoner_result',{});assert result['status']=='consistent';assert payload['owl2_dl_profile'];assert len(payload['expectations'])==2;assert all(x['passed'] for x in payload['expectations'])
summary={'status':'PASS','source_only':True,'mapping_axioms_loaded':0,'target_ontologies_loaded':0,'owl2_dl_profile':payload['owl2_dl_profile'],'consistent':payload['consistent'],'expectations':payload['expectations'],'proof':'If x deployedSystem y and y is System, inverseOf gives y hasDeployment x; System subclass (hasDeployment only Deployment) implies x is Deployment. No mapping equivalence is used.','strict_weakening_relative_to_full_closure':'Baseline entails the new equivalence: old forward implication implies PlannedAct and some deployedSystem.System, while the source-only converse entails the reverse. Candidate does not entail the old equivalence because candidate permits a platform-free Deployment, as confirmed in focused-validation. Therefore this is a strict logical weakening relative to the retained source/mapping closure.','no_source_or_repository_changes':True}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
