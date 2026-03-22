import random
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def send_task(bot: Bot, user_id: int, word: str, details: dict, lang: str):
    from ..database import db # Go up one level to find db
    
    vocab = db.get_vocab(lang)
    correct = details['definition']
    others = [v['definition'] for k, v in vocab.items() if v['definition'] != correct]
    options = random.sample(others, min(3, len(others))) + [correct]
    random.shuffle(options)
    
    builder = InlineKeyboardBuilder()
    for opt in options:
        res = "correct" if opt == correct else "wrong"
        builder.button(text=opt, callback_data=f"q:{res}:{word}")
    
    builder.adjust(1)
    await bot.send_message(
        user_id, 
        f"❓ <b>Que signifie: {word}?</b>", 
        reply_markup=builder.as_markup(), 
        parse_mode="HTML"
    )