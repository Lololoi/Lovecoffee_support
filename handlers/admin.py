from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import aiosqlite

from config import ADMIN_IDS, DB_PATH

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("stats"))
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
        (open_count,) = await cursor.fetchone()
        cursor = await db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
        (closed_count,) = await cursor.fetchone()
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        (users_count,) = await cursor.fetchone()

        await message.answer(
        f" Статистика підтримки\n\n"
        f"Відкритих тікетів: {open_count}\n"
        f"Закритих тікетів: {closed_count}\n"
        f"Усього користувачів: {users_count}"
        )

@router.message(Command("ban"))
async def ban_user(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.reply("Приклад: /ban <user_id>")
        return

    user_id = int(parts[1])

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
        await db.commit()

    await message.reply(f"Користувача {user_id} заблоковано для звернень у підтримку.")