import webbrowser
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSound

def there_exists(terms, voice):
    for term in terms:
        if term in voice:
            return True
def respond(voice):
    if there_exists(["search for"], voice):
        search_term = voice.split("for")[-1]
        url = f"https://google.com/search?q={search_term}"
        webbrowser.get().open(url)
