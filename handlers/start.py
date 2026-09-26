from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.main_menu import language_kb, main_menu_kb
from database import add_user_if_not_exists, set_user_lang, get_user_lang

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await add_user_if_not_exists(
        user_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "👋 Вітаємо! Будь ласка, оберіть мову для продовження:\n"
        "👋 Welcome! Please choose a language to proceed:",
        reply_markup=language_kb(),
    )


@router.callback_query(F.data.startswith("lang_"))
async def choose_language(call: CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]
    await set_user_lang(call.from_user.id, lang)
    await call.answer()
    await show_main_menu(call, lang)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = await get_user_lang(call.from_user.id)
    await show_main_menu(call, lang)


async def show_main_menu(call: CallbackQuery, lang: str):
    text = (
        "Головне меню\n\n"
        "Вітаємо у службі підтримки сайту LoveCoffee."
        if lang == "uk" else
        "Main menu\n\n"
        "Welcome to LoveCoffee support service."
    )
    await call.message.edit_text(text, reply_markup=main_menu_kb(lang))
    await call.answer()