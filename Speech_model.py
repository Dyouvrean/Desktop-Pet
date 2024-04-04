import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal
import concurrent.futures
import asyncio
class ListenerThread(QThread):
    recognizedSpeech = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False

    async def recognize_audio(self, audio):
        # This function runs the blocking recognize_google call in a separate thread
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.recognizer.recognize_google, audio)
            return await asyncio.wrap_future(future)
    def run(self):
        with self.microphone as source:
            print("Calibrating microphone...")
            # Adjust the recognizer sensitivity to ambient noise
            self.recognizer.adjust_for_ambient_noise(source)
            print("Say something!")
            print(self.is_listening)
            while True:
                print(self.is_listening)
                if self.is_listening:
                    try:
                        # Listen for the first phrase and extract it into audio data
                        audio = self.recognizer.listen(source)
                        print("Got audio! Recognizing...")
                        # Recognize speech using Google Web Speech API
                        text = asyncio.run(self.recognize_audio(audio))
                        #text = self.recognizer.recognize_google(audio)
                        print(f"Google thinks you said: {text}")
                        self.recognizedSpeech.emit(text)
                    except sr.UnknownValueError:
                        print("Google could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google; {e}")
                else:
                    self.msleep(100)

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False