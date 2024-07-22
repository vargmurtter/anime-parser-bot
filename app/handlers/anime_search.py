from aiogram import Router, F
from aiogram.types import Message, InlineQuery
from aiogram.filters import Command, CommandObject
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram_widgets.pagination import KeyboardPaginator
from app.handlers import anime_info
from app.models import Anime
from app.states import BotStates
from app import keyboards as kb, utils


router = Router()
router.message.filter(F.from_user.id != F.bot.id)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


# обработка inline-запроса
@router.inline_query(F.chat_type == ChatType.SENDER, BotStates.main)
async def handle_search_inline_query(inline_query: InlineQuery) -> None:
    anime_title_query = inline_query.query
    
    # запоминаем сдвиг, чтобы подгружать данные по мере скролла
    query_offset = int(inline_query.offset) if inline_query.offset else 0

    animes = await Anime.search_by_title(
        title_pattern=anime_title_query, start_num=query_offset
    )
    
    # тут просто данные из бд упаковываются в понятную для ТГ структуру
    articles = [utils.anime_inline_article(anime) for anime in animes]

    # если данных много, то говорим ТГ какой будет следующий сдвиг
    # и отправляем ответ
    if len(articles) < 50:
        await inline_query.answer(
            articles, cache_time=60 * 5, is_personal=True, next_offset=""
        )
    else:
        await inline_query.answer(
            articles,
            cache_time=60 * 5,
            is_personal=True,
            next_offset=str(query_offset + 50),
        )


# если юзер кликает по аниме в inline-режиме, то от имени юзера отправляется 
# команда /get_anime <ID>, чтобы получить картоку аниме, а тут эта команда
# отлавливается
@router.message(Command("get_anime"), BotStates.main)
async def handle_get_anime_cmd(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    try:
        anime_id = int(command.args)
    except ValueError:
        await message.answer("Неизвестная ошибка")
        return
    await anime_info.show_anime_info(message, state, anime_id)


# также реализована команда /search для поиска вручную, потому что того 
# требовало ТЗ
@router.message(Command("search"))
async def handle_search_cmd(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    await state.set_state(BotStates.search)

    query = command.args
    if not query:
        await message.answer(
            "Вы не ввели запрос. Пример запроса:\n\n<pre>/search naruto</pre>",
            parse_mode="HTML",
        )
        return
    
    animes = await Anime.search_by_title(query)

    # для пагинации воспользовался либой aiogram_widgets
    paginator = KeyboardPaginator(
        router=router,
        data=kb.anime_list_buttons(animes),
        per_page=10,
        per_row=2,
    )

    await message.answer(
        f"По вашему запросу найдено {len(animes)} аниме.",
        reply_markup=paginator.as_markup(),
    )
