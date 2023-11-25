from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


def Depends(arg_name: str, arg_value: Any):
    class AddDependencyMiddleware(BaseMiddleware):
        name = arg_name

        def __init__(self, value: Any):
            super().__init__()
            self.value = value

        async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
        ) -> Any:
            data[self.name] = self.value
            return await handler(event, data)

    return AddDependencyMiddleware(arg_value)
