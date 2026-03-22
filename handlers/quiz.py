from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from utils.database import db

router = Router()

class QuizState(StatesGroup):
    waiting_for_typing = State()

@router.callback_query(F.data.startswith("q:"))
async def handle_quiz_button(callback: types.CallbackQuery):
    _, res, word = callback.data.split(":")
    data = db.get_vocab(db.get_user(callback.from_user.id)['target_lang'])
    correct_def = data[word]['definition']

    if res == "correct":
        text = f"✅<b>{word}</b>\n\n<blockquote>{correct_def}</blockquote>"
    else:
        text = f"❌<b>{word}</b>\n\n<blockquote>{correct_def}</blockquote>"
    
    # CRITICAL: Unblock the queue now that the user interacted
    db.update_user(callback.from_user.id, waiting_ack=False)
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()

@router.message(QuizState.waiting_for_typing)
async def handle_typing_attempt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get('correct_word')
    attempts = data.get('attempts', 0)

    if message.text.lower().strip() == correct.lower().strip():
        await message.answer("✅ Correct! Jarvis is impressed.")
        db.update_user(message.from_user.id, waiting_ack=False)
        await state.clear()
    elif attempts < 1:
        await state.update_data(attempts=attempts + 1)
        await message.answer("❌ Not quite. Try one more time!")
    else:
        await message.answer(f"❌ Wrong. The answer was: <b>{correct}</b>", parse_mode="HTML")
        db.update_user(message.from_user.id, waiting_ack=False)
        await state.clear()