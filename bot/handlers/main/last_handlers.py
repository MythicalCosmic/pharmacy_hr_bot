from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import is_back, is_skip, Validators
from utils.helpers import get_app_id, get_lang
from utils.helpers import get_lang

router = Router(name="last_handlers")


@router.message(ApplicationState.how_found, F.text)
async def process_how_found(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.resume.ask"), reply_markup=Keyboards.skip_back(lang))
            await state.set_state(ApplicationState.resume)
            return
        
        if is_skip(message.text):
            await message.answer(t(lang, "application.additional_notes.ask"), reply_markup=Keyboards.skip_back(lang))
            await state.set_state(ApplicationState.additional_notes)
            return
        
        is_valid, cleaned = Validators.text_field(message.text)
        if not is_valid:
            await message.answer(t(lang, "application.how_found.invalid"), reply_markup=Keyboards.skip_back(lang))
            return
        
        app_id = await get_app_id(state)
        await DB.app.update(app_id, how_found_us=cleaned)
        await message.answer(t(lang, "application.additional_notes.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.additional_notes)
    except Exception as e:
        print(f"Error: {e}")