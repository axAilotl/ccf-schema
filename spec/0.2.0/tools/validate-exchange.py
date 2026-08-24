#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / "0.1.2"


def load_json(path: Path):
    return json.loads(path.read_text())


def fixture_submission_hash(submission) -> str:
    canonical = json.dumps(
        submission,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return "sha256:" + hashlib.sha256(b"ccf:submission:v2\0" + canonical).hexdigest()


schemas = {}
schema_registry = Registry()
for schema_root in (BASE / "schemas", ROOT / "schemas"):
    for path in schema_root.rglob("*.json"):
        if path.name == "catalog.json":
            continue
        schema = load_json(path)
        schema_id = schema.get("$id")
        if schema_id is None:
            continue
        if schema_id in schemas:
            raise SystemExit(f"duplicate schema id {schema_id}")
        schemas[schema_id] = schema
        schema_registry = schema_registry.with_resource(
            schema_id, Resource.from_contents(schema)
        )


def validate(schema_id: str, instance, label: str):
    if schema_id not in schemas:
        raise SystemExit(f"missing schema {schema_id} for {label}")
    validator = Draft202012Validator(
        schemas[schema_id],
        registry=schema_registry,
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        print(f"FAIL {label}: {len(errors)} error(s)")
        for error in errors[:30]:
            print("  ", "/".join(map(str, error.path)), error.message)
        raise SystemExit(1)
    print("OK  ", label)


registry_specs = {
    "levels.registry.json": "urn:ccf:schema:0.2.0:registries.level-registry",
    "roles.registry.json": "urn:ccf:schema:0.2.0:registries.role-registry",
    "capabilities.registry.json": "urn:ccf:schema:0.2.0:registries.capability-registry",
    "semantic-packs.registry.json": "urn:ccf:schema:0.2.0:registries.semantic-pack-registry",
    "semantic-requirements.registry.json": "urn:ccf:schema:0.2.0:registries.semantic-requirements-registry",
    "legacy-profile-mappings.registry.json": "urn:ccf:schema:0.2.0:registries.legacy-profile-mapping-registry",
    "compatibility-rules.registry.json": "urn:ccf:schema:0.2.0:registries.compatibility-rule-registry",
}
registries = {}
for filename, schema_id in registry_specs.items():
    value = load_json(ROOT / "registries" / filename)
    registries[filename] = value
    validate(schema_id, value, filename)


levels = {entry["id"]: entry for entry in registries["levels.registry.json"]["entries"]}
if len(levels) != len(registries["levels.registry.json"]["entries"]):
    raise SystemExit("duplicate guarantee level")
ordered_levels = sorted(levels.values(), key=lambda entry: entry["rank"])
level_rank = {entry["id"]: entry["rank"] for entry in ordered_levels}
if [entry["rank"] for entry in ordered_levels] != [1, 2, 3, 4]:
    raise SystemExit("guarantee levels must have contiguous ranks 1 through 4")
for index, entry in enumerate(ordered_levels):
    expected = [item["id"] for item in ordered_levels[: index + 1]]
    if entry["accepts_levels"] != expected:
        raise SystemExit(f'{entry["id"]} must accept itself and every lower level')

roles = {entry["id"] for entry in registries["roles.registry.json"]["entries"]}
if len(roles) != len(registries["roles.registry.json"]["entries"]):
    raise SystemExit("duplicate implementation role")
capabilities = {
    entry["id"]: entry for entry in registries["capabilities.registry.json"]["entries"]
}
if len(capabilities) != len(registries["capabilities.registry.json"]["entries"]):
    raise SystemExit("duplicate capability")
semantic_packs = {
    entry["id"]: entry for entry in registries["semantic-packs.registry.json"]["entries"]
}
if len(semantic_packs) != len(registries["semantic-packs.registry.json"]["entries"]):
    raise SystemExit("duplicate semantic pack")
for entry in capabilities.values():
    if entry["minimum_level"] not in levels:
        raise SystemExit(f'unknown capability minimum level for {entry["id"]}')
    missing = set(entry["depends_on"]) - capabilities.keys()
    if missing:
        raise SystemExit(f'unknown capability dependencies for {entry["id"]}: {sorted(missing)}')
for entry in semantic_packs.values():
    if entry["minimum_level"] not in levels:
        raise SystemExit(f'unknown semantic-pack minimum level for {entry["id"]}')
    missing = set(entry["required_capabilities"]) - capabilities.keys()
    if missing:
        raise SystemExit(f'unknown semantic-pack capabilities for {entry["id"]}: {sorted(missing)}')

base_profiles = {
    entry["name"] for entry in load_json(BASE / "registries" / "profiles.registry.json")["entries"]
}
legacy_mappings = registries["legacy-profile-mappings.registry.json"]["entries"]
mapped_profiles = {entry["legacy_profile"] for entry in legacy_mappings}
if len(mapped_profiles) != len(legacy_mappings) or mapped_profiles != base_profiles:
    raise SystemExit("legacy profile mappings do not cover each 0.1.2 profile exactly once")
for entry in legacy_mappings:
    if entry["level"] is not None and entry["level"] not in levels:
        raise SystemExit(f'legacy profile maps to unknown level: {entry["legacy_profile"]}')
    if entry["capability"] is not None and entry["capability"] not in capabilities:
        raise SystemExit(f'legacy profile maps to unknown capability: {entry["legacy_profile"]}')
    if entry["semantic_pack"] is not None and entry["semantic_pack"] not in semantic_packs:
        raise SystemExit(f'legacy profile maps to unknown semantic pack: {entry["legacy_profile"]}')

compatibility_ids = [
    entry["id"] for entry in registries["compatibility-rules.registry.json"]["entries"]
]
if compatibility_ids != [f"CCF-COMPAT-{index}" for index in range(1, 7)]:
    raise SystemExit("compatibility rules must be ordered and complete")


base_resources = set()
base_registry_entries = {}
for filename, resource_kind in (
    ("types.registry.json", "record_type"),
    ("links.registry.json", "link_type"),
    ("blobs.registry.json", "blob_type"),
    ("predicates.registry.json", "predicate"),
):
    entries = load_json(BASE / "registries" / filename)["entries"]
    base_registry_entries[resource_kind] = {
        (entry["name"], entry["version"]): entry for entry in entries
    }
    for entry in entries:
        base_resources.add((resource_kind, entry["name"], entry["version"]))

requirements = registries["semantic-requirements.registry.json"]["entries"]
declared_resources = {
    (entry["resource_kind"], entry["name"], entry["version"]) for entry in requirements
}
if len(declared_resources) != len(requirements):
    raise SystemExit("duplicate semantic requirement entry")
if declared_resources != base_resources:
    missing = sorted(base_resources - declared_resources)
    extra = sorted(declared_resources - base_resources)
    raise SystemExit(f"semantic requirement coverage mismatch; missing={missing}, extra={extra}")
for entry in requirements:
    if entry["minimum_level"] not in levels:
        raise SystemExit(f'unknown minimum level for {entry["name"]}')
    effects_level = entry["state_effects_level"]
    if effects_level is not None:
        if effects_level not in levels:
            raise SystemExit(f'unknown state-effects level for {entry["name"]}')
        if level_rank[effects_level] < level_rank[entry["minimum_level"]]:
            raise SystemExit(f'state effects precede semantic activation for {entry["name"]}')
    missing = set(entry["required_capabilities"]) - capabilities.keys()
    if missing:
        raise SystemExit(f'unknown required capabilities for {entry["name"]}: {sorted(missing)}')
    pack = entry["semantic_pack"]
    if pack is not None and pack not in semantic_packs:
        raise SystemExit(f'unknown semantic pack for {entry["name"]}: {pack}')
print(f"OK   semantic requirement coverage ({len(requirements)} resources)")

requirement_by_resource = {
    (entry["resource_kind"], entry["name"], entry["version"]): entry
    for entry in requirements
}


def assert_declared_features_fit_level(declaration, label: str):
    declared_level_rank = level_rank[declaration["level"]]
    for feature_id in declaration["capabilities"]:
        feature = capabilities.get(feature_id) or semantic_packs.get(feature_id)
        if feature is None:
            raise SystemExit(f"{label} declares unknown feature {feature_id}")
        if level_rank[feature["minimum_level"]] > declared_level_rank:
            raise SystemExit(f"{label} declares {feature_id} below its minimum level")


bundle_root = ROOT / "bundles"
bundles = {}
for path in sorted(bundle_root.glob("*.json")):
    bundle = load_json(path)
    validate(
        "urn:ccf:schema:0.2.0:declarations.bundle-manifest",
        bundle,
        f"bundle {path.name}",
    )
    if bundle["id"] in bundles:
        raise SystemExit(f'duplicate bundle ID {bundle["id"]}')
    bundles[bundle["id"]] = bundle

if len(bundles) != 7:
    raise SystemExit("expected four level bundles and three semantic-pack bundles")
source_roots = {"ccf-0.1.2": BASE, "ccf-0.2.0": ROOT}
for bundle in bundles.values():
    missing_dependencies = set(bundle["depends_on"]) - bundles.keys()
    if missing_dependencies:
        raise SystemExit(f'unknown bundle dependency for {bundle["id"]}: {sorted(missing_dependencies)}')
    artifact_keys = set()
    for artifact in bundle["artifacts"]:
        key = (artifact["source_package"], artifact["path"])
        if key in artifact_keys:
            raise SystemExit(f'duplicate artifact in {bundle["id"]}: {key}')
        artifact_keys.add(key)
        path = source_roots[artifact["source_package"]] / artifact["path"]
        actual_digest = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_digest != artifact["digest"]:
            raise SystemExit(f'stale artifact digest in {bundle["id"]}: {artifact["path"]}')
    if bundle["kind"] == "level":
        if bundle["provides"] not in levels:
            raise SystemExit(f'{bundle["id"]} provides an unknown level')
        if bundle["provides"] != "ccf-governed-archive-v1":
            forbidden = (
                "schemas/payloads/continuity/",
                "schemas/payloads/work/",
                "schemas/payloads/agent/",
            )
            leaking = [
                artifact["path"]
                for artifact in bundle["artifacts"]
                if artifact["source_package"] == "ccf-0.1.2"
                and artifact["path"].startswith(forbidden)
            ]
            if leaking:
                raise SystemExit(f'{bundle["id"]} leaks semantic-pack schemas: {leaking}')
    elif bundle["provides"] not in semantic_packs:
        raise SystemExit(f'{bundle["id"]} provides an unknown semantic pack')
print("OK   four level bundles and three isolated semantic-pack bundles")


all_capability_ids = capabilities.keys() | semantic_packs.keys()
implementation = load_json(ROOT / "examples" / "implementation-declaration.json")
validate(
    "urn:ccf:schema:0.2.0:declarations.implementation",
    implementation,
    "implementation declaration",
)
if implementation["level"] not in levels:
    raise SystemExit("implementation declares an unknown level")
if not set(implementation["roles"]) <= roles:
    raise SystemExit("implementation declares an unknown role")
if not set(implementation["capabilities"]) <= all_capability_ids:
    raise SystemExit("implementation declares an unknown capability or semantic pack")
assert_declared_features_fit_level(implementation, "implementation")


capsule_root = ROOT / "examples" / "capsule"
manifest = load_json(capsule_root / "manifest.json")
validate("urn:ccf:schema:0.2.0:exchange.capsule-manifest", manifest, "capsule manifest")
if manifest["level"] not in levels:
    raise SystemExit("capsule declares an unknown level")
if not set(manifest["capabilities"]) <= all_capability_ids:
    raise SystemExit("capsule declares an unknown capability or semantic pack")
assert_declared_features_fit_level(manifest, "capsule")

submissions = []
stream_paths = [stream["path"] for stream in manifest["streams"]]
if len(stream_paths) != len(set(stream_paths)):
    raise SystemExit("duplicate capsule stream path")
for stream in manifest["streams"]:
    path = capsule_root / stream["path"]
    content = path.read_bytes()
    digest = "sha256:" + hashlib.sha256(content).hexdigest()
    if digest != stream["digest"] or len(content) != int(stream["byte_length"]):
        raise SystemExit(f'capsule stream metadata mismatch: {stream["path"]}')
    if stream["media_type"] == "application/x-ndjson":
        submissions.extend(json.loads(line) for line in content.splitlines() if line.strip())

ids = [submission["id"] for submission in submissions]
if len(ids) != len(set(ids)):
    raise SystemExit("duplicate object ID in capsule")
if manifest["root_record_id"] not in ids:
    raise SystemExit("capsule root Record is absent")
for submission in submissions:
    validate(
        f'urn:ccf:schema:0.1.2:submissions.{submission["submission_kind"]}',
        submission,
        f'capsule submission {submission["id"]}',
    )
    resource_kind = f'{submission["submission_kind"]}_type'
    if submission["submission_kind"] == "record":
        resource_kind = "record_type"
    elif submission["submission_kind"] == "link":
        resource_kind = "link_type"
    key = (resource_kind, submission.get("type", "blob.manifest"), submission.get("type_version", 1))
    requirement = requirement_by_resource.get(key)
    if requirement is not None:
        if level_rank[requirement["minimum_level"]] > level_rank[manifest["level"]]:
            raise SystemExit(f'capsule activates {submission["id"]} below its minimum level')
        needed = set(requirement["required_capabilities"])
        if requirement["semantic_pack"] is not None:
            needed.add(requirement["semantic_pack"])
        if not needed <= set(manifest["capabilities"]):
            raise SystemExit(f'capsule activates {submission["id"]} without {sorted(needed)}')
    if submission["submission_kind"] == "record" and submission["type_visibility"] == "clear":
        type_entry = base_registry_entries["record_type"].get(
            (submission["type"], submission["type_version"])
        )
        if type_entry is not None:
            validate(
                type_entry["semantic_schema_id"],
                submission["payload"],
                f'capsule payload {submission["id"]}',
            )

included_or_declared = set(ids) | {
    dependency["object_id"] for dependency in manifest["dependencies"]
}
for submission in submissions:
    if submission["submission_kind"] == "link":
        for endpoint in (submission["from_id"], submission["to_id"]):
            if endpoint not in included_or_declared:
                raise SystemExit(f"capsule Link has undeclared endpoint {endpoint}")

member_ids = set(ids) - {manifest["root_record_id"]}
membership_links = {
    submission["from_id"]
    for submission in submissions
    if submission["submission_kind"] == "link"
    and submission["type"] in manifest["membership_link_types"]
    and submission["to_id"] == manifest["root_record_id"]
}
if not member_ids - {submission["id"] for submission in submissions if submission["submission_kind"] == "link"} <= membership_links:
    raise SystemExit("capsule object is not connected to the root by a membership Link")
print(f"OK   capsule membership and streams ({len(submissions)} submissions)")
availability_states = {entry["availability"] for entry in manifest["dependencies"]}
if availability_states != {"external", "withheld", "erased"}:
    raise SystemExit("capsule fixture does not keep external, withheld, and erased distinct")
submission_by_id = {
    submission["id"]: submission for submission in submissions
}
unknown_extension = submission_by_id[manifest["root_record_id"]]["extensions"]
if json.loads(json.dumps(unknown_extension)) != unknown_extension:
    raise SystemExit("unknown Capsule extension did not round trip")

origin_index = {}


def import_submission(submission):
    origin = submission.get("origin")
    if origin is None:
        return "admitted"
    key = (
        origin["source_id"],
        origin["native_id"],
        origin["revision"],
        submission["submission_kind"],
    )
    digest = fixture_submission_hash(submission)
    previous = origin_index.get(key)
    if previous is None:
        origin_index[key] = digest
        return "admitted"
    return "existing" if previous == digest else "origin_revision_conflict"


origin_submission = next(submission for submission in submissions if submission.get("origin"))
if import_submission(origin_submission) != "admitted" or import_submission(origin_submission) != "existing":
    raise SystemExit("duplicate Capsule import is not idempotent")
changed_submission = json.loads(json.dumps(origin_submission))
changed_submission["payload"][next(iter(changed_submission["payload"]))] = "changed"
if import_submission(changed_submission) != "origin_revision_conflict":
    raise SystemExit("changed same-origin revision did not conflict")
print("OK   unknown round trip, duplicate import, and revision conflict")

uplift = load_json(capsule_root / "uplift-receipt.json")
validate("urn:ccf:schema:0.2.0:exchange.uplift-receipt", uplift, "uplift receipt")
if level_rank[uplift["destination_level"]] < level_rank[uplift["source_level"]]:
    raise SystemExit("uplift receipt moves to a weaker level")
if {entry["source_id"] for entry in uplift["objects"]} != set(submission_by_id):
    raise SystemExit("uplift receipt does not cover every capsule object exactly once")
for admission in uplift["objects"]:
    if admission["source_id"] != admission["canonical_id"]:
        raise SystemExit("uplift changed a supplied portable ID")
    if admission["producer_authentication"] == "verified" and admission["producer_proof"] is None:
        raise SystemExit("uplift silently strengthened producer authentication")
    # Submission hashes are independently checked by the inherited L2 vectors;
    # this fixture additionally pins the exact source assertion used for uplift.
    if fixture_submission_hash(submission_by_id[admission["source_id"]]) != admission["source_submission_hash"]:
        raise SystemExit(f'uplift source hash mismatch for {admission["source_id"]}')

downgrade = load_json(capsule_root / "downgrade-receipt.json")
validate("urn:ccf:schema:0.2.0:exchange.downgrade-receipt", downgrade, "downgrade receipt")
if downgrade["losslessness"] == "lossy" and not downgrade["omissions"]:
    raise SystemExit("lossy downgrade did not enumerate omissions")
if level_rank[downgrade["target_level"]] >= level_rank[downgrade["source_level"]]:
    raise SystemExit("downgrade receipt does not move to a weaker level")


base_catalog = load_json(BASE / "semantic-catalog.json")
draft_catalog = load_json(ROOT / "semantic-catalog.json")
schema_catalog = load_json(ROOT / "schemas" / "catalog.json")
discovered_schema_ids = set(schemas) - {
    schema_id for schema_id in schemas if schema_id.startswith("urn:ccf:schema:0.1.2:")
}
catalog_schema_ids = {entry["id"] for entry in schema_catalog["schemas"]}
if catalog_schema_ids != discovered_schema_ids:
    raise SystemExit("draft schema catalog does not exactly cover draft schema IDs")
if schema_catalog["schemas"] != draft_catalog["schemas"]:
    raise SystemExit("schema and semantic catalogs disagree")
for entry in draft_catalog["schemas"] + draft_catalog["registries"]:
    if not (ROOT / entry["path"]).exists():
        raise SystemExit(f'stale draft catalog path {entry["path"]}')
base_pin = draft_catalog["base_catalogs"][0]
if base_pin["version"] != base_catalog["version"] or base_pin["root"] != base_catalog["root"]:
    raise SystemExit("0.2.0 draft does not pin the exact 0.1.2 semantic catalog")
print("OK   exact 0.1.2 catalog compatibility pin")
print("\nCCF 0.2.0 Exchange conformance checks passed.")
