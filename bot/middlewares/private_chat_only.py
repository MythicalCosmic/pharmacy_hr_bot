from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.enums import ChatType


class PrivateChatOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.type != ChatType.PRIVATE:
            print(f"[PrivateChatOnly] Blocked {event.chat.type} chat: {event.chat.id}")
            try:
                await event.answer("❌ This bot only works in private chats.")
                await event.bot.leave_chat(event.chat.id)
            except:
                pass
            
            return 
        return await handler(event, data)