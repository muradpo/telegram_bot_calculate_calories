from aiogram import BaseMiddleware
from aiogram.types import Message


class ProfileRequiredMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        state = data.get("state")

        # если FSMContext нет — пропускаем
        if state is None:
            return await handler(event, data)

        # 🔥 ЕСЛИ ПОЛЬЗОВАТЕЛЬ В FSM — ПРОПУСКАЕМ
        current_state = await state.get_state()
        if current_state is not None:
            return await handler(event, data)

        user_data = await state.get_data()

        allowed_commands = (
            "/start",
            "/help",
            "/set_profile",
            "/cancel"
        )

        if event.text and event.text.startswith(allowed_commands):
            return await handler(event, data)

        if "calories_goal" not in user_data:
            await event.answer(
                "Сначала заполните профиль через /set_profile"
            )
            return

        return await handler(event, data)
