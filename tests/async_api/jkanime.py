import asyncio
from ani_scrapy.async_api import JKAnimeScraper, AsyncBrowser

query = "grand"
anime_id = "grand-blue-season-2"
episode_id = 7


async def main():
    async with AsyncBrowser(
        headless=True,
    ) as browser:
        scraper = JKAnimeScraper(verbose=True, level="DEBUG")
        search_results = await scraper.search_anime(query=query)
        print(search_results)

        anime_info = await scraper.get_anime_info(
            anime_id=anime_id, browser=browser
        )
        print(anime_info)

        table_links = await scraper.get_table_download_links(
            anime_id=anime_id, episode_id=episode_id, browser=browser
        )
        print(table_links)

        iframe_links = await scraper.get_iframe_download_links(
            anime_id=anime_id, episode_id=episode_id, browser=browser
        )
        print(iframe_links)

        try:
            file_links = await scraper.get_file_download_link(
                download_info=table_links.download_links[1], browser=browser
            )
            print(file_links)
        except Exception:
            print(None)

    anime_info = await scraper.get_anime_info(anime_id=anime_id)
    print(anime_info)

    table_links = await scraper.get_table_download_links(
        anime_id=anime_id, episode_id=episode_id
    )
    print(table_links)

    iframe_links = await scraper.get_iframe_download_links(
        anime_id=anime_id, episode_id=episode_id
    )
    print(iframe_links)

    try:
        file_links = await scraper.get_file_download_link(
            download_info=table_links.download_links[1]
        )
        print(file_links)
    except Exception:
        print(None)


if __name__ == "__main__":
    asyncio.run(main())
