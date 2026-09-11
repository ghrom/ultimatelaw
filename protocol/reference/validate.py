#!/usr/bin/env python3
"""Dependency-free reference validator for Ultimate Law Protocol 1 streams."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PROTOCOL_ROOT.parent
ONTOLOGY_PATH = PROTOCOL_ROOT / "ontology" / "core.json"

PROTOCOL = "ultimate-law/1"
RECORD_TYPES = {
    "boundary",
    "consent",
    "agreement",
    "action",
    "evidence",
    "claim",
    "judgment",
    "mandate",
    "response",
    "resolution",
    "challenge",
    "correction",
}
BOUNDARY_KINDS = {"body", "property", "freedom", "agreement"}
AGENT_ID_RE = re.compile(r"^[a-z][a-z0-9+.-]*:.+$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EXTENSION_RE = re.compile(r"^x-[a-z0-9.-]+$")

COMMON_FIELDS = {"protocol", "id", "type", "issued_at", "issuer", "payload", "proof"}

REQUIRED_PAYLOAD_FIELDS = {
    "boundary": {"holder", "kind", "object", "protection"},
    "consent": {"grantor", "grantee", "action", "object", "scope", "state"},
    "agreement": {"parties", "terms_digest", "state"},
    "action": {"actor", "verb", "object", "occurred_at"},
    "evidence": {"statement", "source", "observed_at", "content_digest"},
    "claim": {
        "claimant",
        "respondent",
        "victim",
        "action_ref",
        "boundary_ref",
        "evidence_refs",
        "allegations",
    },
    "judgment": {
        "judge",
        "claim_ref",
        "evidence_refs",
        "dictionary_digest",
        "falsifiable",
        "findings",
    },
    "mandate": {"principal", "delegate", "judgment_ref", "powers", "kinds", "state"},
    "response": {"actor", "target", "basis", "action", "kind"},
    "resolution": {"victim", "judgment_ref", "mode", "moral_debt"},
    "challenge": {"target_ref", "grounds", "statement"},
    "correction": {"target_ref", "replacement_ref", "reason"},
}

ALLOWED_PAYLOAD_FIELDS = {
    "boundary": REQUIRED_PAYLOAD_FIELDS["boundary"],
    "consent": REQUIRED_PAYLOAD_FIELDS["consent"] | {"valid_until", "supersedes"},
    "agreement": REQUIRED_PAYLOAD_FIELDS["agreement"] | {"acceptance_refs"},
    "action": REQUIRED_PAYLOAD_FIELDS["action"] | {"boundary_ref", "consent_ref"},
    "evidence": REQUIRED_PAYLOAD_FIELDS["evidence"] | {"about_ref", "locator"},
    "claim": REQUIRED_PAYLOAD_FIELDS["claim"],
    "judgment": REQUIRED_PAYLOAD_FIELDS["judgment"],
    "mandate": REQUIRED_PAYLOAD_FIELDS["mandate"] | {"valid_until", "supersedes"},
    "response": REQUIRED_PAYLOAD_FIELDS["response"]
    | {
        "action_ref",
        "boundary_ref",
        "threat_state",
        "minimal_force",
        "causally_directed",
        "ends_when_crossing_ends",
        "judgment_ref",
        "mandate_ref",
    },
    "resolution": REQUIRED_PAYLOAD_FIELDS["resolution"] | {"restitution_ref"},
    "challenge": REQUIRED_PAYLOAD_FIELDS["challenge"] | {"evidence_refs"},
    "correction": REQUIRED_PAYLOAD_FIELDS["correction"],
}

REQUIRED_FINDINGS = {
    "causation",
    "boundary_crossing",
    "crossed_boundary_protection",
    "victim_status",
    "guilt",
    "forfeiture",
    "law_terms",
    "permitted_response_kinds",
    "restitution",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    record_id: str = "<stream>"

    def __str__(self) -> str:
        return f"{self.code} {self.record_id}: {self.message}"


def _load_ontology() -> dict[str, Any]:
    return json.loads(ONTOLOGY_PATH.read_text(encoding="utf-8"))


ONTOLOGY = _load_ontology()
DICTIONARY_DIGEST = ONTOLOGY["dictionary"]["digest"]
LAW_TERMS = set(ONTOLOGY["dictionary"]["terms"])


def _issue(issues: list[ValidationIssue], code: str, message: str, record_id: Any) -> None:
    issues.append(ValidationIssue(code, message, str(record_id or "<unknown>")))


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _parse_timestamp(value: Any) -> datetime | None:
    if not _is_timestamp(value):
        return None
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _is_record_ref(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("urn:uuid:"):
        return False
    try:
        uuid.UUID(value.removeprefix("urn:uuid:"))
    except (ValueError, AttributeError):
        return False
    return True


def _is_agent_id(value: Any) -> bool:
    return isinstance(value, str) and bool(AGENT_ID_RE.fullmatch(value))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0


def _all_unique(values: Iterable[Any]) -> bool:
    materialized = list(values)
    try:
        return len(materialized) == len(set(materialized))
    except TypeError:
        return False


def _check_timestamp(
    issues: list[ValidationIssue], value: Any, code: str, field: str, record_id: Any
) -> None:
    if not _is_timestamp(value):
        _issue(issues, code, f"{field} must be a UTC RFC 3339 timestamp ending in Z", record_id)


def _check_digest(
    issues: list[ValidationIssue], value: Any, code: str, field: str, record_id: Any
) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        _issue(issues, code, f"{field} must be a lowercase sha256:<64 hex> digest", record_id)


def _check_agent(
    issues: list[ValidationIssue], value: Any, code: str, field: str, record_id: Any
) -> None:
    if not _is_agent_id(value):
        _issue(issues, code, f"{field} must be a URI-like agent identifier", record_id)


def _check_string(
    issues: list[ValidationIssue], value: Any, code: str, field: str, record_id: Any
) -> None:
    if not _is_nonempty_string(value):
        _issue(issues, code, f"{field} must be a non-empty string", record_id)


def validate_ontology(repository_root: Path = REPOSITORY_ROOT) -> list[ValidationIssue]:
    """Check that the machine-readable ontology still pins the current dictionary."""
    issues: list[ValidationIssue] = []
    source = repository_root / ONTOLOGY["dictionary"]["source"]
    if not source.is_file():
        return [ValidationIssue("ULP300", f"dictionary source is missing: {source}")]
    actual = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != DICTIONARY_DIGEST:
        issues.append(
            ValidationIssue(
                "ULP301",
                f"ontology pins {DICTIONARY_DIGEST}, but dictionary is {actual}",
            )
        )
    return issues


def validate_record_structure(record: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(record, dict):
        return [ValidationIssue("ULP001", "record must be a JSON object")]

    record_id = record.get("id", "<unknown>")
    missing_common = {"protocol", "id", "type", "issued_at", "issuer", "payload"} - set(record)
    if missing_common:
        _issue(issues, "ULP002", f"missing envelope fields: {sorted(missing_common)}", record_id)

    unknown_common = set(record) - COMMON_FIELDS
    if unknown_common:
        _issue(issues, "ULP003", f"unknown envelope fields: {sorted(unknown_common)}", record_id)

    if record.get("protocol") != PROTOCOL:
        _issue(issues, "ULP010", f"protocol must equal {PROTOCOL}", record_id)
    if not _is_record_ref(record.get("id")):
        _issue(issues, "ULP011", "id must be a urn:uuid identifier", record_id)

    record_type = record.get("type")
    if record_type not in RECORD_TYPES:
        _issue(issues, "ULP012", f"unsupported record type: {record_type!r}", record_id)
    _check_timestamp(issues, record.get("issued_at"), "ULP013", "issued_at", record_id)
    _check_agent(issues, record.get("issuer"), "ULP014", "issuer", record_id)

    payload = record.get("payload")
    if not isinstance(payload, dict):
        _issue(issues, "ULP015", "payload must be an object", record_id)
        return issues

    if record_type in REQUIRED_PAYLOAD_FIELDS:
        missing = REQUIRED_PAYLOAD_FIELDS[record_type] - set(payload)
        if missing:
            _issue(issues, "ULP100", f"missing {record_type} payload fields: {sorted(missing)}", record_id)
        unknown = {
            key
            for key in set(payload) - ALLOWED_PAYLOAD_FIELDS[record_type]
            if not EXTENSION_RE.fullmatch(key)
        }
        if unknown:
            _issue(issues, "ULP101", f"unknown {record_type} payload fields: {sorted(unknown)}", record_id)

    proof = record.get("proof")
    if proof is not None:
        required = {"algorithm", "key_id", "created", "signature"}
        if not isinstance(proof, dict) or not required <= set(proof):
            _issue(issues, "ULP020", "proof must contain algorithm, key_id, created, and signature", record_id)
        else:
            _check_string(issues, proof.get("algorithm"), "ULP020", "proof.algorithm", record_id)
            _check_agent(issues, proof.get("key_id"), "ULP020", "proof.key_id", record_id)
            _check_timestamp(issues, proof.get("created"), "ULP020", "proof.created", record_id)
            signature = proof.get("signature")
            if not isinstance(signature, str) or len(signature) < 16 or not re.fullmatch(r"[A-Za-z0-9_-]+", signature):
                _issue(issues, "ULP020", "proof.signature must be base64url text of at least 16 characters", record_id)

    if record_type == "boundary":
        _check_agent(issues, payload.get("holder"), "ULP110", "holder", record_id)
        if payload.get("kind") not in BOUNDARY_KINDS:
            _issue(issues, "ULP110", "kind must be a recognized boundary kind", record_id)
        _check_string(issues, payload.get("object"), "ULP110", "object", record_id)
        if payload.get("protection") != "intact":
            _issue(issues, "ULP111", "a boundary declaration may only declare intact protection", record_id)

    elif record_type == "consent":
        for field in ("grantor", "grantee"):
            _check_agent(issues, payload.get(field), "ULP120", field, record_id)
        for field in ("action", "object", "scope"):
            _check_string(issues, payload.get(field), "ULP120", field, record_id)
        if payload.get("state") not in {"granted", "withdrawn"}:
            _issue(issues, "ULP120", "state must be granted or withdrawn", record_id)
        if "valid_until" in payload:
            _check_timestamp(issues, payload["valid_until"], "ULP120", "valid_until", record_id)

    elif record_type == "agreement":
        parties = payload.get("parties")
        if not _is_nonempty_list(parties) or len(parties) < 2 or not all(_is_agent_id(p) for p in parties):
            _issue(issues, "ULP130", "parties must contain at least two agent identifiers", record_id)
        elif not _all_unique(parties):
            _issue(issues, "ULP130", "parties must be unique", record_id)
        _check_digest(issues, payload.get("terms_digest"), "ULP130", "terms_digest", record_id)
        if payload.get("state") not in {"offered", "accepted", "rejected", "terminated"}:
            _issue(issues, "ULP130", "invalid agreement state", record_id)

    elif record_type == "action":
        _check_agent(issues, payload.get("actor"), "ULP140", "actor", record_id)
        _check_string(issues, payload.get("verb"), "ULP140", "verb", record_id)
        _check_string(issues, payload.get("object"), "ULP140", "object", record_id)
        _check_timestamp(issues, payload.get("occurred_at"), "ULP140", "occurred_at", record_id)

    elif record_type == "evidence":
        for field in ("statement", "source"):
            _check_string(issues, payload.get(field), "ULP150", field, record_id)
        _check_timestamp(issues, payload.get("observed_at"), "ULP150", "observed_at", record_id)
        _check_digest(issues, payload.get("content_digest"), "ULP150", "content_digest", record_id)

    elif record_type == "claim":
        for field in ("claimant", "respondent", "victim"):
            _check_agent(issues, payload.get(field), "ULP210", field, record_id)
        if not _is_nonempty_list(payload.get("evidence_refs")):
            _issue(issues, "ULP211", "a claim must cite at least one evidence record", record_id)
        if not _is_nonempty_list(payload.get("allegations")):
            _issue(issues, "ULP212", "a claim must name at least one allegation", record_id)

    elif record_type == "judgment":
        _check_agent(issues, payload.get("judge"), "ULP220", "judge", record_id)
        if payload.get("falsifiable") is not True:
            _issue(issues, "ULP221", "a Judgment must be explicitly falsifiable", record_id)
        if not _is_nonempty_list(payload.get("evidence_refs")):
            _issue(issues, "ULP222", "a Judgment must cite evidence", record_id)
        _check_digest(issues, payload.get("dictionary_digest"), "ULP223", "dictionary_digest", record_id)
        if payload.get("dictionary_digest") != DICTIONARY_DIGEST:
            _issue(issues, "ULP224", "Judgment dictionary_digest does not match the ULP/1 ontology", record_id)
        findings = payload.get("findings")
        if not isinstance(findings, dict):
            _issue(issues, "ULP225", "findings must be an object", record_id)
        else:
            missing = REQUIRED_FINDINGS - set(findings)
            if missing:
                _issue(issues, "ULP225", f"missing findings: {sorted(missing)}", record_id)
            law_terms = findings.get("law_terms")
            if not _is_nonempty_list(law_terms):
                _issue(issues, "ULP226", "findings.law_terms must be non-empty", record_id)
            else:
                unknown_terms = sorted(set(law_terms) - LAW_TERMS)
                if unknown_terms:
                    _issue(issues, "ULP226", f"law terms are not pinned by the ontology: {unknown_terms}", record_id)
                if findings.get("causation") == "proven" and "Causation" not in law_terms:
                    _issue(
                        issues,
                        "ULP226",
                        "proven causation requires the Causation term; Correlation cannot substitute for it",
                        record_id,
                    )
            kinds = findings.get("permitted_response_kinds")
            if not isinstance(kinds, list) or not set(kinds) <= BOUNDARY_KINDS or not _all_unique(kinds):
                _issue(issues, "ULP227", "permitted_response_kinds must be unique boundary kinds", record_id)
            if findings.get("forfeiture") == "proven":
                prerequisites = {
                    "causation": "proven",
                    "boundary_crossing": "proven",
                    "crossed_boundary_protection": "intact",
                    "victim_status": "victim",
                }
                failed = [key for key, value in prerequisites.items() if findings.get(key) != value]
                if failed or "Forfeiture" not in (law_terms or []):
                    _issue(
                        issues,
                        "ULP228",
                        "Forfeiture requires proven causation and crossing of an intact boundary, a Victim, and the Forfeiture term",
                        record_id,
                    )
            restitution = findings.get("restitution")
            if not isinstance(restitution, dict) or not {"required", "description"} <= set(restitution):
                _issue(issues, "ULP229", "restitution must contain required and description", record_id)

    elif record_type == "mandate":
        for field in ("principal", "delegate"):
            _check_agent(issues, payload.get(field), "ULP230", field, record_id)
        if not _is_nonempty_list(payload.get("powers")):
            _issue(issues, "ULP230", "powers must be non-empty", record_id)
        kinds = payload.get("kinds")
        if not _is_nonempty_list(kinds) or not set(kinds) <= BOUNDARY_KINDS:
            _issue(issues, "ULP230", "kinds must contain recognized boundary kinds", record_id)
        if payload.get("state") not in {"granted", "revoked"}:
            _issue(issues, "ULP230", "state must be granted or revoked", record_id)
        if "valid_until" in payload:
            _check_timestamp(issues, payload["valid_until"], "ULP230", "valid_until", record_id)

    elif record_type == "response":
        for field in ("actor", "target"):
            _check_agent(issues, payload.get(field), "ULP240", field, record_id)
        _check_string(issues, payload.get("action"), "ULP240", "action", record_id)
        if payload.get("kind") not in BOUNDARY_KINDS:
            _issue(issues, "ULP240", "kind must be a recognized boundary kind", record_id)
        basis = payload.get("basis")
        if basis not in {"self-defense", "justice"}:
            _issue(issues, "ULP240", "basis must be self-defense or justice", record_id)
        elif basis == "self-defense":
            needed = {
                "action_ref",
                "boundary_ref",
                "threat_state",
                "minimal_force",
                "causally_directed",
                "ends_when_crossing_ends",
            }
            if not needed <= set(payload):
                _issue(issues, "ULP241", f"self-defense is missing: {sorted(needed - set(payload))}", record_id)
            if payload.get("threat_state") not in {"ongoing", "immediately_credible"}:
                _issue(issues, "ULP242", "self-defense requires an ongoing or immediately credible crossing", record_id)
            if payload.get("minimal_force") is not True:
                _issue(issues, "ULP243", "self-defense must assert minimum necessary force", record_id)
            if payload.get("causally_directed") is not True:
                _issue(issues, "ULP244", "self-defense must be directed at the crossing agent", record_id)
            if payload.get("ends_when_crossing_ends") is not True:
                _issue(issues, "ULP245", "self-defense must end when the crossing ends", record_id)
        elif "judgment_ref" not in payload:
            _issue(issues, "ULP246", "a Justice response must reference a Judgment", record_id)

    elif record_type == "resolution":
        _check_agent(issues, payload.get("victim"), "ULP260", "victim", record_id)
        if payload.get("mode") not in {"collection", "release"}:
            _issue(issues, "ULP260", "mode must be collection or release", record_id)
        if payload.get("moral_debt") != "closed":
            _issue(issues, "ULP260", "a resolution records moral_debt as closed", record_id)

    elif record_type == "challenge":
        if not _is_nonempty_list(payload.get("grounds")):
            _issue(issues, "ULP270", "grounds must be non-empty", record_id)
        _check_string(issues, payload.get("statement"), "ULP270", "statement", record_id)

    elif record_type == "correction":
        _check_string(issues, payload.get("reason"), "ULP280", "reason", record_id)

    return issues


def validate_stream(records: list[Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for record in records:
        issues.extend(validate_record_structure(record))

    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            continue
        record_id = record["id"]
        if record_id in by_id:
            _issue(issues, "ULP030", "record id is duplicated", record_id)
        else:
            by_id[record_id] = record

    def resolve(owner: dict[str, Any], ref: Any, expected: str | set[str] | None, field: str) -> dict[str, Any] | None:
        owner_id = owner.get("id")
        if not _is_record_ref(ref):
            _issue(issues, "ULP200", f"{field} is not a record reference", owner_id)
            return None
        target = by_id.get(ref)
        if target is None:
            _issue(issues, "ULP201", f"{field} does not resolve: {ref}", owner_id)
            return None
        if expected is not None:
            allowed = {expected} if isinstance(expected, str) else expected
            if target.get("type") not in allowed:
                _issue(
                    issues,
                    "ULP202",
                    f"{field} must reference {sorted(allowed)}, not {target.get('type')!r}",
                    owner_id,
                )
                return None
        return target

    def resolve_many(owner: dict[str, Any], refs: Any, expected: str, field: str) -> list[dict[str, Any]]:
        if not isinstance(refs, list):
            return []
        found = []
        for ref in refs:
            target = resolve(owner, ref, expected, field)
            if target is not None:
                found.append(target)
        return found

    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("payload"), dict):
            continue
        record_id = record.get("id")
        issuer = record.get("issuer")
        record_type = record.get("type")
        payload = record["payload"]

        if record_type == "boundary":
            if issuer != payload.get("holder"):
                _issue(issues, "ULP310", "a boundary must be issued by its holder", record_id)

        elif record_type == "consent":
            if issuer != payload.get("grantor"):
                _issue(issues, "ULP320", "consent must be issued by its grantor", record_id)
            if "supersedes" in payload:
                resolve(record, payload["supersedes"], "consent", "supersedes")

        elif record_type == "agreement":
            refs = payload.get("acceptance_refs", [])
            consents = resolve_many(record, refs, "consent", "acceptance_refs")
            if payload.get("state") == "accepted":
                grantors = {
                    item["payload"].get("grantor")
                    for item in consents
                    if item.get("payload", {}).get("state") == "granted"
                }
                if set(payload.get("parties", [])) != grantors:
                    _issue(issues, "ULP330", "an accepted agreement needs a grant from every party", record_id)
                terms_digest = payload.get("terms_digest")
                parties = set(payload.get("parties", []))
                mismatched = [
                    item.get("id")
                    for item in consents
                    if item["payload"].get("action") != "accept"
                    or item["payload"].get("object") != terms_digest
                    or item["payload"].get("grantee") not in parties
                ]
                if mismatched:
                    _issue(
                        issues,
                        "ULP331",
                        f"agreement acceptance does not match its terms or parties: {mismatched}",
                        record_id,
                    )

        elif record_type == "action":
            if "boundary_ref" in payload:
                resolve(record, payload["boundary_ref"], "boundary", "boundary_ref")
            if "consent_ref" in payload:
                consent = resolve(record, payload["consent_ref"], "consent", "consent_ref")
                if consent is not None:
                    grant = consent["payload"]
                    mismatch = (
                        grant.get("state") != "granted"
                        or grant.get("grantee") != payload.get("actor")
                        or grant.get("action") != payload.get("verb")
                        or grant.get("object") != payload.get("object")
                    )
                    if mismatch:
                        _issue(issues, "ULP340", "action falls outside the referenced consent", record_id)
                    action_time = _parse_timestamp(payload.get("occurred_at"))
                    expiry = _parse_timestamp(grant.get("valid_until"))
                    revoked_at = [
                        _parse_timestamp(item.get("issued_at"))
                        for item in records
                        if isinstance(item, dict)
                        and item.get("type") == "consent"
                        and isinstance(item.get("payload"), dict)
                        and item["payload"].get("state") == "withdrawn"
                        and item["payload"].get("supersedes") == consent.get("id")
                    ]
                    revoked_before_action = any(
                        moment is not None and action_time is not None and moment <= action_time
                        for moment in revoked_at
                    )
                    if (expiry is not None and action_time is not None and action_time > expiry) or revoked_before_action:
                        _issue(issues, "ULP341", "action cites expired or withdrawn consent", record_id)

        elif record_type == "evidence":
            if "about_ref" in payload:
                resolve(record, payload["about_ref"], None, "about_ref")

        elif record_type == "claim":
            if issuer != payload.get("claimant"):
                _issue(issues, "ULP350", "a claim must be issued by its claimant", record_id)
            action = resolve(record, payload.get("action_ref"), "action", "action_ref")
            boundary = resolve(record, payload.get("boundary_ref"), "boundary", "boundary_ref")
            resolve_many(record, payload.get("evidence_refs"), "evidence", "evidence_refs")
            if action is not None and action["payload"].get("actor") != payload.get("respondent"):
                _issue(issues, "ULP351", "claim respondent does not match the alleged actor", record_id)
            if boundary is not None and boundary["payload"].get("holder") != payload.get("victim"):
                _issue(issues, "ULP352", "claim victim does not hold the referenced boundary", record_id)

        elif record_type == "judgment":
            if issuer != payload.get("judge"):
                _issue(issues, "ULP360", "a Judgment must be issued by its Judge", record_id)
            claim = resolve(record, payload.get("claim_ref"), "claim", "claim_ref")
            evidence = resolve_many(record, payload.get("evidence_refs"), "evidence", "evidence_refs")
            if claim is not None:
                claim_evidence = set(claim["payload"].get("evidence_refs", []))
                judgment_evidence = {item.get("id") for item in evidence}
                if not claim_evidence <= judgment_evidence:
                    _issue(issues, "ULP361", "Judgment omits Evidence cited by the Claim", record_id)

        elif record_type == "mandate":
            if issuer != payload.get("principal"):
                _issue(issues, "ULP370", "a Mandate must be issued by its principal", record_id)
            judgment = resolve(record, payload.get("judgment_ref"), "judgment", "judgment_ref")
            if "supersedes" in payload:
                resolve(record, payload["supersedes"], "mandate", "supersedes")
            if judgment is not None:
                claim = resolve(record, judgment["payload"].get("claim_ref"), "claim", "judgment.claim_ref")
                if claim is not None and payload.get("principal") != claim["payload"].get("victim"):
                    _issue(issues, "ULP371", "Mandate principal must be the underlying Victim", record_id)

        elif record_type == "response":
            if issuer != payload.get("actor"):
                _issue(issues, "ULP380", "a response must be issued by its actor", record_id)
            if payload.get("basis") == "self-defense":
                action = resolve(record, payload.get("action_ref"), "action", "action_ref")
                boundary = resolve(record, payload.get("boundary_ref"), "boundary", "boundary_ref")
                if action is not None and action["payload"].get("actor") != payload.get("target"):
                    _issue(issues, "ULP381", "self-defense target must be the crossing actor", record_id)
                if boundary is not None and boundary["payload"].get("holder") != payload.get("actor"):
                    _issue(issues, "ULP382", "self-defense actor must hold the protected boundary", record_id)
            elif payload.get("basis") == "justice":
                judgment = resolve(record, payload.get("judgment_ref"), "judgment", "judgment_ref")
                if judgment is None:
                    continue
                findings = judgment["payload"].get("findings", {})
                if findings.get("forfeiture") != "proven":
                    _issue(issues, "ULP383", "Justice response requires proven Forfeiture", record_id)
                if payload.get("kind") not in findings.get("permitted_response_kinds", []):
                    _issue(issues, "ULP384", "response kind exceeds the Judgment's Proportion", record_id)
                claim = resolve(record, judgment["payload"].get("claim_ref"), "claim", "judgment.claim_ref")
                if claim is None:
                    continue
                victim = claim["payload"].get("victim")
                respondent = claim["payload"].get("respondent")
                if payload.get("target") != respondent:
                    _issue(issues, "ULP385", "Justice response target must be the respondent", record_id)
                if payload.get("actor") != victim:
                    mandate_ref = payload.get("mandate_ref")
                    if mandate_ref is None:
                        _issue(issues, "ULP386", "a proxy Justice response requires a Mandate", record_id)
                    else:
                        mandate = resolve(record, mandate_ref, "mandate", "mandate_ref")
                        if mandate is not None:
                            delegation = mandate["payload"]
                            response_time = _parse_timestamp(record.get("issued_at"))
                            expiry = _parse_timestamp(delegation.get("valid_until"))
                            revoked_at = [
                                _parse_timestamp(item.get("issued_at"))
                                for item in records
                                if isinstance(item, dict)
                                and item.get("type") == "mandate"
                                and isinstance(item.get("payload"), dict)
                                and item["payload"].get("state") == "revoked"
                                and item["payload"].get("supersedes") == mandate.get("id")
                            ]
                            revoked_before_response = any(
                                moment is not None and response_time is not None and moment <= response_time
                                for moment in revoked_at
                            )
                            valid = (
                                delegation.get("state") == "granted"
                                and delegation.get("principal") == victim
                                and delegation.get("delegate") == payload.get("actor")
                                and delegation.get("judgment_ref") == payload.get("judgment_ref")
                                and payload.get("action") in delegation.get("powers", [])
                                and payload.get("kind") in delegation.get("kinds", [])
                                and not (expiry is not None and response_time is not None and response_time > expiry)
                                and not revoked_before_response
                            )
                            if not valid:
                                _issue(issues, "ULP387", "response falls outside the referenced Mandate", record_id)

        elif record_type == "resolution":
            if issuer != payload.get("victim"):
                _issue(issues, "ULP390", "a resolution must be issued by the Victim", record_id)
            judgment = resolve(record, payload.get("judgment_ref"), "judgment", "judgment_ref")
            if judgment is not None:
                claim = resolve(record, judgment["payload"].get("claim_ref"), "claim", "judgment.claim_ref")
                if claim is not None and payload.get("victim") != claim["payload"].get("victim"):
                    _issue(issues, "ULP391", "resolution issuer is not the underlying Victim", record_id)
            if "restitution_ref" in payload:
                resolve(record, payload["restitution_ref"], "response", "restitution_ref")

        elif record_type == "challenge":
            resolve(record, payload.get("target_ref"), None, "target_ref")
            resolve_many(record, payload.get("evidence_refs", []), "evidence", "evidence_refs")

        elif record_type == "correction":
            target = resolve(record, payload.get("target_ref"), None, "target_ref")
            replacement = resolve(record, payload.get("replacement_ref"), None, "replacement_ref")
            if target is not None and replacement is not None and target.get("type") != replacement.get("type"):
                _issue(issues, "ULP400", "a correction replacement must have the same record type", record_id)
            if payload.get("target_ref") == payload.get("replacement_ref"):
                _issue(issues, "ULP401", "a correction cannot replace a record with itself", record_id)

    correction_edges = {
        record["payload"].get("target_ref"): record["payload"].get("replacement_ref")
        for record in records
        if isinstance(record, dict)
        and record.get("type") == "correction"
        and isinstance(record.get("payload"), dict)
    }
    for start in correction_edges:
        seen: set[str] = set()
        current = start
        while current in correction_edges:
            if current in seen:
                _issue(issues, "ULP402", "correction links contain a cycle", start)
                break
            seen.add(current)
            current = correction_edges[current]

    return sorted(set(issues), key=lambda item: (item.record_id, item.code, item.message))


def load_records(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        value = json.loads(text)
        return value if isinstance(value, list) else [value]
    records = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return records


def validate_path(path: Path) -> list[ValidationIssue]:
    try:
        records = load_records(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [ValidationIssue("ULP000", str(exc))]
    return validate_stream(records)


def _print_issues(issues: list[ValidationIssue]) -> None:
    for issue in issues:
        print(issue)


def validate_manifest(path: Path) -> bool:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    base = path.parent
    ok = True

    ontology_issues = validate_ontology()
    if ontology_issues:
        ok = False
        print("FAIL ontology")
        _print_issues(ontology_issues)
    else:
        print("PASS ontology")

    for relative in manifest.get("valid", []):
        vector = base / relative
        issues = validate_path(vector)
        if issues:
            ok = False
            print(f"FAIL expected-valid {relative}")
            _print_issues(issues)
        else:
            print(f"PASS expected-valid {relative}")

    for item in manifest.get("invalid", []):
        relative = item["path"]
        expected = set(item["codes"])
        vector = base / relative
        issues = validate_path(vector)
        actual = {issue.code for issue in issues}
        if not issues or not expected <= actual:
            ok = False
            print(f"FAIL expected-invalid {relative}: expected {sorted(expected)}, got {sorted(actual)}")
            _print_issues(issues)
        else:
            print(f"PASS expected-invalid {relative}: {sorted(expected)}")
    return ok


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("path", nargs="?", type=Path, help="JSON or JSONL ULP record stream")
    group.add_argument("--manifest", type=Path, help="conformance manifest to execute")
    parser.add_argument("--json", action="store_true", help="emit issues as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.manifest:
        return 0 if validate_manifest(args.manifest) else 1

    issues = validate_ontology() + validate_path(args.path)
    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], indent=2))
    elif issues:
        print(f"FAIL {args.path}")
        _print_issues(issues)
    else:
        print(f"PASS {args.path}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
