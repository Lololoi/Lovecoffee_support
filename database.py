import aiosqlite
from config import DB_PATH

async def fetch_one(query: str, args: tuple = ()):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, args)
        return await cursor.fetchone()


async def execute_db(query: str, args: tuple = ()):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, args)
        await db.commit()
        return cursor.lastrowid

async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                lang TEXT DEFAULT 'uk',
                is_banned INTEGER DEFAULT 0
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                status TEXT DEFAULT 'open',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                closed_at DATETIME
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS relay_map (
                admin_msg_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                ticket_id INTEGER
            )
        """)
        await db.commit()

async def add_user_if_not_exists(user_id: int, username: str, full_name: str) -> None:
    await execute_db(
        "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
        (user_id, username, full_name)
    )


async def set_user_lang(user_id: int, lang: str) -> None:
    await execute_db("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))


async def get_user_lang(user_id: int) -> str:
    row = await fetch_one("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    return row[0] if row else "uk"


async def is_user_banned(user_id: int) -> bool:
    row = await fetch_one("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    return bool(row[0]) if row else False

async def create_ticket(user_id: int) -> int:
    return await execute_db("INSERT INTO tickets (user_id, status) VALUES (?, 'open')", (user_id,))


async def close_ticket(ticket_id: int) -> int | None:
    row = await fetch_one("SELECT user_id FROM tickets WHERE ticket_id = ?", (ticket_id,))
    if row:
        await execute_db(
            "UPDATE tickets SET status = 'closed', closed_at = datetime('now') WHERE ticket_id = ?",
            (ticket_id,)
        )
        return row[0]
    return None

async def save_relay(admin_msg_id: int, user_id: int, ticket_id: int) -> None:
    await execute_db(
        "INSERT INTO relay_map (admin_msg_id, user_id, ticket_id) VALUES (?, ?, ?)",
        (admin_msg_id, user_id, ticket_id)
    )

async def get_relay_by_admin_msg(admin_msg_id: int) -> dict | None:
    row = await fetch_one("SELECT user_id, ticket_id FROM relay_map WHERE admin_msg_id = ?", (admin_msg_id,))
    return {"user_id": row[0], "ticket_id": row[1]} if row else None