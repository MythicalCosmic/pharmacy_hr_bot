from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from database.db import DB


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user and not user.is_bot:
            db_user, created = await DB.user.get_or_create(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )
            if not created:
                if (db_user.first_name != user.first_name or
                    db_user.last_name != user.last_name or
                    db_user.username != user.username):
                    await DB.user.sync_telegram(
                        user_id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        username=user.username
                    )

            data["db_user"] = db_user
            data["is_new_user"] = created

        return await handler(event, data)