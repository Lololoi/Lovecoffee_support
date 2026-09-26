import time
from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.last_call: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        if user_id is not None:
            now = time.monotonic()
            last = self.last_call.get(user_id, 0)
            
            if now - last < self.interval:
                return
            
            self.last_call[user_id] = now
            
        return await handler(event, data)