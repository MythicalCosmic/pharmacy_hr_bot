from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from bot.keyboards.reply import Keyboards
from bot.states.user import MenuState
from bot.validators.validator import get_selected_lang
from bot.states.user import MenuState, ApplicationState
from services.language_service import t, btn
from database.db import DB
# from services.file_service import FileService

router = Router()


# ==================== SETTINGS ====================


# ==================== FIRST NAME ====================




# ==================== LAST NAME ====================

@router.message(ApplicationState.last_name, F.text)
async def process_last_name(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.first_name.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.first_name)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.name(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.last_name.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_last_name(app_id, cleaned)
        await message.answer(t(lang, "application.birth_date.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.birth_date)
    except Exception as e:
        print(f"Error: {e}")


# ==================== BIRTH DATE ====================

@router.message(ApplicationState.birth_date, F.text)
async def process_birth_date(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.last_name.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.last_name)
            return
        
        app_id = await get_app_id(state)
        is_valid, birth_date = Validators.birth_date(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.birth_date.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_birth_date(app_id, birth_date)
        await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
        await state.set_state(ApplicationState.gender)
    except Exception as e:
        print(f"Error: {e}")


# ==================== GENDER ====================

@router.message(ApplicationState.gender, F.text)
async def process_gender(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.birth_date.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.birth_date)
            return
        
        app_id = await get_app_id(state)
        gender = get_gender(message.text)
        
        if not gender:
            await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
            return
        
        from database.models.enums import GenderEnum
        await DB.app.set_gender(app_id, GenderEnum(gender))
        await message.answer(t(lang, "application.address.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.address)
    except Exception as e:
        print(f"Error: {e}")


# ==================== ADDRESS ====================

@router.message(ApplicationState.address, F.text)
async def process_address(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.gender.ask"), reply_markup=Keyboards.gender(lang))
            await state.set_state(ApplicationState.gender)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.address(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.address.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        await DB.app.set_address(app_id, cleaned)
        await message.answer(t(lang, "application.phone.ask"), reply_markup=Keyboards.phone(lang))
        await state.set_state(ApplicationState.phone)
    except Exception as e:
        print(f"Error: {e}")


# ==================== PHONE ====================

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
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.address.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.address)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.phone(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.phone.invalid"), reply_markup=Keyboards.phone(lang))
            return
        
        await DB.app.set_phone(app_id, cleaned)
        await message.answer(t(lang, "application.email.ask"), reply_markup=Keyboards.skip_back(lang))
        await state.set_state(ApplicationState.email)
    except Exception as e:
        print(f"Error: {e}")


# ==================== EMAIL ====================

@router.message(ApplicationState.email, F.text)
async def process_email(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.phone.ask"), reply_markup=Keyboards.phone(lang))
            await state.set_state(ApplicationState.phone)
            return
        
        if is_skip(message.text):
            await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
            await state.set_state(ApplicationState.is_student)
            return
        
        app_id = await get_app_id(state)
        is_valid, cleaned = Validators.email(message.text)
        
        if not is_valid:
            await message.answer(t(lang, "application.email.invalid"), reply_markup=Keyboards.skip_back(lang))
            return
        
        await DB.app.update(app_id, email=cleaned)
        await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
        await state.set_state(ApplicationState.is_student)
    except Exception as e:
        print(f"Error: {e}")


# ==================== IS STUDENT ====================

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
            # Invalid input - show keyboard again
            await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
    except Exception as e:
        print(f"Error: {e}")


# ==================== EDUCATION PLACE ====================

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


# ==================== EDUCATION LEVEL ====================

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


# ==================== RUSSIAN LEVEL ====================

@router.message(ApplicationState.russian_level, F.text)
async def process_russian_level(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        data = await state.get_data()
        
        if is_back(message.text):
            if data.get("is_student"):
                await message.answer(t(lang, "application.education_level.ask"), reply_markup=Keyboards.language_level(lang))
                await state.set_state(ApplicationState.education_level)
            else:
                await message.answer(t(lang, "application.is_student.ask"), reply_markup=Keyboards.yes_no(lang))
                await state.set_state(ApplicationState.is_student)
            return
        
        level = get_level(message.text)
        if not level:
            await message.answer(t(lang, "application.russian_level.ask"), reply_markup=Keyboards.language_level(lang))
            return
        
        app_id = await get_app_id(state)
        from database.models.enums import LevelEnum
        await DB.app.set_russian_level(app_id, LevelEnum(level))
        await message.answer(t(lang, "application.russian_voice.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.russian_voice)
    except Exception as e:
        print(f"Error: {e}")


# ==================== RUSSIAN VOICE ====================

@router.message(ApplicationState.russian_voice, F.voice)
async def process_russian_voice(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        filepath = await FileService.download_voice(message.bot, message.voice, message.from_user.id, "russian")
        if filepath:
            await DB.app.set_russian_voice(app_id, filepath)
        
        await message.answer(t(lang, "application.english_level.ask"), reply_markup=Keyboards.language_level(lang))
        await state.set_state(ApplicationState.english_level)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.russian_voice, F.text)
async def russian_voice_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.russian_level.ask"), reply_markup=Keyboards.language_level(lang))
            await state.set_state(ApplicationState.russian_level)
            return
        
        await message.answer(t(lang, "application.russian_voice.invalid"), reply_markup=Keyboards.back(lang))
    except Exception as e:
        print(f"Error: {e}")


# ==================== ENGLISH LEVEL ====================

@router.message(ApplicationState.english_level, F.text)
async def process_english_level(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.russian_voice.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.russian_voice)
            return
        
        level = get_level(message.text)
        if not level:
            await message.answer(t(lang, "application.english_level.ask"), reply_markup=Keyboards.language_level(lang))
            return
        
        app_id = await get_app_id(state)
        from database.models.enums import LevelEnum
        await DB.app.set_english_level(app_id, LevelEnum(level))
        await message.answer(t(lang, "application.english_voice.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.english_voice)
    except Exception as e:
        print(f"Error: {e}")


# ==================== ENGLISH VOICE ====================

@router.message(ApplicationState.english_voice, F.voice)
async def process_english_voice(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        filepath = await FileService.download_voice(message.bot, message.voice, message.from_user.id, "english")
        if filepath:
            await DB.app.set_english_voice(app_id, filepath)
        
        await message.answer(t(lang, "application.has_experience.ask"), reply_markup=Keyboards.yes_no(lang))
        await state.set_state(ApplicationState.has_experience)
    except Exception as e:
        print(f"Error: {e}")


@router.message(ApplicationState.english_voice, F.text)
async def english_voice_text(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.english_level.ask"), reply_markup=Keyboards.language_level(lang))
            await state.set_state(ApplicationState.english_level)
            return
        
        await message.answer(t(lang, "application.english_voice.invalid"), reply_markup=Keyboards.back(lang))
    except Exception as e:
        print(f"Error: {e}")


# ==================== HAS EXPERIENCE ====================

@router.message(ApplicationState.has_experience, F.text)
async def process_has_experience(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.english_voice.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.english_voice)
            return
        
        app_id = await get_app_id(state)
        
        if is_yes(message.text):
            await DB.app.update(app_id, has_work_experience=True)
            await state.update_data(has_experience=True)
            await message.answer(t(lang, "application.experience_years.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.experience_years)
        elif is_no(message.text):
            await DB.app.update(app_id, has_work_experience=False)
            await state.update_data(has_experience=False)
            await message.answer(t(lang, "application.photo.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.photo)
        else:
            await message.answer(t(lang, "application.has_experience.ask"), reply_markup=Keyboards.yes_no(lang))
    except Exception as e:
        print(f"Error: {e}")


# ==================== EXPERIENCE YEARS ====================

@router.message(ApplicationState.experience_years, F.text)
async def process_experience_years(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.has_experience.ask"), reply_markup=Keyboards.yes_no(lang))
            await state.set_state(ApplicationState.has_experience)
            return
        
        is_valid, years = Validators.experience_years(message.text)
        if not is_valid:
            await message.answer(t(lang, "application.experience_years.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        app_id = await get_app_id(state)
        await DB.app.update(app_id, work_experience_length=years)
        await state.update_data(experience_years=years)
        await message.answer(t(lang, "application.last_workplace.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.last_workplace)
    except Exception as e:
        print(f"Error: {e}")


# ==================== LAST WORKPLACE ====================

@router.message(ApplicationState.last_workplace, F.text)
async def process_last_workplace(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.experience_years.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.experience_years)
            return
        
        is_valid, cleaned = Validators.text_field(message.text)
        if not is_valid:
            await message.answer(t(lang, "application.last_workplace.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        app_id = await get_app_id(state)
        await DB.app.update(app_id, last_workplace=cleaned)
        await message.answer(t(lang, "application.last_position.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.last_position)
    except Exception as e:
        print(f"Error: {e}")


# ==================== LAST POSITION ====================

@router.message(ApplicationState.last_position, F.text)
async def process_last_position(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.last_workplace.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.last_workplace)
            return
        
        is_valid, cleaned = Validators.text_field(message.text, 2, 100)
        if not is_valid:
            await message.answer(t(lang, "application.last_position.invalid"), reply_markup=Keyboards.back(lang))
            return
        
        app_id = await get_app_id(state)
        await DB.app.update(app_id, last_position=cleaned)
        await message.answer(t(lang, "application.photo.ask"), reply_markup=Keyboards.back(lang))
        await state.set_state(ApplicationState.photo)
    except Exception as e:
        print(f"Error: {e}")


# ==================== PHOTO ====================

@router.message(ApplicationState.photo, F.photo)
async def process_photo(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        photo = message.photo[-1]  # Best quality
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


# ==================== RESUME ====================

@router.message(ApplicationState.resume, F.document)
async def process_resume(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        # Check file type
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


# ==================== HOW FOUND ====================

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


# ==================== ADDITIONAL NOTES ====================

@router.message(ApplicationState.additional_notes, F.text)
async def process_additional_notes(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        
        if is_back(message.text):
            await message.answer(t(lang, "application.how_found.ask"), reply_markup=Keyboards.skip_back(lang))
            await state.set_state(ApplicationState.how_found)
            return
        
        app_id = await get_app_id(state)
        
        if not is_skip(message.text):
            await DB.app.update(app_id, additional_notes=message.text[:500])
        
        # Show confirmation
        await show_confirmation(message, state, user_lang)
    except Exception as e:
        print(f"Error: {e}")


# ==================== CONFIRMATION ====================

async def show_confirmation(message: Message, state: FSMContext, user_lang: str = "uz"):
    """Show application summary"""
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        data = await state.get_data()
        
        app = await DB.app.get(app_id)
        if not app:
            await message.answer(t(lang, "errors.general"))
            return
        
        # Build confirmation text
        gender_text = {"male": "👨", "female": "👩"}.get(app.gender.value if app.gender else "", "—")
        
        text = t(lang, "application.confirmation.header")
        text += t(lang, "application.confirmation.personal",
            first_name=app.first_name or "—",
            last_name=app.last_name or "—",
            birth_date=app.birth_date.strftime("%d.%m.%Y") if app.birth_date else "—",
            gender=gender_text
        )
        text += t(lang, "application.confirmation.contact",
            address=app.address or "—",
            phone=app.phone_number or "—",
            email=app.email or "—"
        )
        text += t(lang, "application.confirmation.education",
            is_student="✅" if app.is_student else "❌",
            education_place=app.education_place or "—",
            education_level=app.education_level.value if app.education_level else "—"
        )
        text += t(lang, "application.confirmation.languages",
            russian_level=app.russian_level.value if app.russian_level else "—",
            english_level=app.english_level.value if app.english_level else "—"
        )
        text += t(lang, "application.confirmation.experience",
            has_experience="✅" if app.has_work_experience else "❌",
            years=str(app.work_experience_length or "—"),
            workplace=app.last_workplace or "—",
            position=app.last_position or "—"
        )
        text += t(lang, "application.confirmation.additional",
            how_found=app.how_found_us or "—",
            notes=(app.additional_notes or "—")[:100]
        )
        text += t(lang, "application.confirmation.footer")
        
        await message.answer(text)
        
        # Send photo
        if app.photo_path and Path(app.photo_path).exists():
            try:
                await message.answer_photo(FSInputFile(app.photo_path), caption="📸")
            except:
                pass
        
        # Send voices
        if app.russian_voice_path and Path(app.russian_voice_path).exists():
            try:
                await message.answer_voice(FSInputFile(app.russian_voice_path), caption="🎤 RU")
            except:
                pass
        
        if app.english_voice_path and Path(app.english_voice_path).exists():
            try:
                await message.answer_voice(FSInputFile(app.english_voice_path), caption="🎤 EN")
            except:
                pass
        
        await message.answer(t(lang, "application.confirmation.ask"), reply_markup=Keyboards.confirmation(lang))
        await state.set_state(ApplicationState.confirmation)
    except Exception as e:
        print(f"Error in show_confirmation: {e}")


@router.message(ApplicationState.confirmation, F.text)
async def process_confirmation(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        if is_confirm(message.text):
            await DB.app.submit(app_id)
            await state.clear()
            await state.update_data(lang=lang)
            await message.answer(t(lang, "application.success"), reply_markup=Keyboards.main_menu(lang))
            await state.set_state(MenuState.main)
        
        elif is_refill(message.text):
            await DB.app.delete(app_id)
            app, _ = await DB.app.get_or_create_draft(message.from_user.id)
            await state.update_data(app_id=app.id, lang=lang)
            await message.answer(t(lang, "application.start"))
            await message.answer(t(lang, "application.first_name.ask"), reply_markup=Keyboards.back(lang))
            await state.set_state(ApplicationState.first_name)
        
        elif is_cancel(message.text):
            await DB.app.delete(app_id)
            await state.clear()
            await state.update_data(lang=lang)
            await message.answer(t(lang, "application.cancelled"), reply_markup=Keyboards.main_menu(lang))
            await state.set_state(MenuState.main)
        
        else:
            await message.answer(t(lang, "application.confirmation.ask"), reply_markup=Keyboards.confirmation(lang))
    except Exception as e:
        print(f"Error: {e}")