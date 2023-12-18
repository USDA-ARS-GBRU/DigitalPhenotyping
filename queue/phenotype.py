import spacy
import re
import nltk
import pandas as pd
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nlp = spacy.load('en_core_web_sm')

features_okra = {
    'stem': ['red green'],
    'flowering': ['not flowering', 'one pod']
}

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
                extracted_features[feature] = list(set(matches))

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

def link_plants(sample, log_file):
    out = {}
    if log_file.endswith('csv'):
        data = pd.read_csv(log_file) 
    elif log_file.endswith('xlsx'):
        data = pd.read_excel(log_file) 
    else:
        raise Exception("Geonav Log File type not supported: "+log_file)
    plants = data['unique id'].unique()
    i=0
    for part in sample.split("new plant"):
        tmp = {}
        if part == "":
            continue
        tmp['transcript'] = part.strip()
        tmp['features'] = extract_features(part)
        out[plants[i]] = tmp
        i += 1
    return out

if __name__ == "__main__":
    sample = "new plant red green stem one pod new plant one pods not flowering plants not flowering"
    # log = "sample_log.csv"
    log = "sample_log.xlsx"
    print(link_plants(sample, log))
