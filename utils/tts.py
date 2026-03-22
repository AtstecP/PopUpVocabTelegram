import os
from gtts import gTTS

async def generate_voice(text, lang='fr'):
    # gTTS uses 'fr' for French and 'en' for English
    filename = f"temp_voice_{hash(text)}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename