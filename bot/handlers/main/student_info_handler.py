from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import Validators, get_level, is_yes, is_back, is_no
from utils.helpers import get_app_id, get_lang
from utils.helpers import get_lang

router = Router(name="student_info_handler")



@router.message(ApplicationState.is_student, F.text)
async def process_is_student(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.email.ask"), reply_markup=Keyboards.skip_back(lang))
            await state.set_state(ApplicationState.email)
            return
        
        app_id = await get_app_id(state)
        
        if is_yes(message.text):
            await DB.app.set_is_student(app_id, True)
            await state.update_data(is_student=True)
            await message.answer(t(lang, "application.education_place.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.education_place)
        elif is_no(message.text):
            await DB.app.set_is_student(app_id, False)
            await state.update_data(is_student=False)
            await message.answer(t(lang, "application.russian_level.ask"), reply_markup=Keyboards.language_level(lang))
            await state.set_state(ApplicationState.russian_level)
        else:
            await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.education_place, F.text)
async def process_education_place(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
            await state.set_state(ApplicationState.is_student)
            return
        
        is_valid, cleaned = Validators.text_field(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.education_place.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        app_id = await get_app_id(state)
        await DB.app.update(app_id, education_place=cleaned)
        await message.answer(t(lang, "application.education_level.ask"), reply_markup=Keyboards.language_level(lang))
        await state.set_state(ApplicationState.education_level)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.education_level, F.text)
async def process_education_level(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.education_place.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.education_place)
            return
        
        level = get_level(message.text)
        if not level:
            await message.answer(t(lang, "application.education_level.ask"), reply_markup=Keyboards.language_level(lang))
            return
        
        app_id = await get_app_id(state)
        from database.models.enums import LevelEnum
        await DB.app.update(app_id, education_level=LevelEnum(level))
        await message.answer(t(lang, "application.russian_level.ask"), reply_markup=Keyboards.language_level(lang))
        await state.set_state(ApplicationState.russian_level)
    except Exception as e:
        print(f"Error: {e}")