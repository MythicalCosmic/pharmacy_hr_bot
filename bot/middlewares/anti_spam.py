from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import re


class AntiSpamMiddleware(BaseMiddleware):
    SPAM_PATTERNS = [
        r'[@&₽)\$€£¥₹]{3,}', 
        r'[₽₴₸₹₺]{2,}',      
        r'[@#$%^&*]{5,}',     
    ]
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.text:
            for pattern in self.SPAM_PATTERNS:
                if re.search(pattern, event.text):
                    return  
        
        return await handler(event, data)