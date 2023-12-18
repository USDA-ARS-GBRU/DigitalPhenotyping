import spacy
import re
from nltk.tree import Tree
from nltk.chunk.util import tagstr2tree
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize, regexp_tokenize
import nltk
import pandas as pd
from spacy.matcher import PhraseMatcher
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nlp = spacy.load('en_core_web_sm')

# Define a dictionary of characteristics and their synonyms
characteristics = {
    'tree health': ['th_good', 'th_poor', 'th_very good'],
    'fruit yield': ['fy_heavy', 'fy_moderate', 'fy_light'],
    'fruit size': ['fs_large', 'fs_medium', 'fs_small'],
    'fruit shape': ['fsh_oblate', 'fsh_elongated', 'fsh_necked', 'fsh_spheroid'],
    'fruit color': ['fc_green', 'fc_color break', 'fc_orange'],
    'harvest': ['hv_plugged', 'hv_clean'],
    'peel': ['p_easy to peel', 'p_not peelable'],
    'peel thickness': ['pt_thick peel', 'pt_thick flavedo', 'pt_thick albedo'],
    'fruit flesh': ['ff_juicy', 'ff_dry', 'ff_segments separate easily'],
    'seed number': ['sn_high', 'sn_moderate', 'sn_low', 'sn_none'],
    'brix': ['b_high', 'b_moderate', 'b_low'],
    'acid': ['a_high', 'a_moderate', 'a_low'],
    'fruit flavor': ['ff_best', 'ff_above average', 'ff_average', 'ff_below average'],
    'trifoliate aftertaste': ['ta_trifoliate aftertaste', 'ta_present', 'ta_not present'],
    'market class': ['mc_grapefruit like', 'mc_orange like', 'mc_mandarin like'],
    'recheck': ['rc_recheck', 'rc_yes', 'rc_no']
}


# Define the features and their associated keywords
features = {
    'health': ['good', 'poor', 'very good'],
    'yield': ['heavy', 'moderate', 'light'],
    'size': ['large', 'medium', 'small'],
    'shape': ['oblate', 'elongated', 'necked', 'spheroid'],
    'color': ['green', 'color break', 'orange'],
    'harvest': ['plugged', 'clean'],
    'peel': ['easy to peel', 'not peelable'],
    'peel thickness': ['thick peel', 'thick flavedo', 'thick albedo'],
    'fruit flesh': ['juicy', 'dry', 'segments separate easily'],
    'seed number': ['high', 'moderate', 'low', 'none'],
    'brix': ['high', 'moderate', 'low'],
    'acid': ['high', 'moderate', 'low'],
    'fruit flavor': ['best', 'above average', 'average', 'below average'],
    'trifoliate aftertaste': ['trifoliate aftertaste', 'trifolate aftertaste', 'present', 'not present'],
    'market class': ['grapefruit like', 'orange like', 'mandarin like'],
    'recheck': ['recheck', 'yes', 'no']
}

features_okra = {
    'stem': ['red green'],
    'flowering': ['not flowering', 'one pod']
}

def extract_features_matcher(text):
    matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
    for characteristic, synonyms in characteristics.items():
        patterns = [nlp.make_doc(syn.lower()) for syn in synonyms]
        matcher.add(characteristic, patterns)
    doc = nlp(text)

    # Initialize an empty dictionary to store the extracted characteristics
    fruit_characteristics = {}

    # Find all matches in the doc and add them to the dictionary
    for match_id, start, end in matcher(doc):
        characteristic = nlp.vocab.strings[match_id]
        value = doc[start:end].text
        fruit_characteristics[characteristic] = value

    # Return the dictionary of extracted characteristics
    return pd.Series(fruit_characteristics)

