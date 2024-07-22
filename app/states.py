from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    main = State()
    search = State()
    lists = State()
    chosen_list = State()

    class AnimeInfo(StatesGroup):
        main = State()
        choose_list = State()
        remove_list = State()
