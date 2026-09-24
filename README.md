# Continuity Core Format

Continuity Core Format (CCF) is a small, portable format for a person's own
information: what exists, where it lives, where it came from, when it changed,
and how it relates to everything else.

CCF describes data; it does not have to hold it. Notes can stay in Obsidian,
pages in Notion, audio on a phone, papers on the web. CCF records point at those
things, fingerprint them with a hash, and link them together, so a summary can be
traced to its transcript, a transcript to its recording, and a meeting to the
people in it. Everything can be exported as plain files with every link intact.

## The format in brief

- Three object kinds: **Record** (a thing), **Link** (a relationship), and
  **Blob** (a pointer to bytes).
- UUIDv7 IDs, created on the device that makes the object and never changed.
- Each object records its source, creation and update times, a revision
  number, and a content hash.
- `status: inferred` marks what a model guessed; `accepted` marks what a person
  confirmed.
- Devices sync by exchanging objects; one deterministic rule picks the winner,
  and conflicts are flagged instead of blocking anything.
- An export is `manifest.json` plus `records.jsonl`, `links.jsonl`,
  `blobs.jsonl`, and optional `files/`.
- The only thing CCF writes into your own files is a single `ccf_id` line.

A typical object is 250–500 bytes.

## Current version

[CCF 0.3.0](spec/0.3.0/CCF-0.3.0-SPEC.md) (draft). It is a new format and is
not compatible with earlier versions.

```text
spec/0.3.0/
  CCF-0.3.0-SPEC.md   specification
  schemas/            JSON Schemas for Record, Link, Blob, and the export manifest
  vectors/            hash and merge test vectors
  examples/export/    a small example export
  tools/validate.py   validator (Python standard library only)
```

## Check

```bash
make check
```

To check your own export:

```bash
python3 spec/0.3.0/tools/validate.py export path/to/export
```

## History

CCF 0.1.2 and the 0.2.0 working draft are preserved on the `archive/0.2.0`
branch and the `ccf-0.2.0-draft` tag. They are retired.

## License

[MIT](LICENSE)
