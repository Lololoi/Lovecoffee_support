from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SITE_URL


def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            ]
        ]
    )


def main_menu_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    support_text = "Contact support" if lang == "en" else "Зв'язатися з технічною підтримкою"
    site_text = "Our site / Channel" if lang == "en" else "Наш сайт / Канал"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=support_text, callback_data="contact_support")],
            [InlineKeyboardButton(text=site_text, url=SITE_URL)],
        ]
    )


def cancel_kb(lang: str = "uk") -> InlineKeyboardMarkup:
    text = "❌ Cancel" if lang == "en" else "❌ Скасувати"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data="cancel_support")]
        ]
    )