from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from config import SUPPORT_CHAT_ID
from database import (
    get_user_lang,
    create_ticket,
    save_relay,
    get_relay_by_admin_msg,
    close_ticket,
)
from keyboards.main_menu import cancel_kb

router = Router()


class SupportForm(StatesGroup):
    waiting_for_ticket_message = State()

@router.callback_query(F.data == "contact_support")
async def start_support(call: CallbackQuery, state: FSMContext):
    lang = await get_user_lang(call.from_user.id)
    await state.set_state(SupportForm.waiting_for_ticket_message)

    text = (
        "Напишіть ваше запитання або опишіть проблему одним повідомленням:"
        if lang == "uk"
        else "Please send your question or describe your issue in one message:"
    )
    await call.message.edit_text(text, reply_markup=cancel_kb(lang))
    await call.answer()

@router.callback_query(F.data == "cancel_support")
async def cancel_support(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(call.from_user.id)
    text = (
        "Звернення скасовано."
        if lang == "uk"
        else "Support request cancelled."
    )
    await call.message.edit_text(text)
    await call.answer()

@router.message(SupportForm.waiting_for_ticket_message)
async def process_ticket_message(message: Message, state: FSMContext, bot: Bot):
    lang = await get_user_lang(message.from_user.id)

    ticket_id = await create_ticket(message.from_user.id)

    header = (
        f"<b>Новий тікет #{ticket_id}</b>\n"
        f"Користувач: {message.from_user.full_name} (@{message.from_user.username or 'немає'})\n"
        f"ID: <code>{message.from_user.id}</code>\n"
        f"----------------------------------------"
    )

    await bot.send_message(chat_id=SUPPORT_CHAT_ID, text=header)

    relayed_msg = await message.copy_to(chat_id=SUPPORT_CHAT_ID)

    await save_relay(
        admin_msg_id=relayed_msg.message_id,
        user_id=message.from_user.id,
        ticket_id=ticket_id,
    )

    await state.clear()

    confirm_text = (
        f"<b>Ваше звернення #{ticket_id} прийнято!</b>\n"
        "Очікуйте на відповідь оператора."
        if lang == "uk"
        else f"<b>Your ticket #{ticket_id} has been submitted!</b>\n"
        "Please wait for an operator to respond."
    )
    await message.answer(confirm_text)

@router.message(F.chat.id == SUPPORT_CHAT_ID, F.reply_to_message)
async def handle_operator_reply(message: Message, bot: Bot):
    reply_msg_id = message.reply_to_message.message_id
    relay = await get_relay_by_admin_msg(reply_msg_id)
    if not relay:
        return  

    user_id = relay["user_id"]
    ticket_id = relay["ticket_id"]

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"<b>Відповідь по тікету #{ticket_id}:</b>",
        )
        await message.copy_to(chat_id=user_id)
    except Exception as e:
        await message.reply(f"Не вдалося надіслати відповідь користувачу: {e}")

@router.message(F.chat.id == SUPPORT_CHAT_ID, F.text.startswith("/close"))
async def handle_close_ticket(message: Message, bot: Bot):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.reply("Використання: <code>/close TICKET_ID</code> (наприклад: <code>/close 1</code>)")
        return

    ticket_id = int(args[1])
    user_id = await close_ticket(ticket_id)

    if user_id:
        await message.reply(f"Тікет #{ticket_id} успішно закрито.")
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"<b>Ваш тікет #{ticket_id} було закрито оператором.</b>",
            )
        except Exception:
            pass
    else:
        await message.reply(f"Тікет #{ticket_id} не знайдено або він вже закритий.")