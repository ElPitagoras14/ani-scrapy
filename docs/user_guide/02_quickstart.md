# Quickstart

## Basic Example

```python
import asyncio

from ani_scrapy import AnimeFLVScraper


async def main() -> None:
    async with AnimeFLVScraper() as scraper:
        results = await scraper.search_anime(query="naruto", page=1)
        anime_id = results.animes[0].id

        info = await scraper.get_anime_info(anime_id=anime_id)
        print(info.title)


if __name__ == "__main__":
    asyncio.run(main())
```
