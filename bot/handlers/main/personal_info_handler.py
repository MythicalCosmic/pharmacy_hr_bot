from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState, MenuState
from bot.states.user import MenuState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import is_back
from utils.helpers import get_app_id, get_lang
from bot.validators.validator import Validators

router = Router(name="personal_info_handler")

@router.message(ApplicationState.first_name, F.text)
async def process_first_name(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "menu.main"), reply_markup=Keyboards.main_menu(lang))
            await state.set_state(MenuState.main)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.name(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.first_name.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_first_name(app_id, cleaned)
        await message.answer(t(lang, "application.last_name.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.last_name)
    except Exception as e:
        print(f"Error: {e}")