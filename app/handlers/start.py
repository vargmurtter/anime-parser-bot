from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from app.extras import helpers
from app.models import User, Anime
from app.states import BotStates
from app.handlers import anime_info
from app import keyboards as kb


router = Router()
router.message.filter(F.from_user.id != F.bot.id)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


# /start
@router.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext) -> None:
    await helpers.try_delete_message(message)

    # создает юзера в бд если такого еще нет
    tg_id = message.chat.id
    user = await User.filter(tg_id=tg_id).first()
    if user is None:
        user = User(tg_id=tg_id)
        await user.save()

    # устанавливаем состояние
    await state.set_state(BotStates.main)

    await message.answer(
        f"Добро пожаловать AniListBot! Тут вы сможете вести списки по аниме.",
        reply_markup=kb.main_keyboard(),
    )


# обработка нажатия на кнопку Случайное аниме
@router.callback_query(F.data == "random", BotStates.main)
async def handle_random_btn(callback: CallbackQuery, state: FSMContext) -> None:
    await anime_info.show_anime_info(callback.message, state, None)


# универсальный колбэк для просмотра карточки аниме по id
@router.callback_query(
    F.data.startswith("get_anime"),
    StateFilter(BotStates.search, BotStates.chosen_list),
)
async def handle_anime_btn(callback: CallbackQuery, state: FSMContext) -> None:
    anime_id = int(callback.data.split(":")[1])
    await anime_info.show_anime_info(callback.message, state, anime_id)


# /latest
@router.message(Command('latest'))
async def latest_cmd(message: Message, state: FSMContext) -> None:
    await helpers.try_delete_message(message)

    last_added_anime = await Anime.all().order_by('-id').first()
    print(last_added_anime.id)
    await anime_info.show_anime_info(message, state, last_added_anime.id)
    