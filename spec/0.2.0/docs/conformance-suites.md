# Tiered conformance suites

The draft Makefile exposes cumulative level checks while keeping their direct
oracles separate.

| Suite | Direct proof boundary |
|---|---|
| `check-exchange` | Registries, declarations, submission schemas and semantic payloads, typed references, streams, resolved catalog dependencies, type and predicate requirements, Capsule, uplift, and exact downgrade inventories |
| `check-canonical` | Exchange plus inherited JCS, adversarial number/key ordering, commitments, every available compartment and Blob body, object hashes, completed and pending uplift, exact origin idempotency, atomic conflict behavior, and unavailable states |
| `check-verified` | Canonical plus commit signing, trusted-genesis signer binding, signature/stream/parent/Merkle tamper rejection, catalog pins, restore identity, downgrade source authentication, foreign merge, head, and member/object correspondence |
| `check-governed` | Verified plus 0.1.2 governance, authority, lineage, suppression, projection, and PostgreSQL fixtures |

`check-exchange` is the acceptance boundary for a notebook importer. It does not
verify portable object hashes, archive signatures, policy evaluation, or PostgreSQL.
Catalog identity still requires the inherited JCS artifact digests: the runner
recomputes catalog roots and schema/registry digests before resolving required
Capsule dependencies by kind, identifier, and digest.
`check-canonical` adds no journal or governance requirement. The destructive and
database-backed checks remain at Governed Archive.

The Exchange runner registers the inherited `ccf-uint64` JSON Schema format and
tests both the maximum value and overflow rejection. A validator that silently
treats that custom format as an unknown annotation does not satisfy CCF schema
validation; signed-sync additionally requires producer sequences to be nonzero
canonical decimal strings.

Canonical Store and Verified Archive publish their state-transition cases under
`vectors/`. The draft source package's reference verifiers execute those input/expected-output
cases, including complete-Capsule replay, atomic rollback of staged object and
origin writes, a completed Capsule uplift receipt with pinned fixture salts and
expected commitments/hashes, restore admission coordinates, and a foreign merge that writes
portable objects unchanged into a distinct archive/epoch and signs the
destination Merkle commit. An implementation claiming a level runs the same
vectors through its own adapter; passing only this repository's reference
verifier proves the standard package, not a third-party implementation.
The conformance-only uplift resolution mapping is specified in
`canonical-uplift-vector.md`; production salts remain random.

Conformance packages and installable distribution bundles are deliberately
different boundaries. `spec/0.2.0` is the conformance package and includes its
tools, fixtures, vectors, Makefiles, and inherited pinned 0.1.2 test inputs.
`bundles/` names only the runtime schemas, registries, and examples needed to
implement a level or capability; it never distributes private test keys or
claims that a manifest alone is an executable test environment.

Capability suites are independent of this cumulative chain. The draft currently
publishes `check-capability-signed-producer-sync`; its registry entry names that
target. Encryption, selective erasure, witnessing, succession, and external-KMS
entries intentionally have null suite fields until independent vectors exist.
A deployment may declare one of those capabilities only with its own equivalent
operational evidence; this repository does not confer the claim. Those suites
are release blockers for turning this Working Draft into a complete 0.2 release.
The base Exchange validator deliberately refuses a `verified` producer receipt;
only the signed-sync capability verifier may accept it after resolving the
retained batch against an explicit credential trust anchor, validating the
ordered, fully hash-pinned canonical credential lineage and revocation state at
batch time, and checking the payload and lineage validity intervals
(`valid_from <= created_at < expires_at`, with null expiry unbounded). Both
ingestion and receipts use the same check. Receipt verification also replays an
ordered, authenticated producer-batch prefix from genesis through the retained
batch, checking sequence and predecessor hashes through the ingestion path.
A signature alone cannot grant the signed-sync claim; missing predecessor
evidence makes receipt verification fail. It then checks the proof digest and
covered submission. The published
trust vector models either an authenticated archive result or an out-of-band
deployment trust store; a credential bundled by an untrusted producer is not a
trust anchor.

The continuity, work, and agent registries likewise name independent
`check-semantic-pack-*` targets. Each target proves exact registered-resource,
payload-schema, and distribution-bundle coverage without raising the
implementation's guarantee level.

The level targets also run `tools/check-reference-boundaries.py` against temporary
package copies. Exchange mutations refresh unsigned stream and bundle checksums
so rejection must come from dependency resolution or activation/reference checks.
Canonical and Verified mutations change available bodies while refreshing only
unsigned stream metadata, leaving committed hashes and the signed journal intact.
Tests include declared unavailable references and opaque extension/literal values
that must remain acceptable. Original 0.1.2 fixtures are never modified.
