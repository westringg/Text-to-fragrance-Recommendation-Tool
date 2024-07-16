import pandas as pd
import pickle
import gensim.downloader as api
from sklearn.metrics.pairwise import cosine_similarity
from mapping import Mapping
from ner import Ner
import PySimpleGUI as psg
import time 
import re

# Load pre-trained Word2Vec embeddings
print("Loading the pre-trained model...")
pretrained_model = api.load("word2vec-google-news-300")    

def calculate_similarity(word1, word2):
    """
        Calculate the cosine similarity between two words.

        Args:
            word1 (str): The first word.
            word2 (str): The second word.

        Returns:
            float: The cosine similarity between the embeddings of the two words.
    """
    # Check if both words are present in the vocabulary
    if word1 in pretrained_model.key_to_index and word2 in pretrained_model.key_to_index:
        # Get the word embeddings for the two words
        embedding1 = pretrained_model[word1]
        embedding2 = pretrained_model[word2]
        # Calculate cosine similarity between the embeddings
        similarity = cosine_similarity([embedding1],[embedding2])[0][0]
        return similarity
    else:
        return None

def generate_mappings(similarity_upper_threshold):
    """
        Generate mappings between keywords and fragrance notes.

        Args:
            similarity_upper_threshold (float): The threshold for similarity between keywords and notes.

        Returns:
            None
    """

    # Direct mapping of token-note when the token equals name of the note (volatility 0)
    #       or the note that is most similar to the token (volatility 1)
    #       or the note category that is most similar to the token (volatility 2)

    mapping = Mapping('token_note_mapping.pkl')
    categories = ['CITRUS SMELLS', 'FRUITS, VEGETABLES AND NUTS', 'FLOWERS', 'WHITE FLOWERS', 'GREENS HERBS AND FOUGERES',
                    'SPICES', 'SWEETS AND GOURMAND SMELLS', 'WOODS AND MOSSES', 'RESINS AND BALSAMS', 'MUSK AMBER ANIMALIC SMELLS',
                    'BEVERAGES', 'NATURAL AND SYNTHETIC, POPULAR AND WEIRD']
    # Load data from CSV file
    print("Loading training dataset...")
    data = pd.read_csv('training_set.csv', encoding='latin-1', on_bad_lines='warn')
    fragrance_descriptions = data['Description'].tolist()

    fragrance_notes = []
    for note in data['Notes']:
        if isinstance(note, str):
            fragrance_notes.append((note.split(',')))
        else:
            fragrance_notes.append([])
    fragrance_notes = [[str(note).strip() for note in notes] for notes in fragrance_notes]

    ner = Ner()
    
    print("Mapping in progress...")
    for i in range(1, len(fragrance_descriptions)):
        description = fragrance_descriptions[i]
        notes = [note.lower() for note in fragrance_notes[i]]
        
        top_keywords = ner.extract_keywords(description)

        for top_keyword in top_keywords:
            # Find the most similar note
            max_similarity = 0
            most_similar_note = None
            for note in notes:
                if top_keyword in note.strip():
                    max_similarity = 1
                    most_similar_note = note
                    mapping.add_mapping(top_keyword, note, 0)
                    top_keywords.remove(top_keyword)
                    break
                similarity = calculate_similarity(top_keyword, note)
                if similarity is not None and similarity > max_similarity:
                    max_similarity = similarity
                    most_similar_note = note

            if max_similarity < 1:
                # Find any note category that contains keyword
                exact_category = None
                for note_category in categories:
                    if top_keyword.upper() in note_category:
                        exact_category = note_category

                # Find the most similar note category
                max_category_similarity = 0
                most_similar_category = None
                for category in categories:
                    category_lower = category.lower()
                    category_similarity = calculate_similarity(top_keyword, category_lower)
                    if category_similarity is not None and category_similarity == 1:
                        max_category_similarity = 1
                        most_similar_category = category
                        break
                    if category_similarity is not None and category_similarity > max_category_similarity:
                        max_category_similarity = category_similarity
                        most_similar_category = category

                if exact_category is not None and max_similarity < similarity_upper_threshold:
                    mapping.add_mapping(top_keyword, exact_category, 1)
                    top_keywords.remove(top_keyword)
                elif max_similarity >= max_category_similarity:
                    mapping.add_mapping(top_keyword, most_similar_note, 1)
                    top_keywords.remove(top_keyword)
                else:
                    mapping.add_mapping(top_keyword, most_similar_category, 2)

    print("Saving the mappings in pickle file...")
    # Serialise mapping object and write it on pickle file
    mapping.save_to_pickle()

