from gtts import gTTS
from pathlib import Path
import logging

def generate_voice(text: str, filename: str = "lesson.mp3") -> str:
    output_path = Path("assets/voices") / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        tts = gTTS(text=text, lang="ru")
        tts.save(str(output_path))
        return str(output_path)
    except Exception as e:
        logging.error(f"Ошибка при генерации голосового файла: {e}")
        return ""
