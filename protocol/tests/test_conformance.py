from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROTOCOL_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = PROTOCOL_ROOT.parent
sys.path.insert(0, str(PROTOCOL_ROOT / "reference"))

import validate  # noqa: E402


class ProtocolConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest_path = PROTOCOL_ROOT / "conformance" / "manifest.json"
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.base = cls.manifest_path.parent

    def test_dictionary_binding_is_current(self) -> None:
        self.assertEqual([], validate.validate_ontology(REPOSITORY_ROOT))

    def test_schema_and_ontology_are_valid_json(self) -> None:
        schema = json.loads((PROTOCOL_ROOT / "schema" / "record.schema.json").read_text(encoding="utf-8"))
        ontology = json.loads((PROTOCOL_ROOT / "ontology" / "core.json").read_text(encoding="utf-8"))
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(validate.PROTOCOL, ontology["protocol"])

    def test_ontology_terms_exist_in_dictionary(self) -> None:
        dictionary_path = REPOSITORY_ROOT / validate.ONTOLOGY["dictionary"]["source"]
        blocks = dictionary_path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n\n")
        headings = {block.splitlines()[0] for block in blocks if block.splitlines()}
        missing = validate.LAW_TERMS - headings
        self.assertEqual(set(), missing)

    def test_all_record_types_have_a_valid_example(self) -> None:
        represented = set()
        for relative in self.manifest["valid"]:
            represented.update(record["type"] for record in validate.load_records(self.base / relative))
        self.assertEqual(validate.RECORD_TYPES, represented)

    def test_valid_vectors_pass(self) -> None:
        for relative in self.manifest["valid"]:
            with self.subTest(vector=relative):
                self.assertEqual([], validate.validate_path(self.base / relative))

    def test_invalid_vectors_fail_for_expected_reason(self) -> None:
        for item in self.manifest["invalid"]:
            with self.subTest(vector=item["path"]):
                issues = validate.validate_path(self.base / item["path"])
                actual = {issue.code for issue in issues}
                self.assertTrue(issues)
                self.assertLessEqual(set(item["codes"]), actual)

    def test_manifest_runner_passes(self) -> None:
        self.assertTrue(validate.validate_manifest(self.manifest_path))


if __name__ == "__main__":
    unittest.main()

