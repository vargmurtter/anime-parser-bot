from aiogram.types import (
    Message,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from app.models import Anime
from app import keyboards as kb


# рисует и отправляет юзеру карточку аниме
async def show_anime_info(message: Message, anime: Anime) -> None:
    info = (
        f"Название: {anime.title}\n"
        f"Тип: {anime.type}\n"
        f"Рейтинг: {anime.rating}\n"
        f"Эпизодов: {anime.episodes}\n"
        f"Стартовал: {anime.aired}\n"
        f"Завершен: {anime.ended}\n\n"
        f"<a href='https://anidb.net/anime/{anime.anime_id}'>Подробнее</a>"
    )

    anime_list = await anime.list_by_user(message.chat.id)

    await message.answer_photo(
        photo=anime.poster_url,
        caption=info,
        reply_markup=kb.anime_keyboard(anime_list),
        parse_mode="HTML",
    )


# упаковывает список аниме в формат понятный телеграму в инлайн-режиме
def anime_inline_article(anime: Anime) -> InlineQueryResultArticle:
    article = InlineQueryResultArticle(
        id=str(anime.id),
        title=anime.title,
        description=f"{anime.type} | Эпизодов: {anime.episodes}",
        thumb_url=anime.poster_thumb_url,
        input_message_content=InputTextMessageContent(
            message_text=f"/get_anime {anime.id}"
        ),
    )
    return article
