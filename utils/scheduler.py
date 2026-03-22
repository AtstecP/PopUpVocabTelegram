import random
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .tts import generate_voice

# 1. Initialize the scheduler FIRST
scheduler = AsyncIOScheduler()

# We will save the dispatcher here when the bot starts
global_dp = None

async def trigger_random_exercise(bot: Bot, user_id: int):
    from .database import db
    from . import modes 

    try:
        user = db.get_user(user_id)
        if not user.get('is_active', True) or user.get('waiting_ack', False):
            return

        lang = user.get('target_lang', 'fr')
        vocab = db.get_vocab(lang)
        if not vocab: return
        
        word = random.choice(list(vocab.keys()))
        details = vocab[word]

        active_modes = [m for m, active in user["modes"].items() if active]
        if not active_modes: return
        mode_name = random.choice(active_modes)

        # Voice is common for all modes
        audio_path = await generate_voice(word, lang=lang)
        await bot.send_voice(user_id, FSInputFile(audio_path))
        os.remove(audio_path)

        db.update_user(user_id, waiting_ack=True)

        # --- THE SMART PART ---
        if mode_name == "typing":
            # Fetch the state context manually using our saved Dispatcher
            state = global_dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
            await modes.typing.send_task(bot, user_id, word, details, lang, state)
        else:
            mode_map = {
                "definition": modes.definition.send_task,
                "test": modes.test.send_task
            }
            await mode_map[mode_name](bot, user_id, word, details, lang)

    except Exception as e:
        logging.error(f"Scheduler error: {e}")


# 3. Update setup_scheduler to accept `dp`
def setup_scheduler(bot: Bot, dp: Dispatcher):
    global global_dp
    global_dp = dp  # Save it so trigger_random_exercise can use it later
    
    from .database import db
    
    for uid in db.users:
        user = db.users[uid]
        if user.get('is_active', True):
            scheduler.add_job(
                trigger_random_exercise, 
                'interval', 
                minutes=user.get('interval', 15), 
                id=f"job_{uid}", 
                args=[bot, uid]
            )
    return scheduler