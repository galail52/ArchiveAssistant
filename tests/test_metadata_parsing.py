import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.metadata import join_people
from core.metadata import parse_people


class MetadataParsingTests(unittest.TestCase):
    def test_empty_people_string(self):
        self.assertEqual(parse_people(""), [])
        self.assertEqual(parse_people("   "), [])

    def test_single_person(self):
        self.assertEqual(parse_people("John Smith"), ["John Smith"])

    def test_comma_separated_people(self):
        self.assertEqual(
            parse_people("John Smith, Mary Smith, Bill"),
            ["John Smith", "Mary Smith", "Bill"],
        )

    def test_extra_spaces_are_trimmed(self):
        self.assertEqual(
            parse_people("  John   Smith  ,   Mary Smith "),
            ["John Smith", "Mary Smith"],
        )

    def test_repeated_commas_do_not_create_blank_values(self):
        self.assertEqual(
            parse_people("John Smith,,Mary Smith,,,"),
            ["John Smith", "Mary Smith"],
        )

    def test_casing_is_preserved(self):
        self.assertEqual(
            parse_people("john SMITH, Mary McDonald"),
            ["john SMITH", "Mary McDonald"],
        )

    def test_join_people_cleans_values(self):
        self.assertEqual(
            join_people([" John   Smith ", "", "Mary Smith"]),
            "John Smith, Mary Smith",
        )


if __name__ == "__main__":
    unittest.main()
