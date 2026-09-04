import fs from 'node:fs';
import path from 'node:path';
import {
  blobContentCommitment,
  compartmentCommitment,
  objectHash,
} from '../../0.1.2/tools/ccf-jcs.mjs';

// Canonical integrity is independent of journal, governance, and availability
// policy. Missing bodies remain unavailable; every supplied body must verify.
export function verifyAvailableBodies(root, headers) {
  const expectedFiles = new Set();
  const ids = new Set();
  function require(condition, label, id) {
    if (!condition) throw new Error(`${label}: ${id}`);
  }
  for (const header of headers) {
    require(!ids.has(header.id), 'duplicate object ID', header.id);
    ids.add(header.id);
    require(header.spec === 'ccf/0.1.2', 'object spec', header.id);
    require(header.hash_profile === 'ccf-jcs-sha256-v2', 'object hash profile', header.id);
    require(objectHash(header) === header.object_hash, 'object hash', header.id);
    const uuid = header.id.slice(header.id.lastIndexOf(':') + 1);
    const bodies = {};
    for (const compartment of ['structural', 'semantic']) {
      const file = path.join(root, 'compartments', `${header.object_kind}s`, `${uuid}.${compartment}.json`);
      expectedFiles.add(file);
      if (!fs.existsSync(file)) continue;
      const envelope = JSON.parse(fs.readFileSync(file, 'utf8'));
      require(
        header[`${compartment}_commitment`] !== null
          && compartmentCommitment(header.object_kind, compartment, envelope)
            === header[`${compartment}_commitment`],
        `${compartment} commitment`, header.id,
      );
      bodies[compartment] = envelope.content;
    }
    if (header.object_kind !== 'blob') continue;
    const bytesPath = path.join(root, 'blob-data', `${uuid}.bin`);
    expectedFiles.add(bytesPath);
    if (!fs.existsSync(bytesPath)) continue;
    require(bodies.structural && bodies.semantic, 'Blob bytes require both compartments', header.id);
    const bytes = fs.readFileSync(bytesPath);
    require(String(bytes.length) === bodies.structural.byte_length, 'Blob byte length', header.id);
    require(
      blobContentCommitment(bodies.semantic.content_salt, bytes) === bodies.structural.content_commitment,
      'Blob content commitment', header.id,
    );
  }
  for (const directory of ['compartments', 'blob-data']) {
    const absolute = path.join(root, directory);
    if (!fs.existsSync(absolute)) continue;
    for (const entry of fs.readdirSync(absolute, { recursive: true, withFileTypes: true })) {
      if (entry.isDirectory()) continue;
      const file = path.join(entry.parentPath, entry.name);
      require(expectedFiles.has(file), 'body without a canonical header', file);
    }
  }
  return true;
}
