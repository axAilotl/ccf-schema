# Continuity Core Format

Continuity Core Format (CCF) is a local-first format for portable, person-owned
data. A CCF archive acts as a durable save file that can move between
applications without making one application the permanent owner of the data.

CCF defines records, relationships, files, provenance, policy, retention,
integrity history, import, export, and synchronization. Search indexes, vector
stores, graph views, summaries, and wiki pages remain rebuildable projections.

The format is suitable for:

- personal knowledge systems and notebooks;
- companion applications and assistants;
- capture, transcription, and research tools;
- local archives with optional multi-device synchronization;
- applications that need portable provenance and deletion records.

CCF does not define an application's interface, personality, model, prompts, or
product behavior. Those belong to the application layer.

## Current release

The current standards package is [CCF 0.1.2](spec/0.1.2/README.md). It includes:

- the consolidated normative specification;
- JSON Schemas and content-addressed registries;
- canonicalization, hashing, signing, and tamper vectors;
- a self-contained example archive and mindpack;
- OpenAPI and PostgreSQL reference envelopes;
- deterministic build and conformance tools.

## Layered-conformance working draft

[CCF 0.2.0](spec/0.2.0/README.md) is an additive Working Draft that separates
implementation roles, cumulative guarantee levels, optional capabilities, and
semantic packs. It also introduces CCF Capsule for scoped knowledge transfer
and tiered `check-exchange`, `check-canonical`, `check-verified`, and
`check-governed` suites.

The draft pins and reuses the 0.1.2 portable object and hash formats. It does not
change the published meaning of 0.1.2 or require existing objects to be
rewritten. CCF 0.1.2 remains the current interoperability release.

## Repository layout

```text
spec/0.1.2/
  CCF-0.1.2-SPEC.md   normative specification
  schemas/            JSON Schemas
  registries/         activated registries and profiles
  examples/           generated personal-archive and mindpack fixtures
  vectors/            executable interoperability vectors
  openapi/             reference API contract
  sql/                 reference PostgreSQL envelope
  tools/               build and verification tools
spec/0.2.0/
  CCF-0.2.0-DRAFT.md  layered-conformance working draft
  schemas/            declaration, registry, Capsule, and receipt schemas
  registries/         levels, roles, capabilities, packs, and requirements
  bundles/            level, capability, and semantic-pack manifests
  examples/capsule/   executable scoped-exchange fixture
  tools/              tiered conformance checks
```

## Verify the package

The checks require Node.js, Python, Docker, and `uv`. The PostgreSQL fixture
starts a disposable PostgreSQL 16 container with pgvector.

```bash
make check
```

To verify the default Exchange and Canonical Store boundaries of the 0.2.0
Working Draft:

```bash
make check-draft
```

The individual root targets are `check-draft-exchange`,
`check-draft-canonical`, `check-draft-verified`, `check-draft-governed`, and
`check-draft-signed-producer-sync`.

To prove that every generated artifact is reproducible:

```bash
make reproduce
```

To build a deterministic release ZIP and checksum:

```bash
make package
(cd spec && sha256sum -c ccf-0.1.2.zip.sha256)
```

## Status

CCF 0.1.2 is the current interoperability release. The package passes its
published vectors, schema checks, mindpack verification, portable conformance
cases, and PostgreSQL reference fixture.

## License

[MIT](LICENSE)
