import asyncio
from datetime import datetime
from aiogram.client.session.aiohttp import AiohttpSession
from bs4 import BeautifulSoup, ResultSet, Tag
from tortoise import Tortoise
from app.models import Anime
import config
from loaders import aiosession


class EndOfDataException(Exception): ...


USER_AGENT = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.465 (Edition Yx GX)",
}


class AniDBParser:
    def __init__(self, session: AiohttpSession) -> None:
        self._session = session
        pass

    def _get_table_data_field(self, entry: Tag, key: str) -> str:
        """Возвращает значение из таблицы про аниме по ключу

        Args:
            entry (Tag): запись в таблице
            key (str): ключ
        """
        return entry.find("td", attrs={"data-label": key}).get_text().strip()

    async def get_page_data(self, page_number: int = 0) -> list[Anime]:
        """Вбирает все данные по аниме на указанной странице

        Args:
            page_number (int, optional): номер страницы, по умолчанию 0.

        Raises:
            EndOfDataException: вызывается, когда на странице не осталось аниме.

        Returns: list[Anime]
        """

        # получаем html страницу
        url = f"https://anidb.net/anime/?h=1&noalias=1&orderby.name=0.1&type.movie=1&type.tvseries=1&view=list&page={page_number}"
        session = await self._session.create_session()
        async with session.get(url, headers=USER_AGENT) as response:
            html_text = await response.text()
        await session.close()

        soup = BeautifulSoup(html_text, "html.parser")

        # если таблицы нет, значит и списка нет, выходим
        table = soup.find("table", class_="animelist")
        if table is None:
            raise EndOfDataException()

        # список представлен в виде таблицы, поэтому тут вычленяем строки из
        # этой таблицы и проходимся по ним, собирая все данные
        entries: ResultSet[Tag] = table.find("tbody").find_all("tr")
        result: list[Anime] = []
        for entry in entries:
            anime_id = int(entry.get("id").replace("a", ""))

            picture = entry.find("picture")

            anime_title = self._get_table_data_field(entry, "Title")

            # не у всех аниме есть постеры, поэтому делаем доп проверку
            try:
                anime_poster_thumb_url = picture.find("img").get("src")
                anime_poster_url = picture.find("source").get("srcset")
            except AttributeError:
                anime_poster_thumb_url = None
                anime_poster_url = None

            anime_type = self._get_table_data_field(entry, "Type")
            anime_rating = self._get_table_data_field(entry, "Rating")
            anime_episodes = self._get_table_data_field(entry, "Eps")
            anime_aired = self._get_table_data_field(entry, "Aired")
            anime_ended = self._get_table_data_field(entry, "Ended")

            # сразу пакуем все данные в модельку
            result.append(
                Anime(
                    anime_id=anime_id,
                    title=anime_title,
                    poster_url=anime_poster_url,
                    poster_thumb_url=anime_poster_thumb_url,
                    type=anime_type,
                    rating=anime_rating,
                    episodes=anime_episodes,
                    aired=anime_aired,
                    ended=anime_ended,
                    updated_date=datetime.now(),
                )
            )
        return result


async def main() -> None:
    await Tortoise.init(config=config.TORTOISE_SETTINGS)
    await Tortoise.generate_schemas()

    parser = AniDBParser(aiosession)
    page_counter = 0
    # бесконечно проходимся по всем страницам, пока не встретим исключение
    while True:
        print(f"PAGE {page_counter}")
        try:
            animes = await parser.get_page_data(page_counter)
        except EndOfDataException:
            break

        # добавляем аниме пачками
        await Anime.bulk_create(animes, ignore_conflicts=True)
        page_counter += 1


if __name__ == "__main__":
    asyncio.run(main())
