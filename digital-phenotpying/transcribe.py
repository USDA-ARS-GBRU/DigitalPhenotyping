from pathlib import Path  # type: ignore
from moviepy.editor import *
import json
import whisper_timestamped

model = whisper_timestamped.load_model("base.en")


def whisper_speech_recognition(audio_file, TMP_DIR):
    audio_path = Path(audio_file)

    audio = whisper_timestamped.load_audio(audio_file)
    result = whisper_timestamped.transcribe(
        model, audio, beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), vad=True, remove_punctuation_from_words=True)
    with open(os.path.join(TMP_DIR, audio_path.name + "_transcript.json"), "w") as f:
        json.dump(result, f)
    return result


def transcribe(audio_file, TMP_DIR="tmp/sample", model="whisper"):
    if model == "whisper":
        result = whisper_speech_recognition(audio_file, TMP_DIR)
        return result


if __name__ == "__main__":
    audio_file = "../1689176449522.wav"
    audio_file = "../I04.02.03_USDABeltsTest_20231214-20240306T223033Z-001/I04.02.03_USDABeltsTest_20231214/MDB-02/experiment-A-full-data.mp4"
    print(transcribe(audio_file, model="whisper"))
