from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from tortoise.contrib.postgres.functions import Random
from app.extras import helpers
from app.handlers import start
from app.models import Anime, User, List
from app.states import BotStates
from app import keyboards as kb, utils


router = Router()
router.message.filter(F.from_user.id != F.bot.id)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


# функция для генерации карточки аниме
async def show_anime_info(
    message: Message,
    state: FSMContext,
    anime_id: int | None = None,
) -> None:
    await helpers.try_delete_message(message)
    await state.set_state(BotStates.AnimeInfo.main)

    if anime_id is None:
        anime = await Anime.annotate(order=Random()).order_by("order").first()
    else:
        anime = await Anime.get(id=anime_id)

    if anime is None:
        await message.answer(
            "Аниме не найдено :с", reply_markup=kb.return_keyboard()
        )
        return

    await state.update_data(anime_id=anime.id)  # таким образом мы сохраняем данные в редис
    await utils.show_anime_info(message, anime)


# обработчик кнопки Добавить в список
@router.callback_query(F.data == "add", BotStates.AnimeInfo.main)
async def handle_add_lst_btn(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await helpers.try_delete_message(callback.message)
    await state.set_state(BotStates.AnimeInfo.choose_list)
    
    data_storage = await state.get_data()  # таким образом мы получаем данные из редиса
    if (anime_id := data_storage.get("anime_id")) is None:
        return
    anime = await Anime.get(id=anime_id)
    if anime is None:
        return

    anime_list = await anime.list_by_user(callback.message.chat.id)

    # показываем юзеру списки, в которые можно сохранить аниме
    await callback.message.answer(
        f"В какой список добавить аниме {anime.title!r}?",
        reply_markup=kb.choose_list_keyboard(
            anime_list.list if anime_list else None
        ),
    )


# сохраняем аниме в выбранный список
@router.callback_query(
    F.data.startswith("add_lst:"), BotStates.AnimeInfo.choose_list
)
async def handle_choosen_lst(
    callback: CallbackQuery, state: FSMContext
) -> None:
    list_type = callback.data.split(":")[1]
    data_storage = await state.get_data()
    if (anime_id := data_storage.get("anime_id")) is None:
        return
    anime = await Anime.get(id=anime_id)
    if anime is None:
        return
    user = await User.get(tg_id=callback.message.chat.id)
    if user is None:
        return

    current_list = await List.filter(user_id=user.id, anime_id=anime.id).first()
    if current_list is None:
        current_list = List(user_id=user.id, anime_id=anime.id)

    current_list.list = list_type
    await current_list.save()
    await callback.answer("✅ Сохранено!")
    await show_anime_info(callback.message, state, anime.id)


# получаем подтверждение об удалении из списка
@router.callback_query(F.data == "remove_lst", BotStates.AnimeInfo.choose_list)
async def handle_remove_lst_btn(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await helpers.try_delete_message(callback.message)
    await state.set_state(BotStates.AnimeInfo.remove_list)
    data_storage = await state.get_data()
    if (anime_id := data_storage.get("anime_id")) is None:
        return
    anime = await Anime.get(id=anime_id)
    if anime is None:
        return

    await callback.message.answer(
        f"Вы точно хотите удалить аниме {anime.title!r} из списка?",
        reply_markup=kb.remove_anime_keyboard(),
    )


# удаляем аниме из списка
@router.callback_query(F.data == "remove", BotStates.AnimeInfo.remove_list)
async def handle_remove_btn(callback: CallbackQuery, state: FSMContext) -> None:
    await helpers.try_delete_message(callback.message)
    await state.set_state(BotStates.AnimeInfo.remove_list)
    data_storage = await state.get_data()
    if (anime_id := data_storage.get("anime_id")) is None:
        return
    anime = await Anime.get(id=anime_id)
    if anime is None:
        return

    anime_list = await anime.list_by_user(callback.message.chat.id)
    if anime_list:
        await anime_list.delete()
    await callback.answer("Аниме удалено из списка")
    await show_anime_info(callback.message, state, anime.id)


@router.callback_query(
    F.data == "return",
    StateFilter(
        BotStates.AnimeInfo.main,
        BotStates.AnimeInfo.choose_list,
        BotStates.AnimeInfo.remove_list,
    ),
)
async def handle_return_btn(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    match current_state:
        case BotStates.AnimeInfo.main:
            await start.start_cmd(callback.message, state)
        case BotStates.AnimeInfo.choose_list | BotStates.AnimeInfo.remove_list:
            # чтобы вернуться назад к карточке, нужно вспомнить к какой именно 
            # карточке нужно вернуться
            data_storage = await state.get_data()
            if (anime_id := data_storage.get("anime_id")) is None:
                await start.start_cmd(callback.message, state)
                return
            await show_anime_info(callback.message, state, anime_id)
