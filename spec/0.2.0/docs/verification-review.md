# Reference verification review — 2026-09-04

All six findings against `7da6518481b25c25e9f4a44a315041b3a6b5ba4c`
were reproduced and corrected in the draft reference checks. The layered
architecture and inherited portable object hashes remain unchanged. These are
reference conformance results, not tests of deployed Cissa or Thoth systems.

| Finding | Confirmed behavior before correction | Corrected boundary |
|---|---|---|
| P1: altered available archive content | Verified accepted changed content after updating unsigned stream checksums | Canonical verifies every supplied compartment and Blob body; Verified restore and downgrade source reuse the same integrity checker |
| P1: expired producer credential | Ingestion accepted a trusted credential expiring at batch time while its receipt failed | Both paths use the same lineage and credential payload validity intervals |
| P2: unresolved catalog dependencies | Exchange accepted required dependency digests replaced with zeroes | Required dependencies resolve by kind, identifier, and recomputed digest; local catalog artifacts are checked too |
| P2: predicate pack bypass | Exchange activated `ccf.work.works_on` without the work pack | Activation combines enclosing type and predicate requirements; unregistered predicates fail |
| P2: receipt without producer continuity | An orphan successor remained pending in ingestion but its receipt verified | Receipts replay authenticated predecessor batches from genesis using ingestion checks |
| P2: undeclared provenance | Exchange accepted an absent `recorded_by` target | Schema-typed provenance, origin, authority, lineage predecessor, payload, and Link references must be included or declared |

The dependency correction also exposed missing recorder/person dependencies in
the downgrade example. Its manifest and generator now declare those references.
Unknown extensions and literal values remain opaque, and declared external,
withheld, and erased references remain acceptable at Exchange.

Regression tests mutate temporary package copies. Exchange tests refresh
unsigned stream and distribution checksums, so package checksum rejection cannot
mask a semantic validation failure. Body tests refresh unsigned stream metadata
without changing committed headers or journal signatures. Regression tests for the exact stored
transcript mutation, structural body mutation, and Blob mutation fail against the
reviewed Canonical and Verified runners because they accept the altered content.
Those rejection tests pass after the fix.

Validation after correction:

- Exchange passes, including 18 boundary regression tests.
- Canonical passes 187 vector/reference checks plus 3 body mutation tests.
- Verified passes 218 history checks plus 3 body mutation tests and the cumulative lower-level checks.
- Signed Producer Sync passes 72 checks, including credential time boundaries and authenticated predecessor evidence.
- Continuity, work, and agent semantic-pack suites pass.
- Governed passes, including the inherited 201 vectors, 991 mindpack checks, 11 portable conformance cases, and the multi-schema PostgreSQL + pgvector fixture. The initial Docker permission failure was resolved by starting a shell with the account's existing Docker group membership; no system configuration was changed.
- The `spec/0.1.2` directory has no changes and its published SHA256SUMS verify.

Run the complete available suite with:

```bash
make -C spec/0.2.0 -k check-governed check-capability-signed-producer-sync \
  check-semantic-pack-continuity check-semantic-pack-work check-semantic-pack-agent
```

0.2.0 remains a Working Draft. Promotion requires resolution of the independent
capability-suite blockers already listed in
[conformance-suites.md](conformance-suites.md): encryption, selective erasure,
witnessing, succession, and external KMS. CCF 0.1.2 remains the interoperability
release. The [Cissa-to-Thoth build checks](adoption-and-interoperability.md)
remain application work even when the reference package passes.
