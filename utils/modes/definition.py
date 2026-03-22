from aiogram import Bot

async def send_task(bot: Bot, user_id: int, word: str, details: dict, lang: str):
    # Format the flashcard text
    text = (
        f"📖 <b>Flashcard ({lang.upper()})</b>\n\n"
        f"<b>{word}</b>\n"
        f"<i>{details.get('partOfSpeech', 'word')}</i>\n\n"
        f"<blockquote>🇬🇧 {details['definition']}</blockquote>"
    )
    
    await bot.send_message(user_id, text, parse_mode="HTML")
    
    # Optional: Since there is no 'answer' to type, we can unblock the queue 
    # immediately or add an "OK" button. For now, let's let the user read it.
    from ..database import db
    db.update_user(user_id, waiting_ack=False)