def predict_notes(user_input, num_random_notes):
    """
        Predict fragrance notes based on user input.

        Args:
            user_input (str): The user's input describing a memory related to a scent.
            num_random_notes (int): The number of random notes to be generated.

        Returns:
            str: A string containing the predicted top, middle, and base notes.
    """
    print("Generating the fragrance notes just like that! Exciting...")    
    # Load mapping data
    with open('token_note_mapping.pkl', 'rb') as f:
        mapping = pickle.load(f)
    
    mapped_tokens = mapping.get_tokens()
    note_class_data = pd.read_csv('note_categories.csv', encoding='latin-1', sep=';', on_bad_lines='warn')

    # Prepare user input data (tokenization, one-hot encoding, etc.)
    ner = Ner()
    keywords = ner.extract_keywords(user_input)

    base_notes, middle_notes, top_notes = [], [], []
    for keyword in keywords:
        max_similarity = 0
        predicted_class = None
        volatility = None

        if keyword in mapped_tokens:
            predicted_class = mapping.get_note_for_token(keyword)
            volatility = mapping.get_volatility(keyword)
        else:
            for token in mapped_tokens:
                similarity = calculate_similarity(keyword, token)
                if similarity is not None and similarity > max_similarity:
                    max_similarity = similarity
                    predicted_class = mapping.get_note_for_token(token)
                    volatility = mapping.get_volatility(token)

        if volatility == 0 and predicted_class not in base_notes:
            base_notes.append(predicted_class)
        else:
            if predicted_class is not None and predicted_class.isupper():
                filtered_notes = note_class_data.loc[note_class_data['Category'] == predicted_class, 'Note Name']
                if not filtered_notes.empty:
                    # Use current time as the random seed
                    random_state = int(time.time())
                    chosen_notes = filtered_notes.sample(num_random_notes, random_state=random_state).tolist()
                else:
                    print("No notes found for the specified category.")
                    break
                if volatility==1:
                    for chosen_note in chosen_notes:
                        if chosen_note not in base_notes and chosen_note not in middle_notes:
                            middle_notes.append(chosen_note)
                else:
                    for chosen_note in chosen_notes:
                        if chosen_note not in base_notes and chosen_note not in middle_notes and chosen_note not in top_notes:
                            top_notes.append(chosen_note)
            elif predicted_class is not None:
                if predicted_class not in base_notes and predicted_class not in middle_notes:
                    middle_notes.append(predicted_class)
    
    print('Top notes for you: %s'%top_notes)
    print('Middle notes for you: %s'%middle_notes)
    print('Base notes for you: %s'%base_notes)
  

    return ('Top notes for you: %s\n\nMiddle notes for you: %s\n\nBase notes for you: %s'%(top_notes, middle_notes, base_notes))

def main():
    # Define the layout of the GUI
    layout = [
        [psg.Text("What memory do you have about this scent you'd like to find?")],
        [psg.Multiline(key="input_text",  size=(80, 30))],
        [psg.Button("Find", size=(10, 1), button_color=("white", "black")), 
         psg.Button("Clear", size=(10, 1),button_color=("white", "black"))]
    ]
    # Create the GUI window
    window = psg.Window("Olfactory Time Machine: Find the Scent that Brings Your Memory Back", layout, size=(600, 500), element_justification='center')

    # Event loop to handle interactions with the GUI
    while True:
        event, values = window.read()
        if event == psg.WINDOW_CLOSED:
            break
        elif event == "Find":
            user_input = values["input_text"]
            if re.search(r'[^a-zA-Z\s.]', user_input):  # Check if input contains characters other than letters, spaces, and dots
                psg.popup_error("Error: Please describe your memory in words! (No digits or symbols)")
            else:
                # Display the output in a pop-up window
                psg.popup_scrolled(predict_notes(user_input, 3), size=(80, 20), title="Recommendation Results")
        elif event == "Clear":
            window["input_text"].update("")

    window.close()
    
# Ensure the main function is only executed when the script is run directly
if __name__ == "__main__":
    # generate_mappings(0.8)          # Uncomment this call only when there is a change in training_set.csv 
                                        # or you don't have token_note_mapping.pkl locally.
    # Run note prediction process
    main()
