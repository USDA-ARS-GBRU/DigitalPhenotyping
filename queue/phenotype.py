import spacy
import re
import nltk
import os
import pandas as pd
import json
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nlp = spacy.load('en_core_web_sm')

features_okra = {
    'stem': ['red green', 'green', 'red'],
    'flowering': ['false', 'true']
}

features_belt = {
    'height': [],
    'color': ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "White", "Black", "Brown", "Cyan", "Magenta", "Gray"],
    'lodging': [],
    'insect damage': ['true', 'false']
}

features_citrus_hfl = {
    "Brix": [],
    "Bricks": [],
    "tree height": [],
    "tree height": [],
    "scion survive": [],
    "fruit harvest trait": [],
    "fruit harvest": [],
    "number of branches": [],
}


def build_traits(trait_df):
    trait_features = {}
    for _, trait_row in trait_df.iterrows():
        if trait_row['format'] == 'categorical':
            trait_features[trait_row['trait']
                           ] = trait_row['categories'].split("/")
        if trait_row['format'] == 'multicat':
            trait_features[trait_row['trait']
                           ] = trait_row['categories'].split("/")
    return trait_features


def extract_features(text, features):
    # Use NER to extract named entities
    doc = nlp(text)
    named_entities = set([ent.text.lower()
                         for ent in doc.ents if ent.label_ == "PRODUCT"])

    # Use POS tagging to extract adjectives
    adjectives = set([token.text.lower()
                     for token in doc if token.pos_ == "ADJ"])

    # Use keyword matching to extract features
    extracted_features = {}
    for feature, keywords in features.items():
        for keyword in keywords:
            pattern = r'\b{}\b'.format(keyword)
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted_features[feature] = list(set(matches))

        # Check if the feature was mentioned as a named entity or adjective
        if feature not in extracted_features:
            numerical_values = re.findall(
                r'(?i)(?<=\b{})[ ]+\d+'.format(feature), text, re.IGNORECASE)
            if any(keyword in named_entities for keyword in keywords):
                extracted_features[feature] = list(
                    named_entities.intersection(keywords))[0]
            elif any(keyword in adjectives for keyword in keywords):
                extracted_features[feature] = list(
                    adjectives.intersection(keywords))[0]
            elif numerical_values and keywords == []:
                extracted_features[feature] = [x.strip() for x in numerical_values]

    # return pd.Series(extracted_features)
    return extracted_features


def link_plants(input_transcript, log_file, trait_file, type="transcript", TMP_DIR="tmp/sample"):
    out = {}

    if log_file.endswith('csv'):
        data = pd.read_csv(log_file, skipinitialspace=True)
    elif log_file.endswith('xlsx'):
        data = pd.read_excel(log_file)
    else:
        raise Exception("Geonav Log File type not supported: " + log_file)

    if trait_file:
        traits_df = pd.read_csv(trait_file)
        features = build_traits(traits_df)
    else:
        # features = features_okra
        # features = features_belt
        features = features_citrus_hfl

    if type=="transcript":
        plants = data['unique id'].unique()
        i = 0
        for part in input_transcript.split("new plant"):
            tmp = {}
            if part == "":
                continue
            tmp['transcript'] = part.strip()
            tmp['features'] = extract_features(part, features)
            out[plants[i]] = tmp
            i += 1
    if type == "timestamp_segment":
        plants = data['unique id'].unique()
        i = 0
        print(len(input_transcript['segments']))
        print(len(plants))
        for segment in input_transcript['segments']:
            if segment['text'] == "":
                continue
            tmp = {}
            tmp['transcript'] = segment['text'].strip()
            tmp['features'] = extract_features(segment['text'], features)
            out[plants[i]] = tmp
            i += 1
    with open(os.path.join(TMP_DIR, "link_plant_out.json"), "w") as f:
        json.dump(out, f)
    return out


if __name__ == "__main__":
    sample = "new plant red green stem one pod new plant one pods not flowering plants not flowering"
    with open("tmp/sample/experiment-A-full-data.mp4_transcript.json") as f:
        sample = json.load(f)
    # log = "sample_log.csv"
    # log = "sample_log.xlsx"
    log = "../I04.02.03_USDABeltsTest_20231214-20240306T223033Z-001/I04.02.03_USDABeltsTest_20231214/MDB-02/limited_log.csv"
    # trait_file = "sample_traits.csv"
    trait_file = None
    print(link_plants(sample, log, trait_file, type="timestamp_segment"))
