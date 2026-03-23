from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.database import db

router = Router()

@router.message(Command("modes"))
async def cmd_modes(message: types.Message):
    uid = message.from_user.id
    user = db.get_user(uid)
    
    builder = InlineKeyboardBuilder()
    
    # 1. Mode Toggles
    for m, s in user["modes"].items():
        builder.button(text=f"{'✅' if s else '❌'} {m.capitalize()}", callback_data=f"toggle:{m}")
    
    # 2. Language Switcher
    current_lang = user.get('target_lang', 'fr').upper()
    builder.button(text=f"🌐 Language: {current_lang}", callback_data="switch_lang")
    
    builder.adjust(1)
    await message.answer("🛠 <b>Your Settings:</b>", reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data == "switch_lang")
async def handle_switch_lang(callback: types.CallbackQuery):
    uid = callback.from_user.id
    user = db.get_user(uid)
    
    # Toggle the language logic
    new_lang = 'en' if user.get('target_lang', 'fr') == 'fr' else 'fr'
    
    # Save it to the database
    db.update_user(uid, target_lang=new_lang)
    
    # Update our local dictionary for the keyboard builder
    user['target_lang'] = new_lang 
    
    # Re-build the keyboard with the new language
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    
    for m, s in user["modes"].items():
        builder.button(text=f"{'✅' if s else '❌'} {m.capitalize()}", callback_data=f"toggle:{m}")
    
    current_lang = user.get('target_lang', 'fr').upper()
    builder.button(text=f"🌐 Language: {current_lang}", callback_data="switch_lang")
    
    builder.adjust(1)
    
    # EDIT the message instead of sending a new one
    await callback.message.edit_text(
        "🛠 <b>Your Settings:</b>", 
        reply_markup=builder.as_markup(), 
        parse_mode="HTML"
    )
    
    # Show a little popup toast notification at the top of Telegram
    await callback.answer(f"Switched to {new_lang.upper()}!")

@router.callback_query(F.data.startswith("toggle:"))
async def handle_toggle(callback: types.CallbackQuery):
    uid = callback.from_user.id
    mode = callback.data.split(":")[1]
    
    user = db.get_user(uid)
    user["modes"][mode] = not user["modes"][mode]
    db.save_all()
    
    # 1. Re-generate the keyboard with the NEW states
    builder = InlineKeyboardBuilder()
    for m, s in user["modes"].items():
        builder.button(text=f"{'✅' if s else '❌'} {m.capitalize()}", callback_data=f"toggle:{m}")
    
    current_lang = user.get('target_lang', 'fr').upper()
    builder.button(text=f"🌐 Language: {current_lang}", callback_data="switch_lang")
    builder.adjust(1)

    # 2. EDIT the message instead of sending a new one
    await callback.message.edit_text(
        "🛠 <b>Your Settings:</b>", 
        reply_markup=builder.as_markup(), 
        parse_mode="HTML"
    )
    await callback.answer() 

@router.message(Command("interval"))
async def cmd_interval(message: types.Message):
    builder = InlineKeyboardBuilder()
    
    # Common interval options in minutes
    options = [5, 15, 30, 60, 120]
    
    for mins in options:
        label = f"⏱ {mins} min"
        builder.button(text=label, callback_data=f"set_int:{mins}")
    
    builder.adjust(2) # Two buttons per row
    
    uid = message.from_user.id
    current = db.get_user(uid).get('interval', 15)
    
    await message.answer(
        f"🕒 <b>Current Interval: {current} minutes</b>\nHow often should Jarvis send you a word?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_int:"))
async def handle_interval_change(callback: types.CallbackQuery):
    new_interval = int(callback.data.split(":")[1])
    uid = callback.from_user.id
    
    # 1. Update Database
    db.update_user(uid, interval=new_interval)
    
    # 2. Update the actual Scheduler Job in real-time
    from utils.scheduler import scheduler
    job_id = f"job_{uid}"
    
    if scheduler.get_job(job_id):
        scheduler.reschedule_job(job_id, trigger='interval', minutes=new_interval)
    
    await callback.message.edit_text(f"✅ Interval updated to <b>{new_interval} minutes</b>!", parse_mode="HTML")
    await callback.answer()