from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.reply import Keyboards
from bot.states.user import MenuState
from bot.validators.validator import get_selected_lang
from bot.states.user import MenuState
from services.language_service import t
from database.db import DB

router = Router(name="language_selection")


@router.message(MenuState.language_select, F.text)
async def language_selected(message: Message, state: FSMContext, db_user=None):
    try:
        selected_lang = get_selected_lang(message.text)
        
        if not selected_lang:
            await message.answer(
                t("uz", "welcome.first_time"),
                reply_markup=Keyboards.language_select()
            )
            return
        if db_user:
            await DB.user.set_language(db_user.id, selected_lang)
        
        await state.update_data(lang=selected_lang)
        
        await message.answer(
            t(selected_lang, "menu.language_changed"),
        )
        await message.answer(
            t(selected_lang, "menu.main"),
            reply_markup=Keyboards.main_menu(selected_lang)
        )
        await state.set_state(MenuState.main)
        await DB.user.set_state(message.from_user.id, MenuState.main.state)
    except Exception as e:
        print(f"Error in language_selected: {e}")
        await message.answer(t("uz", "errors.general"))