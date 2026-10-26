# Current SSN/SOSA source notes

The current mapping authority is `mappings/SSN2BFO-COMS.xlsx`; the integrated ontology and three maintained modules are generated from it. The former current-track editor, direct-mapping shells, development catalog, and hierarchy-projection analysis have been retired rather than preserved as aliases.

This source directory retains only example data and its explicit parse-validation target. Validation resolves the maintained project modules and the pinned local dependencies directly, so it requires no development XML catalog. The full flattened merged CCO/BFO file `imports/cco.ttl` is a validation dependency, not a placeholder or mapping authority.

The separate `sosa-next` track is maintained with its own pinned SOSA-2023 source identity; it is not the source version of this current track. Formal release packages generate their own byte-governed package-relative catalog. Persistent-IRI deployment, redirects, and actual publication remain separate work; no release is created by publication-readiness assessment.

The current local source snapshot, merged CCO 2.0/BFO 2020 target, workbook, products, and scope are byte-pinned in `config/current-ssn-sosa-identity.json`. The source files preserve 2017-generation annotations and have no version IRIs; an upstream immutable commit is not established from repository evidence. The sampling file imports SKOS, for which no local dependency artifact is present. Local byte pinning does not establish a complete upstream import closure.

See `reports/current-ssn-sosa-publication-readiness.md` for current assessment and validation evidence, and `docs/CURRENT-SSN-SOSA-SEMANTIC-REVIEW.md` for the project review protocol. Historical diagnostic reports do not establish the current exact-closure publication result.