def extract_features(text):
    # Use NER to extract named entities
    doc = nlp(text)
    named_entities = set([ent.text.lower()
                         for ent in doc.ents if ent.label_ == "PRODUCT"])

    # Use POS tagging to extract adjectives
    adjectives = set([token.text.lower()
                     for token in doc if token.pos_ == "ADJ"])

    # Use keyword matching to extract features
    extracted_features = {}
    for feature, keywords in features_okra.items():
        for keyword in keywords:
            pattern = r'\b{}\b'.format(keyword)
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted_features[feature] = set(matches)

        # Check if the feature was mentioned as a named entity or adjective
        if feature not in extracted_features:
            if any(keyword in named_entities for keyword in keywords):
                extracted_features[feature] = list(
                    named_entities.intersection(keywords))[0]
            elif any(keyword in adjectives for keyword in keywords):
                extracted_features[feature] = list(
                    adjectives.intersection(keywords))[0]

    # return pd.Series(extracted_features)
    return extracted_features


def context_phenotype_text(text, context_size=0):
    # Tokenize the text into individual words
    tokens = word_tokenize(text)

    # Use part-of-speech (POS) tagging to identify the parts of speech of each word
    pos_tags = nltk.pos_tag(tokens)

    # Extract the characteristics of the fruit
    fruit_characteristics = {}
    for characteristic, synonyms in characteristics.items():
        extracted_synonyms = []
        for i in range(len(tokens)):
            word = tokens[i]
            for syn in synonyms:
                if word.lower() == syn.split("_")[1]:
                    extracted_synonyms.append(syn)
                    # Check the surrounding words in the n-gram
                    start_index = max(i - context_size, 0)
                    end_index = min(i + context_size + 1, len(tokens))
                    ngram = tokens[start_index:end_index]
                    for ngram_word, tag in nltk.pos_tag(ngram):
                        if ngram_word.lower() in synonyms:
                            extracted_synonyms.append(ngram_word.lower())
                elif wordnet.synsets(word):
                    word_synonyms = []
                    for synset in wordnet.synsets(word):
                        for lemma in synset.lemmas():
                            word_synonyms.extend([synonym.lower() for synonym in lemma.name().split(
                                '_') if synonym.lower() in synonyms])
                    if word_synonyms:
                        # Check the surrounding words in the n-gram
                        start_index = max(i - context_size, 0)
                        end_index = min(i + context_size + 1, len(tokens))
                        ngram = tokens[start_index:end_index]
                        for ngram_word, tag in nltk.pos_tag(ngram):
                            if ngram_word.lower() in word_synonyms:
                                extracted_synonyms.append(ngram_word.lower())
        if extracted_synonyms:
            fruit_characteristics[characteristic] = extracted_synonyms

    if fruit_characteristics:
        for key in fruit_characteristics.keys():
            fruit_characteristics[key] = list(set(fruit_characteristics[key]))
        return pd.Series(fruit_characteristics)
        # for characteristic, synonyms in fruit_characteristics.items():
        # print(f"The {characteristic} of the fruit is {', '.join(synonyms)}")

    else:
        # print("No characteristics found.")
        return None


def reg_phenotype_text(text):
    # Tokenize the text into individual words
    reg_tokens = regexp_tokenize(text, pattern=r"(\w+\s\w+|\w+)")
    tokens = word_tokenize(text)

    # Use part-of-speech (POS) tagging to identify the parts of speech of each word
    pos_tags = nltk.pos_tag(tokens)
    reg_pos_tags = nltk.pos_tag(reg_tokens)

    # pos_tags = pos_tags + reg_pos_tags
    pos_tags = reg_pos_tags

    with open("pos_tag_regex.txt", "w") as f:
        f.write(str(pos_tags))

    # entities = nltk.chunk.ne_chunk(pos_tags)

    # tree = Tree(tagstr2tree(pos_tags))
    # print(tree.pretty_print())

    # print(entities)

    # Extract the characteristics of the fruit
    fruit_characteristics = {}
    for characteristic, synonyms in characteristics.items():
        extracted_synonyms = []
        for word, tag in pos_tags:
            # print(word, tag, [(s.name(), s.lemmas())
            #       for s in wordnet.synsets(word)])
            for syn in synonyms:
                if word.lower() == syn.split("_")[1]:
                    extracted_synonyms.append(syn)
                elif wordnet.synsets(word):
                    # word_synonyms = [synonym.lower() for synonym in wordnet.synset(
                    #     wordnet.synsets(word)[0].name()).lemma_names() if synonym.lower()]
                    # if word_synonyms:
                    #     extracted_synonyms.extend(word_synonyms)
                    # word_synonyms = [s for s in synonyms if wordnet.synsets(word) and s.endswith(wordnet.synset(
                    #     wordnet.synsets(word)[0].name()).lemmas()[0].name())]
                    word_synonyms = []
                    for s in synonyms:
                        if wordnet.synsets(word) and s.endswith(wordnet.synset(wordnet.synsets(word)[0].name()).lemmas()[0].name()):
                            word_synonyms.append(s)
                    extracted_synonyms.extend(word_synonyms)
        if extracted_synonyms:
            fruit_characteristics[characteristic] = extracted_synonyms

    # Print the extracted characteristics
    if fruit_characteristics:
        for key in fruit_characteristics.keys():
            fruit_characteristics[key] = list(set(fruit_characteristics[key]))
        return pd.Series(fruit_characteristics)
        # for characteristic, synonyms in fruit_characteristics.items():
        # print(f"The {characteristic} of the fruit is {', '.join(synonyms)}")

    else:
        # print("No characteristics found.")
        return None


