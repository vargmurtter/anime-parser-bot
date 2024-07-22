from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_widgets.types import ButtonType, AdditionalButtonsType
from app.enums import ListType
from app.models import Anime, List
import config


def return_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data="return",
    )


def return_button_row() -> AdditionalButtonsType:
    return [[return_button()]]


def return_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[return_button()]])


def main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Поиск", switch_inline_query_current_chat="")
    builder.button(text="📖 Мои списки", callback_data="lists")
    builder.button(text="🎲 Случайное аниме", callback_data="random")
    builder.adjust(2, 1)
    return builder.as_markup()


def anime_keyboard(anime_list: List | None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if anime_list:
        builder.button(
            text=f"🔖 Список: {anime_list.list_locale}", callback_data="add"
        )
    else:
        builder.button(text="➕ Добавить в список", callback_data="add")
    builder.button(text="⬅️ Назад", callback_data="return")
    builder.adjust(1)
    return builder.as_markup()


def choose_list_keyboard(
    current_list: str | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for list_type, text in config.LIST_TYPES.items():
        icon = "🔳" if current_list == list_type else "⬜️"
        builder.button(
            text=f"{icon} {text}", callback_data=f"add_lst:{list_type}"
        )

    if current_list:
        builder.button(text="🗑 Удалить из списка", callback_data="remove_lst")

    builder.button(text="⬅️ Назад", callback_data="return")
    builder.adjust(2, 2, 1)

    return builder.as_markup()


def remove_anime_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Удалить", callback_data="remove")
    builder.button(text="⬅️ Назад", callback_data="return")
    builder.adjust(2)
    return builder.as_markup()


def anime_list_buttons(
    animes: list[Anime], callback_name: str = "get_anime"
) -> list[ButtonType]:
    buttons: list[ButtonType] = [
        InlineKeyboardButton(
            text=anime.title, callback_data=f"{callback_name}:{anime.id}"
        )
        for anime in animes
    ]
    return buttons


def lists_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👁️ Смотрю", callback_data=f"lst:{ListType.WATCHING}")
    builder.button(
        text="✅ Просмотренно", callback_data=f"lst:{ListType.COMPLETED}"
    )
    builder.button(
        text="🔖 В планах", callback_data=f"lst:{ListType.PLAN_TO_WATCH}"
    )
    builder.button(text="❌ Брошено", callback_data=f"lst:{ListType.DROPPED}")
    builder.add(return_button())
    builder.adjust(2, 2, 1)
    return builder.as_markup()
