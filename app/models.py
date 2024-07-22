from __future__ import annotations
from tortoise.models import Model
from tortoise.fields import (
    IntField,
    BigIntField,
    TextField,
)

from app.enums import ListType


class User(Model):
    id = IntField(primary_key=True)
    tg_id = BigIntField(unique=True, null=False)

    class Meta:
        table = "users"


class Anime(Model):
    id = IntField(primary_key=True)
    anime_id = BigIntField(unique=True)
    title = TextField()
    poster_url = TextField(null=True)
    poster_thumb_url = TextField(null=True)
    type = TextField()
    rating = TextField()
    episodes = TextField()
    aired = TextField()
    ended = TextField()

    @staticmethod
    async def search_by_title(
        title_pattern: str = "", start_num: int = 0, limit_size: int = 50
    ) -> list[Anime]:
        """Проводит поиск по названию аниме"""
        if title_pattern:
            animes = await Anime.filter(title__icontains=title_pattern).all()
        else:
            animes = await Anime.all()
        return animes[start_num : start_num + limit_size]

    async def list_by_user(self, user_tg_id: int) -> List | None:
        """Возвращает связь аниме со списком. Просто удобная сокращалка."""
        user = await User.get(tg_id=user_tg_id)
        if user is None:
            return None
        return await List.filter(user_id=user.id, anime_id=self.id).first()

    class Meta:
        table = "anime"


class List(Model):
    id = IntField(primary_key=True)
    list = TextField()
    user_id = IntField()
    anime_id = IntField()

    async def get_user(self) -> User:
        user = await User.get(id=self.user_id)
        if user is None:
            raise Exception("User not found")
        return user

    async def get_anime(self) -> Anime:
        anime = await Anime.get(id=self.anime_id)
        if anime is None:
            raise Exception("Anime not found")
        return anime

    @property
    def list_locale(self) -> str:
        """Устал каждый раз делать словарь для локализации енумов, поэтому вот"""
        return {
            ListType.WATCHING: "Смотрю",
            ListType.PLAN_TO_WATCH: "В планах",
            ListType.COMPLETED: "Просмотрено",
            ListType.DROPPED: "Брошено",
        }[self.list]

    class Meta:
        table = "lists"
