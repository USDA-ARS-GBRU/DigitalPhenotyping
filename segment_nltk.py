import nltk
nltk.download('punkt')

# Load the text file as a string
with open('transcript.txt', 'r') as f:
    text = f.read()

# Tokenize the text into sentences
sentences = nltk.sent_tokenize(text)

# Define a function to check if a sentence contains a mention of a new sample


def contains_new_sample(sentence):
    # Here, you would need to define your own logic to check if a sentence mentions a new sample
    # For example, you could look for keywords like "sample", "product", or specific sample names
    # and return True if the sentence contains a mention of a new sample
    if "new tree" in sentence.lower():
        return True
    return False


# Segment the text into parts where a new sample is being discussed
segments = []
current_segment = []
for sentence in sentences:
    if contains_new_sample(sentence):
        if current_segment:
            segments.append(" ".join(current_segment))
            current_segment = []
    current_segment.append(sentence)
segments.append(" ".join(current_segment))

# Print the segments
for i, segment in enumerate(segments):
    print(f"Sample {i+1} observations:\n{segment}")
