import pickle

class Mapping():
    "Class that manages list of mappings of word and fragrance note"
    def __init__(self, pickle_file):
        """
        Initialises the Mapping object.

        Args:
            pickle_file (str): The path to the pickle file for storing mappings.
        """
        self.mappings = [] 
        self.pickle_file = pickle_file
    
    def add_mapping(self, token, note, volatility):
        """
        Adds a new mapping or updates an existing one if a lower volatility is provided.

        Args:
            token (str): The token to be mapped.
            note (str): The note associated with the token.
            volatility (int): The volatility of the mapping.

        """
        if note is not None:
            existing_mapping = self.get_mapping(token)
            if existing_mapping:
                if volatility < existing_mapping['volatility']:
                    # Update existing mapping with lower volatility
                    existing_mapping['note'] = note
                    existing_mapping['volatility'] = volatility
            else:
                # Add a new mapping
                self.mappings.append({'token': token, 'note': note, 'volatility': volatility})

    def get_mapping(self, token):
        """
        Returns the mapping for the given token.

        Args:
            token (str): The token for which to retrieve the mapping.

        Returns:
            dict: The mapping for the token, or None if not found.
        """
        for mapping in self.mappings:
            if mapping['token'] == token:
                return mapping
        return None

    def get_note_for_token(self, token):
        """
        Returns the note associated with the given token.

        Args:
            token (str): The token for which to retrieve the note.

        Returns:
            str: The note associated with the token.

        Raises:
            ValueError: If the token is not found.
        """
        for mapping in self.mappings:
            if mapping['token'] == token:
                return mapping['note']
        raise ValueError("Token not found")

    def get_volatility(self, token):
        """
        Returns the volatility associated with the given token.

        Args:
            token (str): The token for which to retrieve the volatility.

        Returns:
            int: The volatility associated with the token, or None if not found.
        """
        for mapping in self.mappings:
            if mapping['token'] == token:
                return mapping['volatility']
        return None

    def get_mappings(self):
        """
        Returns all mappings.

        Returns:
            list: A list of all mappings.
        """
        return self.mappings
    
    def get_tokens(self):
        """
        Returns all unique tokens.

        Returns:
            list: A list of all unique tokens.
        """
        return list(mapping['token'] for mapping in self.mappings)  
    
    def get_notes(self):
        """
        Returns all unique notes.

        Returns:
            list: A list of all unique notes.
        """
        return list(mapping['note'] for mapping in self.mappings) 
    
    def save_to_pickle(self):
        """
        Saves the Mapping object to a pickle file.
        """
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self, f)