from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import is_back, is_skip
from utils.helpers import get_app_id, get_lang
from services.file_service import FileService

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


@router.message(ApplicationState.resume, F.document)
async def process_resume(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        doc = message.document
        if doc.file_name and not any(doc.file_name.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx']):
            await message.answer(t(lang, "application.resume.invalid"), reply_markup=Keyboards.skip_back(lang))
            return
        
        filepath = await FileService.download_document(message.bot, doc, message.from_user.id)
        if filepath:
            await DB.app.set_resume(app_id, filepath)
        
        await message.answer(t(lang, "application.how_found.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.how_found)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.resume, F.text)
async def resume_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.photo.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.photo)
            return
        
        if is_skip(message.text):
            await message.answer(t(lang, "application.how_found.ask"), reply_markup=Keyboards.skip_back(lang))
            await state.set_state(ApplicationState.how_found)
            return
        
        await message.answer(t(lang, "application.resume.invalid"), reply_markup=Keyboards.skip_back(lang))
    except Exception as e:
        print(f"Error: {e}")