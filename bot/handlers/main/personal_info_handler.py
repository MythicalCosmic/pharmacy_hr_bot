from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState, MenuState
from bot.states.user import MenuState
from services.language_service import t
from database.db import DB
from services.language_service import t
from bot.validators.validator import get_gender, is_back, is_skip
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
            await DB.user.set_state(message.from_user.id, MenuState.main.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.name(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.first_name.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_first_name(app_id, cleaned)
        await message.answer(t(lang, "application.last_name.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.last_name)
        await DB.user.set_state(message.from_user.id, ApplicationState.last_name.state)
    except Exception as e:
        print(f"Error: {e}")



@router.message(ApplicationState.last_name, F.text)
async def process_last_name(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.first_name.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.first_name)
            await DB.user.set_state(message.from_user.id, ApplicationState.first_name.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.name(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.last_name.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_last_name(app_id, cleaned)
        await message.answer(t(lang, "application.birth_date.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.birth_date)
        await DB.user.set_state(message.from_user.id, ApplicationState.birth_date.state)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.birth_date, F.text)
async def process_birth_date(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.last_name.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.last_name)
            await DB.user.set_state(message.from_user.id, ApplicationState.last_name.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, birth_date = Validators.birth_date(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.birth_date.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_birth_date(app_id, birth_date)
        await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
        await state.set_state(ApplicationState.gender)
        await DB.user.set_state(message.from_user.id, ApplicationState.gender.state)
    except Exception as e:
        print(f"Error: {e}")



@router.message(ApplicationState.gender, F.text)
async def process_gender(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.birth_date.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.birth_date)
            await DB.user.set_state(message.from_user.id, ApplicationState.birth_date.state)
            return
        
        app_id = await get_app_id(state)
        gender = get_gender(message.text)
        
        if not gender:
            await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
            return
        
        from database.models.enums.application_status import GenderEnum
        await DB.app.set_gender(app_id, GenderEnum(gender))
        await message.answer(t(lang, "application.address.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.address)
        await DB.user.set_state(message.from_user.id, ApplicationState.address.state)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.address, F.text)
async def process_address(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
            await state.set_state(ApplicationState.gender)
            await DB.user.set_state(message.from_user.id, ApplicationState.gender.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.address(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.address.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_address(app_id, cleaned)
        await message.answer(t(lang, "application.phone.ask"), reply_markup=Keyboards.phone(lang))
        await state.set_state(ApplicationState.phone)
        await DB.user.set_state(message.from_user.id, ApplicationState.phone.state)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        phone = message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
        
        await DB.app.set_phone(app_id, phone)
        await message.answer(t(lang, "application.email.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.email)
        await DB.user.set_state(message.from_user.id, ApplicationState.email.state)
    except Exception as e:
        print(f"Error: {e}")



@router.message(ApplicationState.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.address.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.address)
            await DB.user.set_state(message.from_user.id, ApplicationState.address.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.phone(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.phone.invalid"), reply_markup=Keyboards.phone(lang))
            return
        
        await DB.app.set_phone(app_id, cleaned)
        await message.answer(t(lang, "application.email.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.email)
        await DB.user.set_state(message.from_user.id, ApplicationState.email.state)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.email, F.text)
async def process_email(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.phone.ask"), reply_markup=Keyboards.phone(lang))
            await state.set_state(ApplicationState.phone)
            await DB.user.set_state(message.from_user.id, ApplicationState.phone.state)
            return
        
        if is_skip(message.text):
            await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
            await state.set_state(ApplicationState.is_student)
            await DB.user.set_state(message.from_user.id, ApplicationState.is_student.state)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.email(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.email.invalid"), reply_markup=Keyboards.skip_back(lang))
            return
        
        await DB.app.update(app_id, email=cleaned)
        await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
        await state.set_state(ApplicationState.is_student)
        await DB.user.set_state(message.from_user.id, ApplicationState.is_student.state)
    except Exception as e:
        print(f"Error: {e}")