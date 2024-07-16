import unittest
from ner import Ner

class TestNer(unittest.TestCase):
    def setUp(self):
        self.ner = Ner()

    def test_extract_keywords(self):
        # Test keyword extraction for a simple description
        description = "This is a test description about fragrance notes and scents."
        expected_keywords = ["test", "description"]
        self.assertEqual(self.ner.extract_keywords(description), expected_keywords)

        # Test keyword extraction for a description with entities and stop words
        description_with_entities = "This scent reminds me of beautiful roses I bought in a market in July 2024."
        expected_keywords_with_entities = ["beautiful", "roses", "market"]
        self.assertEqual(self.ner.extract_keywords(description_with_entities), expected_keywords_with_entities)

        # Add more test cases for edge cases, handling of different parts of speech, etc.

if __name__ == "__main__":
    unittest.main()
