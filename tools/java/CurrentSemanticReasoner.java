/* Project-local complete-reasoner adapter. Uses the existing pinned ROBOT jar. */
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import org.semanticweb.HermiT.ReasonerFactory;
import org.semanticweb.owlapi.apibinding.OWLManager;
import org.semanticweb.owlapi.model.*;
import org.semanticweb.owlapi.profiles.*;
import org.semanticweb.owlapi.reasoner.*;

public class CurrentSemanticReasoner {
    static Map<String, Object> row(String kind, String left, String right) {
        Map<String, Object> result = new TreeMap<>();
        result.put("kind", kind); result.put("subject", left); result.put("object", right);
        return result;
    }
    static boolean named(OWLClass c) { return !c.isOWLThing() && !c.isOWLNothing(); }
    static boolean named(OWLObjectPropertyExpression p) {
        return !p.isAnonymous() && !p.isOWLTopObjectProperty() && !p.isOWLBottomObjectProperty();
    }
    static OWLAxiom query(Map<String, Object> q, OWLDataFactory f) {
        IRI s = IRI.create((String) q.get("subject"));
        IRI o = IRI.create((String) q.get("object"));
        switch ((String) q.get("kind")) {
            case "class_assertion": return f.getOWLClassAssertionAxiom(f.getOWLClass(o), f.getOWLNamedIndividual(s));
            case "object_property_assertion": return f.getOWLObjectPropertyAssertionAxiom(
                f.getOWLObjectProperty(IRI.create((String) q.get("predicate"))), f.getOWLNamedIndividual(s), f.getOWLNamedIndividual(o));
            case "class_subsumption": return f.getOWLSubClassOfAxiom(f.getOWLClass(s), f.getOWLClass(o));
            case "object_property_subsumption": return f.getOWLSubObjectPropertyOfAxiom(f.getOWLObjectProperty(s), f.getOWLObjectProperty(o));
            case "existential_subsumption": return f.getOWLSubClassOfAxiom(f.getOWLClass(s), f.getOWLObjectSomeValuesFrom(
                f.getOWLObjectProperty(IRI.create((String) q.get("predicate"))), f.getOWLClass(o)));
            default: throw new IllegalArgumentException("Unsupported expectation kind: " + q.get("kind"));
        }
    }
    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        Map<String, Object> result = new LinkedHashMap<>();
        OWLReasoner reasoner = null;
        try {
            OWLOntologyManager manager = OWLManager.createOWLOntologyManager();
            // Python has already expanded all available local imports and removed import
            // directives from the temporary document. No network resolution is permitted.
            manager.getIRIMappers().add(iri -> IRI.create("file:///__current_semantic_no_network__/missing.owl"));
            manager.setOntologyLoaderConfiguration(new OWLOntologyLoaderConfiguration()
                .setMissingImportHandlingStrategy(MissingImportHandlingStrategy.THROW_EXCEPTION)
                .setRepairIllegalPunnings(false));
            OWLOntology ontology = manager.loadOntologyFromOntologyDocument(new File(args[0]));
            if (!ontology.getImportsDeclarations().isEmpty()) throw new IllegalArgumentException("Unexpected unresolved import directive");
            result.put("logical_axiom_count", ontology.getLogicalAxiomCount());
            OWLProfileReport profile = new OWL2DLProfile().checkOntology(ontology);
            List<String> violations = new ArrayList<>();
            for (OWLProfileViolation v : profile.getViolations()) violations.add(v.toString());
            Collections.sort(violations);
            result.put("owl2_dl_profile", profile.isInProfile());
            result.put("profile_violations", violations);
            List<String> classes = new ArrayList<>(), properties = new ArrayList<>();
            for (OWLClass c : ontology.getClassesInSignature()) if (named(c)) classes.add(c.getIRI().toString());
            for (OWLObjectProperty p : ontology.getObjectPropertiesInSignature()) if (named(p)) properties.add(p.getIRI().toString());
            Collections.sort(classes); Collections.sort(properties);
            result.put("signature", Map.of("classes", classes, "object_properties", properties));
            reasoner = new ReasonerFactory().createReasoner(ontology);
            result.put("reasoner", reasoner.getReasonerName());
            result.put("reasoner_version", reasoner.getReasonerVersion().toString());
            boolean consistent = reasoner.isConsistent();
            result.put("consistent", consistent);
            result.put("status", profile.isInProfile() ? (consistent ? "consistent" : "inconsistent") : "profile_failure");
            // Diagnostic consistency from an out-of-profile graph is never publication evidence.
            if (consistent && profile.isInProfile()) {
                if (args[1].equals("hierarchy")) {
                    reasoner.precomputeInferences(InferenceType.CLASS_HIERARCHY, InferenceType.OBJECT_PROPERTY_HIERARCHY);
                    Map<String, Map<String, Object>> relations = new TreeMap<>();
                    for (OWLClass c : ontology.getClassesInSignature()) if (named(c)) {
                        String left = c.getIRI().toString();
                        Set<OWLClass> supers = new HashSet<>(reasoner.getSuperClasses(c, false).getFlattened());
                        Set<OWLClass> equivalents = reasoner.getEquivalentClasses(c).getEntities();
                        supers.addAll(equivalents);
                        for (OWLClass sup : supers) if (named(sup) && !sup.equals(c)) {
                            String right = sup.getIRI().toString();
                            relations.put("C\t" + left + "\t" + right, row("class_subsumption", left, right));
                        }
                        for (OWLClass eq : equivalents) if (named(eq) && !eq.equals(c)) {
                            String right = eq.getIRI().toString();
                            if (left.compareTo(right) < 0) relations.put("E\t" + left + "\t" + right, row("class_equivalence", left, right));
                        }
                    }
                    for (OWLObjectProperty p : ontology.getObjectPropertiesInSignature()) if (named(p)) {
                        String left = p.getIRI().toString();
                        Set<OWLObjectPropertyExpression> supers = new HashSet<>(reasoner.getSuperObjectProperties(p, false).getFlattened());
                        Set<OWLObjectPropertyExpression> equivalents = reasoner.getEquivalentObjectProperties(p).getEntities();
                        supers.addAll(equivalents);
                        for (OWLObjectPropertyExpression sup : supers) if (named(sup) && !sup.equals(p)) {
                            String right = sup.asOWLObjectProperty().getIRI().toString();
                            relations.put("P\t" + left + "\t" + right, row("object_property_subsumption", left, right));
                        }
                        for (OWLObjectPropertyExpression eq : equivalents) if (named(eq) && !eq.equals(p)) {
                            String right = eq.asOWLObjectProperty().getIRI().toString();
                            if (left.compareTo(right) < 0) relations.put("Q\t" + left + "\t" + right, row("object_property_equivalence", left, right));
                        }
                    }
                    result.put("relations", new ArrayList<>(relations.values()));
                }
                if (args.length > 2) {
                    List<Map<String, Object>> queries = new ObjectMapper().readValue(Files.readString(Paths.get(args[2])), List.class);
                    List<Map<String, Object>> answers = new ArrayList<>();
                    for (Map<String, Object> q : queries) {
                        OWLAxiom axiom = query(q, manager.getOWLDataFactory());
                        if (!reasoner.isEntailmentCheckingSupported(axiom.getAxiomType()))
                            throw new IllegalArgumentException("Entailment query unsupported: " + axiom.getAxiomType());
                        boolean entailed = reasoner.isEntailed(axiom);
                        answers.add(Map.of("id", q.get("id"), "entailed", entailed,
                            "passed", entailed == (Boolean) q.get("expected_entailed")));
                    }
                    result.put("expectations", answers);
                }
            }
        } catch (Throwable error) {
            result.put("status", "technical_failure");
            result.put("error", error.getClass().getName() + ": " + error.getMessage());
            error.printStackTrace(System.err);
        } finally {
            if (reasoner != null) reasoner.dispose();
        }
        System.out.println(new ObjectMapper().writeValueAsString(result));
        if (!List.of("consistent", "inconsistent").contains(result.get("status"))) System.exit(2);
    }
}
