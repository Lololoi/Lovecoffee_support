from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" Назад до меню", callback_data="back_to_menu")]
    ])