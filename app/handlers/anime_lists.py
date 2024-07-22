from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram_widgets.pagination import KeyboardPaginator
from app.enums import ListType
from app.extras import helpers
from app.handlers import start
from app.models import User, List
from app.states import BotStates
from app import keyboards as kb
import config


router = Router()
router.message.filter(F.from_user.id != F.bot.id)
router.message.filter(F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


# показываем списки юзера
@router.callback_query(F.data == "lists", BotStates.main)
async def handle_lists_btn(callback: CallbackQuery, state: FSMContext) -> None:
    await helpers.try_delete_message(callback.message)
    await state.set_state(BotStates.lists)

    user = await User.get(tg_id=callback.message.chat.id)
    if user is None:
        return

    # тут просто считаем кол-во добавленных аниме в каждом списке
    watching_count = await List.filter(
        user_id=user.id, list=str(ListType.WATCHING)
    ).count()
    completed_count = await List.filter(
        user_id=user.id, list=str(ListType.COMPLETED)
    ).count()
    plan_count = await List.filter(
        user_id=user.id, list=str(ListType.PLAN_TO_WATCH)
    ).count()
    dropped_count = await List.filter(
        user_id=user.id, list=str(ListType.DROPPED)
    ).count()

    await callback.message.answer(
        f"👁️ Смотрю: {watching_count}\n"
        f"✅ Просмотренно: {completed_count}\n"
        f"🔖 В планах: {plan_count}\n"
        f"❌ Брошено: {dropped_count}\n\n"
        "Выберите интересующий вас список:",
        reply_markup=kb.lists_keyboard(),
    )


# показываем все аниме добавленные в выбранный список
@router.callback_query(F.data.startswith("lst:"), BotStates.lists)
async def handle_chosen_list(
    callback: CallbackQuery, state: FSMContext
) -> None:
    list_type = callback.data.split(":")[1]

    await helpers.try_delete_message(callback.message)
    await state.set_state(BotStates.chosen_list)

    user = await User.get(tg_id=callback.message.chat.id)
    if user is None:
        return

    chosen_list_animes = await List.filter(
        user_id=user.id, list=list_type
    ).all()
    animes = [
        await lsted_anime.get_anime() for lsted_anime in chosen_list_animes
    ]

    paginator = KeyboardPaginator(
        router=router,
        data=kb.anime_list_buttons(animes),
        per_page=10,
        per_row=2,
        additional_buttons=kb.return_button_row(),
    )

    await callback.message.answer(
        f"Ваши аниме из списка {config.LIST_TYPES[list_type]!r}",
        reply_markup=paginator.as_markup(),
    )


# обработка кнопок Назад
@router.callback_query(
    F.data == "return",
    StateFilter(
        BotStates.lists,
        BotStates.chosen_list,
    ),
)
async def handle_return_btn(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    match current_state:
        case BotStates.lists:
            await start.start_cmd(callback.message, state)
        case BotStates.chosen_list:
            await handle_lists_btn(callback, state)
