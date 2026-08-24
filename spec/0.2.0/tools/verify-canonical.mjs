import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  blobContentCommitment,
  canonicalDigest,
  canonicalize,
  compartmentCommitment,
  objectHash,
  semanticCatalogRoot,
  submissionHash,
} from '../../0.1.2/tools/ccf-jcs.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BASE = path.resolve(ROOT, '..', '0.1.2');
const VECTORS = path.join(BASE, 'vectors');
const EXAMPLE = path.join(BASE, 'examples', 'personal-archive');
let checks = 0;

function check(condition, label) {
  checks += 1;
  if (!condition) throw new Error(`FAIL: ${label}`);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

const canonicalization = readJson(path.join(VECTORS, 'canonicalization.json'));
for (const vector of canonicalization.cases) {
  check(canonicalize(vector.value) === vector.expected, `canonical ${vector.name}`);
  check(
    canonicalDigest('ccf:canonicalization-vector:v1', vector.value) === vector.digest,
    `canonical digest ${vector.name}`,
  );
}

const objects = readJson(path.join(VECTORS, 'object-hashes.json'));
for (const [kind, vector] of Object.entries(objects)) {
  check(vector.header.spec === 'ccf/0.1.2', `${kind} portable format remains 0.1.2`);
  check(
    compartmentCommitment(kind, 'structural', vector.structural) === vector.expected_structural_commitment,
    `${kind} structural commitment`,
  );
  check(
    compartmentCommitment(kind, 'semantic', vector.semantic) === vector.expected_semantic_commitment,
    `${kind} semantic commitment`,
  );
  check(objectHash(vector.header) === vector.expected_object_hash, `${kind} object hash`);
}
check(
  blobContentCommitment(
    objects.blob.semantic.content.content_salt,
    fs.readFileSync(path.join(EXAMPLE, 'segment-1842.wav')),
  ) === objects.blob.expected_content_commitment,
  'Blob content commitment',
);

const batch = readJson(path.join(VECTORS, 'producer-batch.json')).batch;
const submissionVectors = readJson(path.join(VECTORS, 'submission-hashes.json'));
const submissions = [...batch.records, ...batch.links, ...batch.blobs];
for (const vector of [
  ...submissionVectors.records,
  ...submissionVectors.links,
  ...submissionVectors.blobs,
]) {
  const submission = submissions.find((item) => item.id === vector.id);
  check(Boolean(submission), `submission present ${vector.id}`);
  check(submissionHash(submission) === vector.expected_submission_hash, `submission hash ${vector.id}`);
}

const draftCatalog = readJson(path.join(ROOT, 'semantic-catalog.json'));
const { root: draftRoot, ...draftCatalogWithoutRoot } = draftCatalog;
check(semanticCatalogRoot(draftCatalogWithoutRoot) === draftRoot, 'draft semantic catalog root');
check(
  draftCatalog.portable_object_formats.length === 1
    && draftCatalog.portable_object_formats[0] === 'ccf/0.1.2',
  'draft preserves the 0.1.2 portable object format',
);

console.log(`CCF Canonical Store inherited vectors pass: ${checks} checks.`);
