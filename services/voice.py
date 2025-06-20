from gtts import gTTS
from pathlib import Path

def generate_voice(text: str, filename: str = "lesson.mp3") -> str:
    output_path = Path("assets/voices") / filename
    tts = gTTS(text=text, lang="ru")
    tts.save(str(output_path))
    return str(output_path)
