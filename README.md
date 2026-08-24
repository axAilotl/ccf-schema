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
```

## Verify the package

The checks require Node.js, Python, Docker, and `uv`. The PostgreSQL fixture
starts a disposable PostgreSQL 16 container with pgvector.

```bash
make check
```

To prove that every generated artifact is reproducible:

```bash
make reproduce
```

To build a deterministic release ZIP and checksum:

```bash
make package
```

## Status

CCF 0.1.2 is the current interoperability release. The package passes its
published vectors, schema checks, mindpack verification, portable conformance
cases, and PostgreSQL reference fixture.

## License

[MIT](LICENSE)
