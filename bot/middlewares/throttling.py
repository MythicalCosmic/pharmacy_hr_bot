"""
🚀 Throttling Middleware for Aiogram 3.x
Using limitless-py style: @ratelimit(calls=3, per=2)

pip install limitless-py
"""
from typing import Callable, Dict, Any, Awaitable, Optional
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from collections import defaultdict
import time


class ThrottlingMiddleware(BaseMiddleware):
    """
    Rate limiting middleware (limitless-py style)

    Same logic as: @ratelimit(calls=3, per=2)

    Usage:
        # 1 message per 0.5 seconds per user
        dp.message.middleware(ThrottlingMiddleware(calls=1, per=0.5))

        # 3 messages per 2 seconds with warning
        dp.message.middleware(ThrottlingMiddleware(
            calls=3,
            per=2,
            warning_message="⏳ Iltimos, sekinroq yozing!"
        ))
    """

    __slots__ = ("calls", "per", "warning_message", "silent", "_user_calls")

    def __init__(
        self,
        calls: int = 1,
        per: float = 0.5,
        warning_message: Optional[str] = None,
        silent: bool = False
    ):
        """
        Args:
            calls: Number of allowed calls within the time period
            per: Time period in seconds
            warning_message: Message to send when rate limited
            silent: If True, silently drop spam without warning
        """
        self.calls = calls
        self.per = per
        self.warning_message = warning_message
        self.silent = silent
        self._user_calls: Dict[int, list] = defaultdict(list)

    def _is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed (limitless-py logic)"""
        now = time.time()
        timestamps = self._user_calls[user_id]

        window_start = now - self.per
        timestamps[:] = [ts for ts in timestamps if ts > window_start]

        if len(timestamps) < self.calls:
            timestamps.append(now)
            return True

        return False

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = getattr(event, "from_user", None)
        if not user or user.is_bot:
            return await handler(event, data)

        if not self._is_allowed(user.id):
            # Rate limited
            if not self.silent and self.warning_message:
                if isinstance(event, Message):
                    try:
                        await event.answer(self.warning_message)
                    except Exception:
                        pass
                elif isinstance(event, CallbackQuery):
                    try:
                        await event.answer(self.warning_message, show_alert=True)
                    except Exception:
                        pass
            return None

        return await handler(event, data)

