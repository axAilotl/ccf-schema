# Adoption and interoperability matrix

## Cissa and Thoth target declarations

| Component | CCF boundary |
|---|---|
| Cissa pendant firmware | Reliable capture transport and device/session identity; not a CCF implementation |
| Cissa phone | Exchange Producer and Preserver with durable batching |
| Cissa phone-only mode | Optional Canonical Store |
| Cissa Home or Cloud | Verified Archive, plus only the capabilities it operates |
| Thoth reference archive | Governed Archive |
| Scoped knowledge transfer | CCF Capsule |
| Backup, replica, or archive migration | mindpack restore or foreign merge |

Full governance is claimed only after policy evaluation, deletion operations,
suppression behavior, generation fences, and destructive projection rebuild have
passed operational tests.

## Planned cross-application cases

1. Exchange Capsule round trip preserves IDs, types, source claims, references,
   and unknown extensions.
2. Canonical round trip preserves object hashes and available compartments.
3. Duplicate Capsule import remains idempotent.
4. Same origin and revision with changed content produces a conflict.
5. Unsupported semantic packs remain preserved and inert.
6. Withheld, erased, and external states remain distinguishable.
7. Foreign merge preserves source proofs and creates destination admission
   history without rewriting portable objects.
8. Audio capture survives termination at every boundary without duplicate or
   missing semantic artifacts.
9. Governed erasure transfer cannot silently resurrect or relabel material.

Round trips between two applications that share one serializer, verifier, or
archive kernel prove integration but not independent interoperability. A full
independent claim needs a separately written generator or verifier. That second
implementation can target Exchange and Canonical Store before implementing an
archive or governance engine.

These cases are an application-integration roadmap, not claims made by this
schema repository. The package directly exercises Capsule preservation,
canonical uplift/idempotency, Verified foreign-merge invariants, and Governed
erasure fixtures. Real Thoth/Cissa round trips and process-interruption tests
require those application repositories and remain external release gates.

## Cissa-to-Thoth build acceptance checks

Use the 0.2.0 Working Draft for the current integration builds while retaining
`ccf/0.1.2` portable Record, Link, Blob, and compartment formats and hashes.
A draft implementation declaration describes the selected role, guarantee level,
and supported packs/capabilities; it does not announce a 0.2.0 interoperability
release. Do not rewrite existing objects to adopt the draft's layered declarations.

The six reference-verifier gaps and their regression results are recorded in
[verification-review.md](verification-review.md). Carry the following checks
into the Cissa sender and Thoth receiver adapters:

| Build boundary | Required integration behavior |
|---|---|
| Cissa export → Thoth Exchange import | Resolve required catalog/schema/registry dependencies by identifier and digest before activation; reject mismatched dependencies |
| Active semantic assertions | Require both the enclosing type's requirements and its predicate's pack/capabilities; preserve unsupported semantics inertly or refuse activation |
| Scoped Capsule dependencies | Include or declare the recorder, origin source, authority/person claims, lineage predecessor, typed payload references, and Link endpoints; retain external/withheld/erased distinctions |
| Canonical admission and archive restore | Verify every available compartment and Blob against committed hashes and byte lengths; updating unsigned stream checksums must not hide altered transcripts or audio |
| Signed upload authentication | Validate the trusted credential lineage and payload at batch time with inclusive `valid_from` and exclusive `expires_at`; null expiry is unbounded |
| Signed-sync receipt | Retain authenticated predecessor evidence and verify continuity; an orphan batch may await its predecessor but cannot receive a verified signed-sync receipt |

For a signed-sync Cissa sender and Thoth receiver, declare
`ccf-signed-producer-sync-v1` explicitly. Persist batch ID, sequence, predecessor
hash, and signature across retries. The receiver must resolve credential state
from its configured trust source. The reference receipt verifier takes an ordered
prefix of retained producer batches from genesis; supplying only a predecessor
hash or a producer-supplied credential does not provide that evidence.

Exercise both successful transfers and the rejection cases above through the
actual application APIs. Include duplicate retries, an out-of-order successor
that resumes after its predecessor arrives, altered transcript/audio content,
and a credential expiring exactly at batch creation time. Verify that rejected
content is not activated or admitted and that receipts report the outcome the
receiver actually established.

Keep the [capture interruption tests](capture-boundary.md) in the build plan.
Reliable capture/spool recovery and archive admission are separate boundaries;
passing the schema reference suite does not establish either application's
crash recovery. Record the sender and receiver revisions, declarations, fixture
inputs, and observed receipts when these cross-application checks run.
