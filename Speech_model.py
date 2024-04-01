import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal

class ListenerThread(QThread):
    recognizedSpeech = pyqtSignal(str)

    def __init__(self,listening):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = listening
    def start_listen(self,is_listen):
        self.is_listening = is_listen


    def run(self):
        with self.microphone as source:
            print("Calibrating microphone...")
            # Adjust the recognizer sensitivity to ambient noise
            self.recognizer.adjust_for_ambient_noise(source)
            print("Say something!")
            print(self.is_listening)
            while self.is_listening:
                print(self.is_listening)
                try:
                    # Listen for the first phrase and extract it into audio data
                    audio = self.recognizer.listen(source)
                    print("Got audio! Recognizing...")
                    # Recognize speech using Google Web Speech API
                    text = self.recognizer.recognize_google(audio)
                    print(f"Google thinks you said: {text}")
                    self.recognizedSpeech.emit(text)
                except sr.UnknownValueError:
                    print("Google could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google; {e}")
