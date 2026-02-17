from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import Validators, is_back, is_yes, is_no
from utils.helpers import get_app_id, get_lang

router = Router(name="photo_handler")

@router.message(ApplicationState.photo, F.photo)
async def process_photo(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        photo = message.photo[-1]  
        filepath = await FileService.download_photo(message.bot, photo, message.from_user.id)
        if filepath:
            await DB.app.set_photo(app_id, filepath)
        
        await message.answer(t(lang, "application.resume.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.resume)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.photo, F.text)
async def photo_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        data = await state.get_data()
        
        if is_back(message.text):
            if data.get("has_experience"):
                await message.answer(t(lang, "application.last_position.ask"), reply_markup=Keyboards.back(lang))
                await state.set_state(ApplicationState.last_position)
            else:
                await message.answer(t(lang, "application.has_experience.ask"), reply_markup=Keyboards.yes_no(lang))
                await state.set_state(ApplicationState.has_experience)
            return
        
        await message.answer(t(lang, "application.photo.invalid"), reply_markup=Keyboards.back(lang))
    except Exception as e:
        print(f"Error: {e}")
