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