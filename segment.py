import pandas as pd

# Load the text file as a string
with open('transcript.txt', 'r') as f:
    text = f.read()

segments: str = text.split("new tree")
segments = [seg.strip() for seg in segments if seg.strip() != ""]

df = pd.read_csv("test_log.csv")
df.sort_values(by='UTC', inplace=True)

if len(segments) == len(df):
    df['transcript'] = segments
    df.to_csv("test_log_with_transcript.csv", index=False)
