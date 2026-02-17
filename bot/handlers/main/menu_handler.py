from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import MenuState
from bot.states.user import MenuState
from services.language_service import t
from database.db import DB
from bot.states.user import ApplicationState
from services.language_service import t, btn
from utils.helpers import get_lang


router = Router(name="menu_handler")

@router.message(MenuState.main, F.text)
async def main_menu_handler(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        text = message.text
        
        start_buttons = [btn("uz", "start_application"), btn("ru", "start_application"), btn("en", "start_application")]
        settings_buttons = [btn("uz", "settings"), btn("ru", "settings"), btn("en", "settings")]
        
        if text in start_buttons:
            app, created = await DB.app.get_or_create_draft(message.from_user.id)
            await state.update_data(app_id=app.id, lang=lang)
            
            await message.answer(
                t(lang, "application.start"),
            )
            await message.answer(
                t(lang, "application.first_name.ask"),
                reply_markup=Keyboards.back(lang)
            )
            await state.set_state(ApplicationState.first_name)
            await DB.user.set_state(message.from_user.id, ApplicationState.first_name.state)
        elif text in settings_buttons:
            await message.answer(
                t(lang, "menu.settings"),
                reply_markup=Keyboards.settings(lang)
            )
            await state.set_state(MenuState.settings)
            await DB.user.set_state(message.from_user.id, MenuState.settings.state)
        
        else:
            await message.answer(
                t(lang, "menu.main"),
                reply_markup=Keyboards.main_menu(lang)
            )
    except Exception as e:
        print(f"Error in main_menu_handler: {e}")
        lang = await get_lang(state, user_lang)
        await message.answer(t(lang, "errors.general"))