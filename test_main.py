import unittest
from main import calculate_similarity, predict_notes

class TestCalculateSimilarity(unittest.TestCase):
    def test_calculate_similarity(self):
        # Test similarity calculation for two words in the model's vocabulary
        similarity = calculate_similarity("dog", "cat")
        self.assertTrue(similarity >= 0 and similarity <= 1)

        # Test similarity calculation for two words in the model's vocabulary
        similarity = calculate_similarity("wood", "forest")
        self.assertTrue(similarity >= 0 and similarity <= 1)
    
    def test_similarity_invalid_word(self):
        # Test similarity calculation for a word not in the model's vocabulary
        similarity_invalid = calculate_similarity("xyzabc", "invalid")
        self.assertIsNone(similarity_invalid)

class TestPredictNotes(unittest.TestCase):
    def test_predict_notes(self):
        # Test predict_notes function with valid input
        user_input = "This is a test input"
        num_random_notes = 3
        result = predict_notes(user_input, num_random_notes)
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
