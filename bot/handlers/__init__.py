"""
Handler registration
"""
from aiogram import Dispatcher
from bot.handlers import commands, messages, callbacks
from bot.handlers.main import language_selection, menu_handler, settings_handler, personal_info_handler

def register_handlers(dp: Dispatcher):
    """Register all handlers"""
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    dp.include_router(language_selection.router)
    dp.include_router(menu_handler.router)
    dp.include_router(settings_handler.router)
    dp.include_router(personal_info_handler.router)
    dp.include_router(callbacks.router)
