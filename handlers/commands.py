from aiogram import Router, types
from aiogram.filters import Command
from utils.database import db 
from utils import scheduler

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    user = db.get_user(uid)
    
    if not user:
        db.create_user(uid)
        # Initialize their first interval job here if needed
    
    db.update_user(uid, is_active=True, waiting_ack=False)
    await message.answer(
        f"Salut {message.from_user.first_name}! Your French/English tutor is active.\n"
        "Commands:\n/stop - Pause the bot\n/now - Get a word immediately\n/modes - Settings\n/interval - notification time"
    )

@router.message(Command("stop"))
async def cmd_stop(message: types.Message):
    db.update_user(message.from_user.id, is_active=False)
    await message.answer("⏸ Bot paused. You won't receive new words until you type /start.")

@router.message(Command("now"))
async def cmd_now(message: types.Message):
    from utils.scheduler import trigger_random_exercise
    # Reset waiting_ack so they can actually get a word now
    db.update_user(message.from_user.id, waiting_ack=False)
    await trigger_random_exercise(message.bot, message.from_user.id)