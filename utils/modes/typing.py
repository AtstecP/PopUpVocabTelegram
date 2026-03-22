from aiogram import Bot
from aiogram.fsm.context import FSMContext
# Import your states from handlers
from handlers.quiz import QuizState 

async def send_task(bot: Bot, user_id: int, word: str, details: dict, lang: str, state: FSMContext):
    text = (
        f"⌨️ <b>Typing Challenge ({lang.upper()})</b>\n\n"
        f"Translate this to {lang.upper()}:\n"
        f"<blockquote>{details['definition']}</blockquote>"
    )
    
    await bot.send_message(user_id, text, parse_mode="HTML")

    # 1. Set the bot to "Listening" mode
    await state.set_state(QuizState.waiting_for_typing)
    
    # 2. Store the correct answer and reset attempts
    await state.update_data(correct_word=word, attempts=0)