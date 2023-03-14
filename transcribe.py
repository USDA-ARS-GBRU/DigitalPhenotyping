import speech_recognition as sr


r = sr.Recognizer()

with sr.AudioFile("ML_ScionPhenotyping_test.wav") as source:
    audio = r.record(source)  # read the entire audio file

# recognize speech using Google Speech Recognition
try:
    text = r.recognize_google(audio)
    print("Google Speech Recognition thinks you said:\n>>>" + text)
    with open("transcript.txt", "w") as f:
        f.write(text)
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print(
        "Could not request results from Google Speech Recognition service; {0}".format(e))
except Exception as e:
    print(e)
