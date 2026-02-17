"""
Helper functions
"""
from aiogram.fsm.context import FSMContext

def format_user_mention(user_id: int, name: str) -> str:
    """Format user mention for HTML"""
    return f'<a href="tg://user?id={user_id}">{name}</a>'

async def get_lang(state: FSMContext, user_lang: str = "uz") -> str:
    """Get language - priority: state > user_lang > default"""
    data = await state.get_data()
    return data.get("lang") or user_lang or "uz"


async def get_app_id(state: FSMContext) -> int:
    data = await state.get_data()
    return data.get("app_id")