def phenotype_text(text):
    # Tokenize the text into individual words
    tokens = word_tokenize(text)

    # Use part-of-speech (POS) tagging to identify the parts of speech of each word
    pos_tags = nltk.pos_tag(tokens)

    # entities = nltk.chunk.ne_chunk(pos_tags)

    # tree = Tree(tagstr2tree(pos_tags))
    # print(tree.pretty_print())

    # print(entities)

    # Extract the characteristics of the fruit
    fruit_characteristics = {}
    for characteristic, synonyms in characteristics.items():
        extracted_synonyms = []
        for word, tag in pos_tags:
            # print(word, tag, wordnet.synsets(word))
            for syn in synonyms:
                if word.lower() == syn.split("_")[1]:
                    extracted_synonyms.append(syn)
                elif wordnet.synsets(word):
                    # word_synonyms = [synonym.lower() for synonym in wordnet.synset(
                    #     wordnet.synsets(word)[0].name()).lemma_names() if synonym.lower()]
                    # if word_synonyms:
                    #     extracted_synonyms.extend(word_synonyms)
                    word_synonyms = [s for s in synonyms if wordnet.synsets(word) and s.endswith(wordnet.synset(
                        wordnet.synsets(word)[0].name()).lemmas()[0].name())]
                    extracted_synonyms.extend(word_synonyms)
        if extracted_synonyms:
            # Check for default synonym "average" for "fruit flavor"
            if characteristic == "fruit flavor":
                for syn in extracted_synonyms:
                    if syn.startswith(("above", "below", "good", "poor")):
                        extracted_synonyms.remove(syn)
                extracted_synonyms.append("ff_average")
            fruit_characteristics[characteristic] = extracted_synonyms

    # Print the extracted characteristics
    if fruit_characteristics:
        for key in fruit_characteristics.keys():
            fruit_characteristics[key] = list(set(fruit_characteristics[key]))
        return pd.Series(fruit_characteristics)

    else:
        # print("No characteristics found.")
        return None


# sample = "thick peel Harvest clean fruit flesh juicy fruit size is medium average fruit flavor with moderate brix moderate acid High seed number trifoliate aftertaste come back and recheck"
sample = "new plant red green stem one pod new plant one pods new plant not flowering new plant not flowering new plant not flowering new plant one pod new plant not flowering"
# df = pd.read_csv("test_log_with_transcript.csv")
# processed_df = pd.concat(
#     [df, df['transcript'].apply(extract_features)], axis=1)
# processed_df.to_csv("phenotype_characteristics.csv", index=False)
# print(extract_features(sample))
for part in sample.split("new plant"):
    print(part)
    print(extract_features(part))
# print("=========BASE===========")
# print(phenotype_text(sample))
# print("=========REGEX===========")
# print(reg_phenotype_text(sample))
# print("=========CONTEXT===========")
# print(context_phenotype_text(sample, 2))
# print("=========SPACY===========")
# print(extract_features(sample))
