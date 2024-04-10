import webbrowser
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSound
import subprocess
def there_exists(terms, voice):
    # voice = " ".join([i.lower() for i in voice.split(" ")])
    # print(voice)
    for term in terms:
        if term in voice.lower():
            return True

def open_wechat():
    try:
        subprocess.Popen(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    except Exception as e:
        print(f"Error opening WeChat: {e}")
def respond(voice):
    if there_exists(["search for"], voice) and 'youtube' not in voice:
        search_term = voice.split("for")[-1]
        url = f"https://google.com/search?q={search_term}"
        webbrowser.get().open(url)
        QSound("Audio/乌拉呀哈（slow).wav")
    if there_exists(["youtube"],voice):
        search_term = voice.split("for")[-1]
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.get().open(url)
        QSound("Audio/乌拉呀哈（fast).wav).wav")
    if there_exists(["wechat"],voice):
        open_wechat()
    if there_exists(["chat gpt"],voice):
        url = f"https://chat.openai.com/"
        webbrowser.get().open(url)