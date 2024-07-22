from strenum import StrEnum


class ListType(StrEnum):
    WATCHING = "watching"
    PLAN_TO_WATCH = "plan_to_watch"
    COMPLETED = "completed"
    DROPPED = "dropped"
