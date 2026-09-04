import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { canonicalDigest, semanticCatalogRoot } from '../../0.1.2/tools/ccf-jcs.mjs';

// Resolve against computed artifact digests, never catalog assertions alone.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const resources = [];
for (const packageRoot of [path.resolve(root, '../0.1.2'), root]) {
  const catalog = JSON.parse(fs.readFileSync(path.join(packageRoot, 'semantic-catalog.json'), 'utf8'));
  const { root: digest, ...body } = catalog;
  if (semanticCatalogRoot(body) !== digest) throw new Error('semantic catalog root mismatch');
  resources.push({ kind: 'semantic_catalog', identifier: catalog.format, digest });
  for (const [kind, entries] of [['schema', catalog.schemas], ['registry', catalog.registries]]) {
    for (const entry of entries) {
      const artifact = JSON.parse(fs.readFileSync(path.join(packageRoot, entry.path), 'utf8'));
      const identifier = kind === 'schema' ? artifact.$id : artifact.registry;
      const actualDigest = canonicalDigest(`ccf:${kind}-artifact:v1`, artifact);
      if (identifier !== (entry.id ?? entry.name) || actualDigest !== entry.digest) {
        throw new Error(`catalog artifact mismatch: ${entry.path}`);
      }
      resources.push({ kind, identifier, digest: actualDigest });
    }
  }
}
console.log(JSON.stringify(resources));
