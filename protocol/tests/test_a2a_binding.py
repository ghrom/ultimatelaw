from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent
A2A_ROOT = PROTOCOL_ROOT / "bindings" / "a2a"
sys.path.insert(0, str(A2A_ROOT / "reference"))
sys.path.insert(0, str(PROTOCOL_ROOT / "reference"))

import adapter  # noqa: E402
import validate as ulp_validate  # noqa: E402


class A2ABindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_path = A2A_ROOT / "conformance" / "manifest.json"
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.base = cls.manifest_path.parent

    def test_binding_constants_pin_the_kernel(self) -> None:
        self.assertEqual("ULP-A2A/1", adapter.PROFILE)
        self.assertEqual("ultimate-law/1", adapter.ULP_PROTOCOL)
        self.assertEqual(ulp_validate.PROTOCOL, adapter.ULP_PROTOCOL)
        self.assertEqual(ulp_validate.DICTIONARY_DIGEST, adapter.DICTIONARY_DIGEST)

    def test_binding_schemas_are_valid_json(self) -> None:
        for path in sorted((A2A_ROOT / "schema").glob("*.json")):
            with self.subTest(schema=path.name):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
                self.assertTrue(schema["$id"].startswith(adapter.EXTENSION_URI))

    def test_agent_card_fragment_is_conforming(self) -> None:
        fragment = json.loads((A2A_ROOT / "agent-card.fragment.json").read_text(encoding="utf-8"))
        self.assertEqual([], adapter.validate_agent_card_fragment(fragment))

    def test_valid_message_vectors_pass(self) -> None:
        for relative in self.manifest["valid_messages"]:
            with self.subTest(vector=relative):
                message = json.loads((self.base / relative).read_text(encoding="utf-8"))
                self.assertEqual([], adapter.validate_message(message))
                self.assertTrue(adapter.unwrap_message(message))

    def test_invalid_message_vectors_fail_for_expected_reason(self) -> None:
        for item in self.manifest["invalid_messages"]:
            with self.subTest(vector=item["path"]):
                message = json.loads((self.base / item["path"]).read_text(encoding="utf-8"))
                issues = adapter.validate_message(message)
                actual = {issue.code for issue in issues}
                self.assertTrue(issues)
                self.assertLessEqual(set(item["codes"]), actual)

    def test_agent_card_vectors_follow_manifest(self) -> None:
        for relative in self.manifest["valid_agent_cards"]:
            with self.subTest(vector=relative):
                fragment = json.loads((self.base / relative).read_text(encoding="utf-8"))
                self.assertEqual([], adapter.validate_agent_card_fragment(fragment))
        for item in self.manifest["invalid_agent_cards"]:
            with self.subTest(vector=item["path"]):
                fragment = json.loads((self.base / item["path"]).read_text(encoding="utf-8"))
                issues = adapter.validate_agent_card_fragment(fragment)
                actual = {issue.code for issue in issues}
                self.assertTrue(issues)
                self.assertLessEqual(set(item["codes"]), actual)

    def test_every_valid_kernel_stream_round_trips_losslessly(self) -> None:
        kernel_manifest_path = PROTOCOL_ROOT / "conformance" / "manifest.json"
        kernel_manifest = json.loads(kernel_manifest_path.read_text(encoding="utf-8"))
        for index, relative in enumerate(kernel_manifest["valid"]):
            with self.subTest(vector=relative):
                records = ulp_validate.load_records(kernel_manifest_path.parent / relative)
                original = copy.deepcopy(records)
                message = adapter.wrap_records(
                    records,
                    role="ROLE_USER" if index % 2 == 0 else "ROLE_AGENT",
                    message_id=f"roundtrip-{index}",
                    context_id="ctx-roundtrip",
                    task_id=f"task-{index}",
                    mode="boundary-gating" if index % 2 == 0 else "informational",
                )
                self.assertEqual([], adapter.validate_message(message))
                self.assertEqual(records, adapter.unwrap_message(message))
                self.assertEqual(original, records)

    def test_multiple_record_parts_and_unrelated_parts_are_allowed(self) -> None:
        message = json.loads(
            (A2A_ROOT / "conformance" / "valid" / "message.json").read_text(encoding="utf-8")
        )
        records = message["parts"][0]["data"]["records"]
        message["parts"] = [
            {"text": "Human-readable explanation", "mediaType": "text/plain"},
            {
                "data": {"records": records[:2]},
                "mediaType": adapter.RECORD_MEDIA_TYPE,
            },
            {
                "data": {"records": records[2:]},
                "mediaType": adapter.RECORD_MEDIA_TYPE,
            },
        ]
        self.assertEqual([], adapter.validate_message(message))
        self.assertEqual(records, adapter.unwrap_message(message))

    def test_a2a_role_does_not_rewrite_ulp_identity(self) -> None:
        records = ulp_validate.load_records(PROTOCOL_ROOT / "conformance" / "valid" / "consented-action.jsonl")
        for role in sorted(adapter.ROLES):
            with self.subTest(role=role):
                message = adapter.wrap_records(records, role=role, message_id=f"identity-{role}")
                extracted = adapter.unwrap_message(message)
                self.assertEqual(records, extracted)
                self.assertEqual("urn:agent:alice", extracted[0]["issuer"])

    def test_extension_header_negotiation_is_explicit(self) -> None:
        header = f"https://example.org/other/v1, {adapter.EXTENSION_URI}, {adapter.EXTENSION_URI}"
        self.assertEqual(
            ["https://example.org/other/v1", adapter.EXTENSION_URI],
            adapter.parse_extensions_header(header),
        )
        self.assertEqual([adapter.EXTENSION_URI], adapter.negotiate_extensions(header))
        self.assertEqual([], adapter.negotiate_extensions(None))

    def test_reference_adapter_rejects_excessive_record_count(self) -> None:
        record = ulp_validate.load_records(
            PROTOCOL_ROOT / "conformance" / "valid" / "consented-action.jsonl"
        )[0]
        with self.assertRaises(adapter.BindingError) as caught:
            adapter.wrap_records(
                [copy.deepcopy(record) for _ in range(adapter.MAX_RECORDS + 1)],
                role="ROLE_USER",
                message_id="too-many-records",
            )
        self.assertIn("A2A111", {issue.code for issue in caught.exception.issues})


if __name__ == "__main__":
    unittest.main()
