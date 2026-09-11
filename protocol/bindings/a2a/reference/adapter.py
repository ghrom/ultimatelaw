#!/usr/bin/env python3
"""Dependency-free ULP-A2A/1 Message adapter and binding validator."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


PROTOCOL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROTOCOL_ROOT / "reference"))

import validate as ulp_validate  # noqa: E402


EXTENSION_URI = "https://ultimatelaw.org/protocol/extensions/ulp/v1"
PROFILE = "ULP-A2A/1"
ULP_PROTOCOL = "ultimate-law/1"
RECORD_SCHEMA = "https://ultimatelaw.org/protocol/1/record.schema.json"
RECORD_MEDIA_TYPE = "application/vnd.ultimatelaw.records+json;version=1"
DICTIONARY_DIGEST = ulp_validate.DICTIONARY_DIGEST
ROLES = {"ROLE_USER", "ROLE_AGENT"}
MODES = {"informational", "boundary-gating"}
MAX_RECORDS = 256
MAX_INPUT_BYTES = 2_000_000
MAX_NESTING_DEPTH = 64

METADATA_FIELDS = {"profile", "mode", "dictionary_digest", "record_ids"}
AGENT_PARAMS_FIELDS = {
    "profile",
    "ulp_protocol",
    "dictionary_digest",
    "record_schema",
    "record_media_type",
    "modes",
}


@dataclass(frozen=True)
class BindingIssue:
    code: str
    message: str
    subject: str = "<message>"

    def __str__(self) -> str:
        return f"{self.code} {self.subject}: {self.message}"


class BindingError(ValueError):
    """Raised when wrapping or extracting a nonconforming binding."""

    def __init__(self, issues: Iterable[BindingIssue | ulp_validate.ValidationIssue]):
        self.issues = list(issues)
        super().__init__("; ".join(str(issue) for issue in self.issues))


def _issue(issues: list[BindingIssue], code: str, message: str, subject: Any) -> None:
    issues.append(BindingIssue(code, message, str(subject or "<message>")))


def _unique_issues(issues: Iterable[BindingIssue]) -> list[BindingIssue]:
    return sorted(set(issues), key=lambda item: (item.subject, item.code, item.message))


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _within_nesting_limit(value: Any, limit: int = MAX_NESTING_DEPTH) -> bool:
    stack: list[tuple[Any, int]] = [(value, 1)]
    seen: set[int] = set()
    while stack:
        item, depth = stack.pop()
        if depth > limit:
            return False
        if isinstance(item, dict):
            marker = id(item)
            if marker in seen:
                continue
            seen.add(marker)
            stack.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            marker = id(item)
            if marker in seen:
                continue
            seen.add(marker)
            stack.extend((child, depth + 1) for child in item)
    return True


def _serialized_size(value: Any) -> int | None:
    try:
        return len(json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    except (TypeError, ValueError, RecursionError):
        return None


def _extract_without_validation(message: dict[str, Any]) -> list[Any]:
    records: list[Any] = []
    parts = message.get("parts")
    if not isinstance(parts, list):
        return records
    for part in parts:
        if not isinstance(part, dict) or part.get("mediaType") != RECORD_MEDIA_TYPE:
            continue
        data = part.get("data")
        if isinstance(data, dict) and isinstance(data.get("records"), list):
            records.extend(data["records"])
    return records


def validate_message(message: Any) -> list[BindingIssue | ulp_validate.ValidationIssue]:
    """Validate an A2A v1.0 Message carrying a ULP-A2A/1 bundle."""

    issues: list[BindingIssue] = []
    if not isinstance(message, dict):
        return [BindingIssue("A2A100", "message must be an object")]

    subject = message.get("messageId", "<message>")
    message_size = _serialized_size(message)
    size_ok = message_size is not None and message_size <= MAX_INPUT_BYTES
    if message_size is None:
        _issue(issues, "A2A111", "message must contain finite JSON-compatible values", subject)
    elif message_size > MAX_INPUT_BYTES:
        _issue(issues, "A2A111", f"message exceeds {MAX_INPUT_BYTES} encoded bytes", subject)
    nesting_ok = _within_nesting_limit(message)
    if not nesting_ok:
        _issue(issues, "A2A111", f"message exceeds nesting depth {MAX_NESTING_DEPTH}", subject)
    if not _is_nonempty_string(message.get("messageId")):
        _issue(issues, "A2A101", "messageId must be a non-empty string", subject)
    if message.get("role") not in ROLES:
        _issue(issues, "A2A102", "role must be ROLE_USER or ROLE_AGENT", subject)
    for field in ("contextId", "taskId"):
        if field in message and not _is_nonempty_string(message[field]):
            _issue(issues, "A2A101", f"{field} must be a non-empty string when present", subject)

    parts = message.get("parts")
    if not isinstance(parts, list) or not parts:
        _issue(issues, "A2A103", "parts must be a non-empty array", subject)
        parts = []
    elif not all(isinstance(part, dict) for part in parts):
        _issue(issues, "A2A103", "every Part must be an object", subject)

    extensions = message.get("extensions")
    if not isinstance(extensions, list) or not all(isinstance(item, str) for item in extensions):
        _issue(issues, "A2A104", "extensions must be an array of URI strings", subject)
    else:
        if len(extensions) != len(set(extensions)):
            _issue(issues, "A2A104", "extensions must not contain duplicates", subject)
        if extensions.count(EXTENSION_URI) != 1:
            _issue(issues, "A2A104", "ULP extension URI must occur exactly once", subject)

    metadata = message.get("metadata")
    binding_metadata: Any = None
    if not isinstance(metadata, dict):
        _issue(issues, "A2A105", "metadata must be an object", subject)
    else:
        binding_metadata = metadata.get(EXTENSION_URI)
        if not isinstance(binding_metadata, dict):
            _issue(issues, "A2A105", "namespaced ULP binding metadata is required", subject)

    expected_ids: Any = None
    if isinstance(binding_metadata, dict):
        unknown = set(binding_metadata) - METADATA_FIELDS
        missing = METADATA_FIELDS - set(binding_metadata)
        if unknown:
            _issue(issues, "A2A105", f"unknown binding metadata members: {sorted(unknown)}", subject)
        if missing:
            _issue(issues, "A2A105", f"missing binding metadata members: {sorted(missing)}", subject)
        if binding_metadata.get("profile") != PROFILE:
            _issue(issues, "A2A106", f"profile must be {PROFILE}", subject)
        if binding_metadata.get("mode") not in MODES:
            _issue(issues, "A2A106", "mode must be informational or boundary-gating", subject)
        if binding_metadata.get("dictionary_digest") != DICTIONARY_DIGEST:
            _issue(issues, "A2A107", "dictionary_digest is not the pinned ULP digest", subject)
        expected_ids = binding_metadata.get("record_ids")
        if not isinstance(expected_ids, list) or not expected_ids:
            _issue(issues, "A2A109", "record_ids must be a non-empty array", subject)
        elif not all(ulp_validate._is_record_ref(item) for item in expected_ids):
            _issue(issues, "A2A109", "record_ids must contain ULP urn:uuid identifiers", subject)
        elif len(expected_ids) != len(set(expected_ids)):
            _issue(issues, "A2A109", "record_ids must be unique", subject)

    record_part_count = 0
    records: list[Any] = []
    for index, part in enumerate(parts):
        if not isinstance(part, dict) or part.get("mediaType") != RECORD_MEDIA_TYPE:
            continue
        record_part_count += 1
        data = part.get("data")
        if not isinstance(data, dict) or set(data) != {"records"}:
            _issue(issues, "A2A108", f"record Part {index} data must contain only records", subject)
            continue
        part_records = data.get("records")
        if not isinstance(part_records, list) or not part_records:
            _issue(issues, "A2A108", f"record Part {index} records must be a non-empty array", subject)
            continue
        records.extend(part_records)

    if record_part_count == 0:
        _issue(issues, "A2A108", f"at least one {RECORD_MEDIA_TYPE} Part is required", subject)
    if len(records) > MAX_RECORDS:
        _issue(issues, "A2A111", f"message carries more than {MAX_RECORDS} ULP records", subject)

    actual_ids = [record.get("id") if isinstance(record, dict) else None for record in records]
    if isinstance(expected_ids, list) and expected_ids != actual_ids:
        _issue(issues, "A2A109", "record_ids do not exactly match carried records in wire order", subject)
    actual_string_ids = [item for item in actual_ids if isinstance(item, str)]
    if len(actual_string_ids) != len(set(actual_string_ids)):
        _issue(issues, "A2A110", "carried ULP record IDs must be unique", subject)

    binding_issues: list[BindingIssue | ulp_validate.ValidationIssue] = _unique_issues(issues)
    if records and len(records) <= MAX_RECORDS and size_ok and nesting_ok:
        binding_issues.extend(ulp_validate.validate_stream(records))
    return binding_issues


def wrap_records(
    records: list[Any],
    *,
    role: str,
    message_id: str,
    context_id: str | None = None,
    task_id: str | None = None,
    mode: str = "informational",
) -> dict[str, Any]:
    """Create a conforming A2A Message without mutating the supplied ULP records."""

    preflight: list[BindingIssue | ulp_validate.ValidationIssue] = []
    if not records:
        preflight.append(BindingIssue("A2A108", "at least one ULP record is required", message_id))
    elif len(records) > MAX_RECORDS:
        preflight.append(
            BindingIssue("A2A111", f"a message may carry at most {MAX_RECORDS} ULP records", message_id)
        )
    if role not in ROLES:
        preflight.append(BindingIssue("A2A102", "role must be ROLE_USER or ROLE_AGENT", message_id))
    if not _is_nonempty_string(message_id):
        preflight.append(BindingIssue("A2A101", "message_id must be a non-empty string", message_id))
    if context_id is not None and not _is_nonempty_string(context_id):
        preflight.append(BindingIssue("A2A101", "context_id must be non-empty when present", message_id))
    if task_id is not None and not _is_nonempty_string(task_id):
        preflight.append(BindingIssue("A2A101", "task_id must be non-empty when present", message_id))
    if mode not in MODES:
        preflight.append(BindingIssue("A2A106", "unsupported handling mode", message_id))
    records_size = _serialized_size(records)
    size_ok = records_size is not None and records_size <= MAX_INPUT_BYTES
    if records_size is None:
        preflight.append(BindingIssue("A2A111", "records must contain finite JSON-compatible values", message_id))
    elif records_size > MAX_INPUT_BYTES:
        preflight.append(BindingIssue("A2A111", f"records exceed {MAX_INPUT_BYTES} encoded bytes", message_id))
    nesting_ok = _within_nesting_limit(records)
    if not nesting_ok:
        preflight.append(
            BindingIssue("A2A111", f"records exceed nesting depth {MAX_NESTING_DEPTH}", message_id)
        )
    if records and len(records) <= MAX_RECORDS and size_ok and nesting_ok:
        preflight.extend(ulp_validate.validate_stream(records))
    if preflight:
        raise BindingError(preflight)

    copied_records = deepcopy(records)
    record_ids = [record["id"] for record in copied_records]
    message: dict[str, Any] = {
        "messageId": message_id,
        "role": role,
        "parts": [
            {
                "data": {"records": copied_records},
                "mediaType": RECORD_MEDIA_TYPE,
            }
        ],
        "metadata": {
            EXTENSION_URI: {
                "profile": PROFILE,
                "mode": mode,
                "dictionary_digest": DICTIONARY_DIGEST,
                "record_ids": record_ids,
            }
        },
        "extensions": [EXTENSION_URI],
    }
    if context_id is not None:
        message["contextId"] = context_id
    if task_id is not None:
        message["taskId"] = task_id
    final_issues = validate_message(message)
    if final_issues:
        raise BindingError(final_issues)
    return message


def unwrap_message(message: Any) -> list[Any]:
    """Validate a bound A2A Message and return a deep copy of its ULP stream."""

    issues = validate_message(message)
    if issues:
        raise BindingError(issues)
    return deepcopy(_extract_without_validation(message))


def validate_agent_card_fragment(fragment: Any) -> list[BindingIssue]:
    """Validate the ULP AgentExtension declaration in an Agent Card or fragment."""

    issues: list[BindingIssue] = []
    subject = "<agent-card>"
    if not isinstance(fragment, dict):
        return [BindingIssue("A2A120", "Agent Card fragment must be an object", subject)]
    capabilities = fragment.get("capabilities")
    if not isinstance(capabilities, dict):
        return [BindingIssue("A2A120", "capabilities must be an object", subject)]
    extensions = capabilities.get("extensions")
    if not isinstance(extensions, list):
        return [BindingIssue("A2A121", "capabilities.extensions must be an array", subject)]
    matches = [item for item in extensions if isinstance(item, dict) and item.get("uri") == EXTENSION_URI]
    if len(matches) != 1:
        return [BindingIssue("A2A121", "exactly one ULP AgentExtension is required", subject)]

    extension = matches[0]
    required_fields = {"uri", "description", "required", "params"}
    if set(extension) != required_fields:
        _issue(issues, "A2A122", "AgentExtension must contain uri, description, required, and params", subject)
    if not _is_nonempty_string(extension.get("description")):
        _issue(issues, "A2A122", "AgentExtension description must be non-empty", subject)
    if not isinstance(extension.get("required"), bool):
        _issue(issues, "A2A122", "AgentExtension required must be boolean", subject)

    params = extension.get("params")
    if not isinstance(params, dict):
        _issue(issues, "A2A122", "AgentExtension params must be an object", subject)
        return _unique_issues(issues)
    if set(params) != AGENT_PARAMS_FIELDS:
        _issue(issues, "A2A122", "AgentExtension params have missing or unknown members", subject)

    expected = {
        "profile": PROFILE,
        "ulp_protocol": ULP_PROTOCOL,
        "dictionary_digest": DICTIONARY_DIGEST,
        "record_schema": RECORD_SCHEMA,
        "record_media_type": RECORD_MEDIA_TYPE,
    }
    for field, value in expected.items():
        if params.get(field) != value:
            _issue(issues, "A2A123", f"AgentExtension {field} is unsupported", subject)
    modes = params.get("modes")
    if (
        not isinstance(modes, list)
        or not modes
        or not all(mode in MODES for mode in modes)
        or len(modes) != len(set(modes))
    ):
        _issue(issues, "A2A123", "AgentExtension modes are invalid", subject)
    return _unique_issues(issues)


def parse_extensions_header(value: str | None) -> list[str]:
    """Parse an A2A-Extensions header into unique URIs in request order."""

    if value is None or not value.strip():
        return []
    result: list[str] = []
    for item in value.split(","):
        uri = item.strip()
        if uri and uri not in result:
            result.append(uri)
    return result


def negotiate_extensions(value: str | None, supported: Iterable[str] = (EXTENSION_URI,)) -> list[str]:
    """Return requested extension URIs supported by this endpoint, preserving order."""

    supported_set = set(supported)
    return [uri for uri in parse_extensions_header(value) if uri in supported_set]


def _load_json(path: Path) -> Any:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_records(path: Path) -> list[Any]:
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    records = ulp_validate.load_records(path)
    if len(records) > MAX_RECORDS:
        raise BindingError(
            [BindingIssue("A2A111", f"input contains more than {MAX_RECORDS} ULP records", str(path))]
        )
    return records


def _write(text: str, output: Path | None) -> None:
    if output is None:
        print(text)
    else:
        output.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")


def _print_issues(issues: Iterable[BindingIssue | ulp_validate.ValidationIssue], as_json: bool) -> None:
    materialized = list(issues)
    if as_json:
        print(json.dumps([asdict(issue) for issue in materialized], indent=2))
    else:
        for issue in materialized:
            print(issue)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    wrap = subparsers.add_parser("wrap", help="wrap a JSON or JSONL ULP stream")
    wrap.add_argument("path", type=Path)
    wrap.add_argument("--role", required=True, choices=sorted(ROLES))
    wrap.add_argument("--message-id", required=True)
    wrap.add_argument("--context-id")
    wrap.add_argument("--task-id")
    wrap.add_argument("--mode", choices=sorted(MODES), default="informational")
    wrap.add_argument("--output", type=Path)

    unwrap = subparsers.add_parser("unwrap", help="validate and extract ULP JSONL")
    unwrap.add_argument("path", type=Path)
    unwrap.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate", help="validate a bound A2A Message")
    validate.add_argument("path", type=Path)
    validate.add_argument("--json", action="store_true")

    card = subparsers.add_parser("validate-agent-card", help="validate an Agent Card fragment")
    card.add_argument("path", type=Path)
    card.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "wrap":
            records = _load_records(args.path)
            message = wrap_records(
                records,
                role=args.role,
                message_id=args.message_id,
                context_id=args.context_id,
                task_id=args.task_id,
                mode=args.mode,
            )
            _write(json.dumps(message, indent=2), args.output)
            return 0

        value = _load_json(args.path)
        if args.command == "unwrap":
            records = unwrap_message(value)
            _write("\n".join(json.dumps(record, separators=(",", ":")) for record in records), args.output)
            return 0

        if args.command == "validate":
            issues = validate_message(value)
        else:
            issues = validate_agent_card_fragment(value)
        if issues:
            _print_issues(issues, args.json)
            return 1
        if args.json:
            print("[]")
        else:
            print(f"PASS {args.path}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, BindingError) as exc:
        if isinstance(exc, BindingError):
            _print_issues(exc.issues, False)
        else:
            print(f"A2A000 <input>: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
