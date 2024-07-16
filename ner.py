from collections import Counter
import spacy

class Ner():
    "A class that manages Named Entity Recognition, especailly keyword extraction"
    
    def __init__(self):
        """
        Initialise the Ner class.
        Loads the English language model for NER using spaCy.
        """
        self.nlp = spacy.load("en_core_web_sm")

    def extract_keywords(self, description):
        """
        Extract keywords from the given description using Named Entity Recognition (NER).

        Parameters:
        - description (str): The description from which keywords are to be extracted.

        Returns:
        - top_keywords (list): List of top keywords extracted from the description.
        """
        doc = self.nlp(description)

        ner_categories = ["PERSON", "LOCATION", "DATE", "ORG"]
        token_labels = [(token.text, token.ent_type_) for token in doc]
        remove_entities = [token for token, label in token_labels if label in ner_categories]

        stop_words = spacy.lang.en.stop_words.STOP_WORDS | \
                     {"like", "note", "notes", "scent", "scents", "fragrance", "perfume", "\x96", "\r", "©", "le"}
        filtered_words = [token.text.lower().split("-")[0] for token in doc 
                          if token.pos_ not in {"VERB", "ADV"} and token.text not in remove_entities
                          and token.text.lower() not in stop_words and not token.is_punct 
                          and not token.is_digit and len(token.text)>1]
        word_freq = Counter(filtered_words)
        top_keywords = [word for word, _ in word_freq.most_common(15)]

        return top_keywords