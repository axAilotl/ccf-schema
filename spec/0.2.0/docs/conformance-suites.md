# Tiered conformance suites

The draft Makefile exposes cumulative level checks while keeping their direct
oracles separate.

| Suite | Direct proof boundary |
|---|---|
| `check-exchange` | Registries, declarations, submission schemas and semantic payloads, references, streams, dependencies, requirements, Capsule, uplift, and downgrade |
| `check-canonical` | Exchange plus inherited JCS, commitments, object hashes, Blob content commitment, and submission hashes |
| `check-verified` | Canonical plus commit signing, Merkle roots, catalog pins, mindpack streams, parent chain, head, and member/object correspondence |
| `check-governed` | Verified plus 0.1.2 governance, authority, lineage, suppression, projection, and PostgreSQL fixtures |

`check-exchange` is the acceptance boundary for a notebook importer. It does not
run canonical hashing, archive signatures, policy evaluation, or PostgreSQL.
`check-canonical` adds no journal or governance requirement. The destructive and
database-backed checks remain at Governed Archive.

Capability suites are independent of this cumulative chain. A deployment runs
the suite for each capability it declares; absence of a capability is not a
failure of its guarantee level.

