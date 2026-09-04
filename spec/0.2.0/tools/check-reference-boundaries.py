#!/usr/bin/env python3
"""Mutation regressions against the real draft runners, in disposable package copies."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[2]
MISSING = 'urn:ccf:record:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'


def write_json(path, value):
    path.write_text(json.dumps(value) + '\n')


def refresh_stream(root, path):
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    content = path.read_bytes()
    for stream in manifest['streams']:
        if stream['path'] == path.relative_to(root).as_posix():
            stream.update(digest='sha256:' + hashlib.sha256(content).hexdigest(),
                          byte_length=str(len(content)))
    write_json(manifest_path, manifest)


class PackageCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='ccf-boundary-')
        self.addCleanup(self.temporary.cleanup)
        self.spec = Path(self.temporary.name) / 'spec'
        shutil.copytree(SOURCE, self.spec)
        self.draft = self.spec / '0.2.0'
        self.capsule = self.draft / 'examples/capsule'

    def run_tool(self, name):
        executable = sys.executable if name.endswith('.py') else 'node'
        return subprocess.run([executable, str(self.draft / 'tools' / name)],
                              capture_output=True, text=True)

    def exchange(self, error=None):
        # Distribution checksums are unsigned packaging metadata, not the oracle.
        result = self.run_tool('build-bundles.mjs')
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_tool('validate-exchange.py')
        if error is None:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, 'Altered Capsule was accepted')
            self.assertIn(error, result.stdout + result.stderr)

    def records(self, mutate):
        path = self.capsule / 'submissions/records.ndjson'
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        mutate(rows)
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        refresh_stream(self.capsule, path)

    def manifest(self, mutate):
        path = self.capsule / 'manifest.json'
        value = json.loads(path.read_text())
        mutate(value)
        write_json(path, value)


class ExchangeBoundaries(PackageCase):
    def test_catalog_digest(self):
        self.manifest(lambda m: [d.update(digest='sha256:' + '0' * 64)
                                 for d in m['catalog_dependencies']])
        self.exchange('unresolved required catalog dependency')

    def test_catalog_identifier(self):
        self.manifest(lambda m: m['catalog_dependencies'][0].update(identifier='unknown'))
        self.exchange('unresolved required catalog dependency')

    def test_schema_dependency_digest(self):
        self.manifest(lambda m: m['catalog_dependencies'].append(dict(
            kind='schema', identifier='urn:ccf:schema:0.1.2:submissions.record',
            digest='sha256:' + '0' * 64, required=True)))
        self.exchange('unresolved required catalog dependency')

    def test_catalog_artifact_bytes(self):
        path = self.spec / '0.1.2/schemas/payloads/semantic/entity.schema.json'
        value = json.loads(path.read_text())
        value['title'] = 'Altered local artifact'
        write_json(path, value)
        self.exchange('catalog artifact mismatch')

    def test_unknown_optional_catalog_can_be_preserved(self):
        self.manifest(lambda m: m['catalog_dependencies'].append(dict(
            kind='registry', identifier='org.example.opaque',
            digest='sha256:' + '0' * 64, required=False)))
        self.exchange()

    def assertion(self, predicate='ccf.work.works_on', literal=False):
        def mutate(rows):
            rows[1].update(type='semantic.assertion', payload=dict(
                subject={'ref': rows[0]['id']}, predicate=predicate,
                object={'value': MISSING, 'datatype': 'string'} if literal else {'ref': rows[2]['id']},
                scope={}, qualifiers={}, extensions={}))
        self.records(mutate)

    def test_predicate_pack(self):
        self.assertion()
        self.exchange('without')

    def test_predicate_pack_present(self):
        self.assertion()
        self.manifest(lambda m: m['capabilities'].append('ccf-work-pack-v1'))
        self.exchange()

    def test_unknown_predicate(self):
        self.assertion('org.example.unknown')
        self.exchange('unregistered')

    def test_recorded_by(self):
        self.records(lambda r: r[1].update(recorded_by=MISSING))
        self.exchange('undeclared reference recorded_by')

    def test_origin(self):
        self.records(lambda r: r[1]['origin'].update(source_id=MISSING))
        self.exchange('undeclared reference origin/source_id')

    def test_authority(self):
        self.records(lambda r: r[1]['claims']['authority'].update(asserted_by=MISSING))
        self.exchange('undeclared reference claims/authority/asserted_by')

    def test_lineage_predecessor(self):
        self.records(lambda r: r[1].update(lineage=dict(
            lineage_id='urn:ccf:lineage:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
            previous_head_id=MISSING, transition='amend',
            valid_from=r[1]['recorded_at'], expires_at=None)))
        self.exchange('undeclared reference lineage/previous_head_id')

    def test_payload_reference(self):
        self.assertion()
        self.manifest(lambda m: m['capabilities'].append('ccf-work-pack-v1'))
        self.records(lambda r: r[1]['payload'].update(object={'ref': MISSING}))
        self.exchange('undeclared reference payload/object/ref')

    def test_sealed_type_payload_reference(self):
        self.assertion()
        self.manifest(lambda m: m['capabilities'].append('ccf-work-pack-v1'))
        self.records(lambda r: r[1].update(type_visibility='sealed'))
        self.records(lambda r: r[1]['payload'].update(object={'ref': MISSING}))
        self.exchange('undeclared reference payload/object/ref')

    def test_provenance_array_reference(self):
        self.records(lambda r: r[1]['claims'].update(privacy=dict(
            data_subjects=[], data_classes=[], consent_refs=[MISSING],
            legal_basis_refs=[], subject_coverage='unknown')))
        self.exchange('undeclared reference claims/privacy/consent_refs/0')

    def test_payload_optional_reference(self):
        self.records(lambda r: r[2]['payload'].update(operator_id=MISSING))
        self.exchange('undeclared reference payload/operator_id')

    def test_literals_and_unknown_extensions_are_not_references(self):
        self.assertion(literal=True)
        self.manifest(lambda m: m['capabilities'].append('ccf-work-pack-v1'))
        self.records(lambda r: r[1]['extensions'].update(unknown={'ref': MISSING}))
        self.exchange()

    def test_declared_provenance_dependency(self):
        for availability in ('external', 'withheld', 'erased'):
            with self.subTest(availability=availability):
                self.records(lambda r: r[1].update(recorded_by=MISSING))
                self.manifest(lambda m: m['dependencies'].__setitem__(0, dict(
                    object_id=MISSING, availability=availability, reason='Outside scope',
                    locator=None, source_custody_proof='source:test',
                    unavailability_lineage_id=m['root_record_id'] if availability == 'erased' else None)))
                self.exchange()


class CanonicalBoundaries(PackageCase):
    runner = 'verify-canonical.mjs'

    def alter_body(self, compartment):
        root = self.spec / '0.1.2/examples/mindpack'
        path = next(p for p in (root / 'compartments/records').glob('*.semantic.json')
                    if 'text' in json.loads(p.read_text())['content'].get('payload', {}))
        path = path.with_name(path.name.replace('.semantic.json', f'.{compartment}.json'))
        value = json.loads(path.read_text())
        if compartment == 'semantic':
            value['content']['payload']['text'] = 'Altered stored transcript.'
        else:
            value['content']['extensions']['tampered'] = True
        write_json(path, value)
        refresh_stream(root, path)

    def reject(self, error):
        result = self.run_tool(self.runner)
        self.assertNotEqual(result.returncode, 0, 'Altered available body was accepted')
        self.assertIn(error, result.stdout + result.stderr)

    def test_semantic_body(self):
        self.alter_body('semantic')
        self.reject('semantic commitment')

    def test_structural_body(self):
        self.alter_body('structural')
        self.reject('structural commitment')

    def test_blob_bytes(self):
        root = self.spec / '0.1.2/examples/mindpack'
        path = next((root / 'blob-data').glob('*.bin'))
        content = bytearray(path.read_bytes())
        content[0] ^= 1
        path.write_bytes(content)
        refresh_stream(root, path)
        self.reject('Blob content commitment')


class VerifiedBoundaries(CanonicalBoundaries):
    runner = 'verify-verified.mjs'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('level', choices=['exchange', 'canonical', 'verified'])
    args = parser.parse_args()
    cls = {'exchange': ExchangeBoundaries, 'canonical': CanonicalBoundaries,
           'verified': VerifiedBoundaries}[args.level]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    sys.exit(not result.wasSuccessful())
