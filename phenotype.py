from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk
import pandas as pd
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Define a dictionary of characteristics and their synonyms
characteristics = {
    'tree health': ['good', 'poor', 'very good'],
    'fruit yield': ['heavy', 'moderate', 'light'],
    'fruit size': ['large', 'medium', 'small'],
    'fruit shape': ['oblate', 'elongated', 'necked', 'spheroid'],
    'fruit color': ['green', 'color break', 'orange'],
    'harvest': ['plugged', 'clean'],
    'peel': ['easy to peel', 'not peelable'],
    'peel thickness': ['thick peel', 'thick flavedo', 'thick albedo'],
    'fruit flesh': ['juicy', 'dry', 'segments separate easily'],
    'seed number': ['high', 'moderate', 'low', 'none'],
    'brix': ['high', 'moderate', 'low'],
    'acid': ['high', 'moderate', 'low'],
    'fruit flavor': ['best', 'above average', 'average', 'below average'],
    'trifoliate aftertaste': ['present', 'not present'],
    'market class': ['grapefruit-like', 'orange-like', 'mandarin-like'],
    'recheck': ['recheck', 'yes', 'no']
}


def phenotype_text(text):
    # Tokenize the text into individual words
    tokens = word_tokenize(text)

    # Use part-of-speech (POS) tagging to identify the parts of speech of each word
    pos_tags = nltk.pos_tag(tokens)

    # Extract the characteristics of the fruit
    fruit_characteristics = {}
    for characteristic, synonyms in characteristics.items():
        extracted_synonyms = []
        for word, tag in pos_tags:
            if word.lower() in synonyms and (tag == 'JJ' or tag == 'NN'):
                extracted_synonyms.append(word.lower())
            elif tag == 'NN' and wordnet.synsets(word):
                word_synonyms = [synonym.lower() for synonym in wordnet.synset(
                    wordnet.synsets(word)[0].name()).lemma_names() if synonym.lower() in synonyms]
                if word_synonyms:
                    extracted_synonyms.extend(word_synonyms)
        if extracted_synonyms:
            fruit_characteristics[characteristic] = extracted_synonyms

    # Print the extracted characteristics
    if fruit_characteristics:
        return pd.Series(fruit_characteristics)
        # for characteristic, synonyms in fruit_characteristics.items():
        # print(f"The {characteristic} of the fruit is {', '.join(synonyms)}")

    else:
        # print("No characteristics found.")
        return None


df = pd.read_csv("test_log_with_transcript.csv")
processed_df = pd.concat([df, df['transcript'].apply(phenotype_text)], axis=1)
processed_df.to_csv("phenotype_characteristics.csv", index=False)
