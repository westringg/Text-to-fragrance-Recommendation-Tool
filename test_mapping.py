import unittest
import os
from mapping import Mapping
import pickle

class TestMapping(unittest.TestCase):
    def setUp(self):
        # Set up a test pickle file
        self.test_pickle_file = 'test_mappings.pkl'
        # Create a Mapping object
        self.mapping = Mapping(self.test_pickle_file)

    def tearDown(self):
        # Clean up the test environment by removing the test pickle file
        if os.path.exists(self.test_pickle_file):
            os.remove(self.test_pickle_file)

    def test_add_mapping(self):
        # Test adding mappings
        self.mapping.add_mapping('token1', 'note1', 0)
        self.assertEqual(len(self.mapping.get_mappings()), 1)
        self.mapping.add_mapping('token2', 'note2', 1)
        self.assertEqual(len(self.mapping.get_mappings()), 2)
        # Ensure that adding a mapping with higher volatility doesn't change existing mapping
        self.mapping.add_mapping('token1', 'note1', 1)
        self.assertEqual(len(self.mapping.get_mappings()), 2)
        self.assertEqual(self.mapping.get_note_for_token('token1'), 'note1')
        self.assertEqual(self.mapping.get_volatility('token1'), 0)

    def test_get_mapping(self):
        # Test getting mappings
        self.mapping.add_mapping('token1', 'note1', 0)
        self.assertIsNotNone(self.mapping.get_mapping('token1'))
        self.assertIsNone(self.mapping.get_mapping('non_existing_token'))

    def test_get_note_for_token(self):
        # Test getting notes for tokens
        self.mapping.add_mapping('token1', 'note1', 0)
        self.assertEqual(self.mapping.get_note_for_token('token1'), 'note1')
        with self.assertRaises(ValueError):
            self.mapping.get_note_for_token('non_existing_token')

    def test_get_volatility(self):
        # Test getting volatility for tokens
        self.mapping.add_mapping('token1', 'note1', 0)
        self.assertEqual(self.mapping.get_volatility('token1'), 0)
        self.assertIsNone(self.mapping.get_volatility('non_existing_token'))

    def test_get_mappings(self):
        # Test getting all mappings
        self.mapping.add_mapping('token1', 'note1', 0)
        self.mapping.add_mapping('token2', 'note2', 1)
        mappings = self.mapping.get_mappings()
        self.assertEqual(len(mappings), 2)
        self.assertEqual(mappings[0]['token'], 'token1')
        self.assertEqual(mappings[1]['note'], 'note2')

    def test_get_tokens(self):
        # Test getting all tokens
        self.mapping.add_mapping('token1', 'note1', 0)
        self.mapping.add_mapping('token2', 'note2', 1)
        tokens = self.mapping.get_tokens()
        self.assertEqual(len(tokens), 2)
        self.assertIn('token1', tokens)
        self.assertIn('token2', tokens)

    def test_get_notes(self):
        # Test getting all notes
        self.mapping.add_mapping('token1', 'note1', 0)
        self.mapping.add_mapping('token2', 'note2', 1)
        notes = self.mapping.get_notes()
        self.assertEqual(len(notes), 2)
        self.assertIn('note1', notes)
        self.assertIn('note2', notes)

    def test_save_to_pickle(self):
        # Test saving mappings to pickle file
        self.mapping.add_mapping('token1', 'note1', 0)
        self.mapping.save_to_pickle()
        self.assertTrue(os.path.exists(self.test_pickle_file))
        # Load mappings from pickle file and check if saved correctly
        with open(self.test_pickle_file, 'rb') as f:
            saved_mappings = pickle.load(f)
        self.assertEqual(len(saved_mappings.get_mappings()), 1)
        self.assertEqual(saved_mappings.get_mappings()[0]['token'], 'token1')
        self.assertEqual(saved_mappings.get_mappings()[0]['note'], 'note1')
        self.assertEqual(saved_mappings.get_mappings()[0]['volatility'], 0)

if __name__ == '__main__':
    unittest.main()
