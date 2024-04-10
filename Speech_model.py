from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSound
import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import random
class ListenerThread(QThread):
    recognizedSpeech = pyqtSignal(str)
    playSoundSignal = pyqtSignal()
    def __init__(self):
        super().__init__()
        QThread.__init__(self)
        QObject.__init__(self)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False



    def run(self):
        with self.microphone as source:
            print("Calibrating microphone...")
            # Adjust the recognizer sensitivity to ambient noise
            self.recognizer.adjust_for_ambient_noise(source,duration=2)
            print("Say something!")
            while True:
                if self.is_listening:
                    try:
                        # Listen for the first phrase and extract it into audio data
                        audio = self.recognizer.listen(source, timeout=10,phrase_time_limit=10)
                        print("Got audio! Recognizing...")
                        # Recognize speech using Google Web Speech API
                        text = self.recognizer.recognize_google(audio)
                        print(f"Google thinks you said: {text}")
                        self.recognizedSpeech.emit(text)
                    except sr.WaitTimeoutError:
                        print("Listening timed out while waiting for phrase to start")
                    except sr.UnknownValueError:
                        self.playSoundSignal.emit()
                        print("Google could not understand audio")
                    except sr.RequestError as e:
                        self.playSoundSignal.emit()
                        print(f"Could not request results from Google; {e}")
                    except Exception as e:
                        self.playSoundSignal.emit()
                        print(f"An unexpected error occurred: {e}")

    def start_listening(self):
        self.is_listening = True

    def stop_listening(self):
        self.is_listening = False