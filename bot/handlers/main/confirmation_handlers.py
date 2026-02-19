from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import ApplicationState, MenuState
from services.language_service import t
from database.db import DB
from bot.validators.validator import is_back, is_skip, is_confirm, is_refill, is_cancel
from utils.helpers import get_app_id, get_lang

router = Router(name="confirmation_handlers")

ADMIN_IDS = [6589960007]  


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
        
        await show_confirmation(message, state, user_lang)
    except Exception as e:
        print(f"Error: {e}")


async def show_confirmation(message: Message, state: FSMContext, user_lang: str = "uz"):
    def _val(field):
        return field.value if hasattr(field, "value") else (field or "—")

    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        data = await state.get_data()
        
        app = await DB.app.get(app_id)
        if not app:
            await message.answer(t(lang, "errors.general"))
            return
        
        gender_text = {"male": "👨", "female": "👩"}.get(_val(app.gender), "—")
        
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
            education_level=_val(app.education_level)
        )
        text += t(lang, "application.confirmation.languages",
            russian_level=_val(app.russian_level),
            english_level=_val(app.english_level)
        )
        text += t(lang, "application.confirmation.experience",
            has_experience="✅" if app.has_work_experience else "❌",
            years=str(app.work_experience_lenght or "—"),
            workplace=app.last_workplace or "—",
            position=app.last_position or "—"
        )
        text += t(lang, "application.confirmation.additional",
            how_found=app.how_found_us or "—",
            notes=(app.additional_notes or "—")[:100]
        )
        text += t(lang, "application.confirmation.footer")
        
        await message.answer(text)
        
        if app.photo_path and Path(app.photo_path).exists():
            try:
                await message.answer_photo(FSInputFile(app.photo_path), caption="📸")
            except:
                pass
        
        await message.answer(t(lang, "application.confirmation.ask"), reply_markup=Keyboards.confirmation(lang))
        await state.set_state(ApplicationState.confirmation)
    except Exception as e:
        print(f"Error in show_confirmation: {e}")


async def send_to_admins(message: Message, app):
    def _val(field):
        return field.value if hasattr(field, "value") else (field or "—")
    
    gender_text = {"male": "👨 Male", "female": "👩 Female"}.get(_val(app.gender), "—")
    
    caption = f"""
🆕 NEW APPLICATION #{app.id}

👤 Shaxsiy malumot:
- To'liq ismi: {app.first_name} {app.last_name}
- Tug'ilgan kuni: {app.birth_date.strftime("%d.%m.%Y") if app.birth_date else "—"}
- Gender: {gender_text}

📞 Bog'lanish:
- Address: {app.address or "—"}
- Telefon: {app.phone_number or "—"}
- Email: {app.email or "—"}

🎓 O'qishi:
- Student: {"✅ Yes" if app.is_student else "❌ No"}
- Insitut: {app.education_place or "—"}
- Daraja: {_val(app.education_level)}

💼 Ish Tarixi:
- Oldin ishlaganmi: {"✅ Yes" if app.has_work_experience else "❌ No"}
- Qancha ishlagan yili: {app.work_experience_lenght or "—"}
- Ohirgi ish joyi: {app.last_workplace or "—"}
- Pozitsiyasi: {app.last_position or "—"}

📝 Qo'shhimcha malumotlar:
- Qanday topgan: {app.how_found_us or "—"}
- Notelar: {app.additional_notes or "—"}
""".strip()
    
    user_info = f"""
━━━━━━━━━━━━━━━━━━━━━
👤 TELEGRAM INFO:
- User ID: {message.from_user.id}
- Username: @{message.from_user.username or "—"}
- First Name: {message.from_user.first_name or "—"}
- Last Name: {message.from_user.last_name or "—"}
- Language: {message.from_user.language_code or "—"}
""".strip()
    
    for admin_id in ADMIN_IDS:
        try:
            if app.photo_path and Path(app.photo_path).exists():
                await message.bot.send_photo(
                    chat_id=admin_id,
                    photo=FSInputFile(app.photo_path),
                    caption=caption
                )
            else:
                await message.bot.send_message(admin_id, caption)
            
            await message.bot.send_message(admin_id, user_info)
            
            if app.resume_path and Path(app.resume_path).exists():
                await message.bot.send_document(
                    chat_id=admin_id,
                    document=FSInputFile(app.resume_path),
                    caption="📄 Resume"
                )
            
            
        except Exception as e:
            print(f"Failed to send to admin {admin_id}: {e}")


@router.message(ApplicationState.confirmation, F.text)
async def process_confirmation(message: Message, state: FSMContext, user_lang: str = "uz"):
    try:
        lang = await get_lang(state, user_lang)
        app_id = await get_app_id(state)
        
        if is_confirm(message.text):
            app = await DB.app.get(app_id)
            await DB.app.submit(app_id)
            
            await send_to_admins(message, app)
            
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