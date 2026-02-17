from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import MenuState
from bot.states.user import MenuState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import get_selected_lang, is_back
from utils.helpers import get_lang


router = Router(name="settings_handler")



@router.message(MenuState.settings, F.text)
async def settings_handler(message: Message, state: FSMContext, db_user=None, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        text = message.text        
        
        if is_back(text):
            await message.answer(
                t(lang, "menu.main"),
                reply_markup=Keyboards.main_menu(lang)
            )
            await state.set_state(MenuState.main)
            await DB.user.set_state(message.from_user.id, MenuState.main.state)
            return
        
        selected_lang = get_selected_lang(text)
        if selected_lang:
            if db_user:
                await DB.user.set_language(db_user.id, selected_lang)
            
            await state.update_data(lang=selected_lang)
            await message.answer(
                t(selected_lang, "menu.main"),
                reply_markup=Keyboards.main_menu(selected_lang)
            )
            await state.set_state(MenuState.main)
            await DB.user.set_state(message.from_user.id, MenuState.main.state)
        else:
            await message.answer(
                t(lang, "menu.settings"),
                reply_markup=Keyboards.settings(lang)
            )
    except Exception as e:
        print(f"Error in settings_handler: {e}")

