import speech_recognition as sr
from pathlib import Path
from moviepy.editor import *

r = sr.Recognizer()


def transcribe(audio_file, TMP_DIR="tmp/sample"):
    audio_path = Path(audio_file)
    if audio_path.suffix == ".mp4":
        video = AudioFileClip(audio_file)
        audio_path = os.path.join(TMP_DIR, f"{audio_path.stem}.wav")
        video.write_audiofile(audio_path)

    with sr.AudioFile(str(audio_path)) as source:
        audio = r.record(source)  # read the entire audio file

    # recognize speech using Google Speech Recognition
    try:
        text = r.recognize_google(audio)
        return text
        # print("Google Speech Recognition thinks you said:\n>>>" + text)
        # with open(f"transcript_{audio_path}.txt", "w") as f:
        #     f.write(text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(e))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    audio_file = "../1689176449522.wav"
    audio_file = "../I04.02.03_USDABeltsTest_20231214-20240306T223033Z-001\I04.02.03_USDABeltsTest_20231214\MDB-02\experiment-A-full-data.mp4"
    print(transcribe(audio_file))
