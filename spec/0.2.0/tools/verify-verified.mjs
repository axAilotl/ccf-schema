import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  commitSigningDigest,
  merkleRoot,
  objectHash,
  semanticCatalogRoot,
} from '../../0.1.2/tools/ccf-jcs.mjs';
import { actualStreams } from '../../0.1.2/tools/mindpack-manifest.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BASE = path.resolve(ROOT, '..', '0.1.2');
const VECTORS = path.join(BASE, 'vectors');
const MINDPACK = path.join(BASE, 'examples', 'mindpack');
let checks = 0;

function check(condition, label) {
  checks += 1;
  if (!condition) throw new Error(`FAIL: ${label}`);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function readNdjson(file) {
  return fs.readFileSync(file, 'utf8').trim().split('\n').filter(Boolean).map(JSON.parse);
}

const merkleVectors = readJson(path.join(VECTORS, 'merkle.json'));
check(merkleRoot([]) === merkleVectors.empty_expected, 'empty Merkle root');
for (const name of ['commit1', 'commit2']) {
  check(
    merkleRoot(merkleVectors[name].members) === merkleVectors[name].expected_root,
    `${name} Merkle root`,
  );
}

const publicKey = fs.readFileSync(path.join(VECTORS, 'archive-ed25519-public.pem'));
const commitVectors = readJson(path.join(VECTORS, 'commit-signing.json'));
for (const [name, vector] of Object.entries(commitVectors)) {
  const digest = commitSigningDigest(
    vector.signing_header,
    vector.structural_content_without_signature,
  );
  check(
    `sha256:${digest.toString('hex')}` === vector.expected_signing_digest,
    `${name} signing digest`,
  );
  check(
    crypto.verify(null, digest, publicKey, Buffer.from(vector.signature, 'base64url')),
    `${name} archive signature`,
  );
  check(objectHash(vector.header) === vector.expected_commit_hash, `${name} commit hash`);
}

const baseCatalog = readJson(path.join(BASE, 'semantic-catalog.json'));
const { root: baseRoot, ...baseCatalogWithoutRoot } = baseCatalog;
check(semanticCatalogRoot(baseCatalogWithoutRoot) === baseRoot, 'base semantic catalog root');

const manifest = readJson(path.join(MINDPACK, 'manifest.json'));
const actualStreamMap = new Map(actualStreams(MINDPACK).map((entry) => [entry.path, entry]));
const manifestStreamMap = new Map(manifest.streams.map((entry) => [entry.path, entry]));
check(
  actualStreamMap.size === manifestStreamMap.size
    && [...actualStreamMap].every(
      ([streamPath, entry]) => JSON.stringify(entry) === JSON.stringify(manifestStreamMap.get(streamPath)),
    ),
  'mindpack stream inventory and digests',
);
const commits = readNdjson(path.join(MINDPACK, 'integrity', 'commits.ndjson'));
const members = readNdjson(path.join(MINDPACK, 'integrity', 'members.ndjson'));
check(commits.length === Number(manifest.counts.commits), 'mindpack commit count');
check(commits[0].commit_hash === manifest.genesis_commit_hash, 'mindpack genesis pin');
check(commits.at(-1).commit_hash === manifest.head_commit_hash, 'mindpack head pin');
check(commits.at(-1).sequence === manifest.head_sequence, 'mindpack head sequence');
check(manifest.semantic_catalog_root === baseRoot, 'mindpack catalog pin');

for (let index = 0; index < commits.length; index += 1) {
  const commit = commits[index];
  const expectedParent = index === 0 ? null : commits[index - 1].commit_hash;
  check(commit.parent_commit_hash === expectedParent, `commit ${commit.sequence} parent`);
  const commitMembers = members.filter((member) => member.commit_sequence === commit.sequence);
  check(merkleRoot(commitMembers) === commit.merkle_root, `commit ${commit.sequence} membership root`);
}

const headers = [
  ...readNdjson(path.join(MINDPACK, 'objects', 'records.ndjson')),
  ...readNdjson(path.join(MINDPACK, 'objects', 'links.ndjson')),
  ...readNdjson(path.join(MINDPACK, 'objects', 'blobs.ndjson')),
];
const headerById = new Map(headers.map((header) => [header.id, header]));
for (const member of members) {
  check(headerById.get(member.object_id)?.object_hash === member.object_hash, `member ${member.object_id}`);
}

console.log(`CCF Verified Archive inherited history checks pass: ${checks} checks.`);
