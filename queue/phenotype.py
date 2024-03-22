import spacy
import re
import nltk
import os
import datetime
import pandas as pd
import json
from json import JSONDecodeError
from transformers import AutoTokenizer, AutoModelForCausalLM

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
    "scion survive": [],
    "fruit harvest trait": [],
    "fruit harvest": [],
    "number of branches": [],
}

features_citrus_hfl_gemma = """
{
    "brix": {{data}},
    "tree height": {{data}},
    "scion survive": {{data}},
    "fruit harvest trait": {{data}},
    "number of branches": {{data}}
}
"""
tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b-it")
model = AutoModelForCausalLM.from_pretrained("google/gemma-2b-it")

input_text = f"""<start_of_turn>user
Consider you are a JSON data extraction tool. You can only reply in JSON with the given format and nothing else {features_citrus_hfl_gemma}
brix is often spelled as bricks
scion survive can be alive or dead
fruit harvest trait can be clean or plugged
tree height is sometimes 3 height

Input: PROMPT_INPUT
<start_of_turn>model
"""


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


def segment_headers(txt, possible_headings):
    for heading in possible_headings:
        txt = txt.split(heading)[-1]
    return txt


def remove_unwanted_characters(txt, characters):
    for c in characters:
        txt = txt.replace(c, "")
    return txt


def extract_features(text, features, gemma=False):
    if gemma:
        input_ids = tokenizer(input_text.replace("PROMPT_INPUT", text), max_length=1000,
                              return_tensors="pt", truncation=True)
        token_output = model.generate(**input_ids, max_new_tokens=200)
        output = tokenizer.decode(token_output[0])
        output = segment_headers(output, [
            "<start_of_turn>model",
            "Output:",
            "Extracted data:",
        ])
        output = output.replace("null", "\"null\"")
        output = remove_unwanted_characters(output, [
            "<eos>",
            "```json",
            "```",
            "*",
        ])

        print(output[:20])

        try:
            return json.loads(output)
        except JSONDecodeError as e:
            print("JSONDecodeError", e)
            print(output)
            return {}

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
                extracted_features[feature] = [x.strip()
                                               for x in numerical_values]

    # return pd.Series(extracted_features)
    return extracted_features


def with_moviepy(filename):
    from moviepy.editor import AudioFileClip
    clip = AudioFileClip(filename)
    duration = clip.duration
    return duration


def link_plants(input_transcript, log_file, trait_file, type="transcript", TMP_DIR="tmp/sample", audio_file=None):
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

    if type == "transcript":
        plants = data['unique id'].unique().tolist()
        plants = [str(x) for x in plants]
        i = 0
        for part in input_transcript.split("new plant"):
            tmp = {}
            if part == "":
                continue
            tmp['transcript'] = part.strip()
            # tmp['features'] = extract_features(part.strip(), features)
            tmp['features'] = extract_features(
                part.strip(), features, gemma=True)
            try:
                out[plants[i]] = tmp
            except IndexError:
                print("Error extracting features", plants, i, tmp)
            i += 1
    if type == "timestamp_segment":
        plants = data['unique id'].unique()
        plants = [str(x) for x in plants]
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
    if type == "timestamp_with_log":
        filter_data = data[['UTC', 'unique id', 'fix']]
        # filter_data['time_since_start'] = filter_data['UTC'] - \
        #     filter_data['UTC'][0]
        # filter_data['id_changed_time'] = filter_data['time_since_start'][filter_data['unique id']
        #                                                                  != filter_data['unique id'].shift()]
        # filter_data.dropna(inplace=True)
        # filter_data['id_changed_time'] = filter_data['id_changed_time'] / 100
        filter_data = filter_data[filter_data['fix'] == "GPS"]
        audio_end_time = audio_file[-23:-4]
        audio_end_time = datetime.datetime.strptime(
            audio_end_time, "%Y-%m-%d-%H-%M-%S")
        audio_length = with_moviepy(audio_file)
        audio_start_time = audio_end_time - \
            datetime.timedelta(seconds=audio_length)


        # filter_data = filter_data.loc(
        #     (filter_data['UTC'] >= datetime.datetime.timestamp(audio_start_time)*1000) & (filter_data['UTC'] <= datetime.datetime.timestamp(audio_end_time)*1000))
        
        end_timestamp = pd.Timestamp(
            audio_end_time).timestamp() * 1000  # Convert to milliseconds
        start_timestamp = pd.Timestamp(
            audio_start_time,tz=).timestamp() * 1000  # Convert to milliseconds
        range_filtered_data = filter_data[(filter_data['UTC'] >= start_timestamp) & (
            filter_data['UTC'] <= end_timestamp)]
        print(filter_data)
        print(range_filtered_data)

        print(start_timestamp, "pd tiemstamp")
        print(end_timestamp, "pd tiemstamp")
        # print(audio_end_time)
        # print(audio_length)
        # print(datetime.datetime.timestamp(audio_start_time)*1000)
        # print(datetime.datetime.timestamp(audio_end_time)*1000)

    with open(os.path.join(TMP_DIR, "ai_link_plant_out.json"), "w") as f:
        try:
            json.dump(out, f)
        except:
            print("Error in json dumping", out)
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
