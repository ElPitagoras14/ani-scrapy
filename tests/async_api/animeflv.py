import asyncio
from ani_scrapy.async_api import AnimeFLVScraper, AsyncBrowser


query = "grand"
anime_id = "one-punch-man-3"
episode_number = 1


async def main():
    async with AsyncBrowser(
        headless=True,
    ) as browser:
        scraper = AnimeFLVScraper(verbose=True, level="DEBUG")
        search_results = await scraper.search_anime(query=query, page=1)
        print(search_results)

        anime_info = await scraper.get_anime_info(anime_id=anime_id)
        print(anime_info)

        new_episodes = await scraper.get_new_episodes(
            anime_id="one-piece-tv", last_episode_number=1130
        )
        print(new_episodes)

        table_links = await scraper.get_table_download_links(
            anime_id=anime_id, episode_number=episode_number
        )
        print(table_links)

        iframe_links = await scraper.get_iframe_download_links(
            anime_id=anime_id, episode_number=episode_number, browser=browser
        )
        print(iframe_links)

        try:
            file_links = await scraper.get_file_download_link(
                download_info=iframe_links.download_links[0], browser=browser
            )
            print(file_links)
        except Exception:
            pass

    iframe_links = await scraper.get_iframe_download_links(
        anime_id=anime_id, episode_number=episode_number
    )
    print(iframe_links)

    try:
        file_links = await scraper.get_file_download_link(
            download_info=iframe_links.download_links[0]
        )
        print(file_links)
    except Exception:
        pass


if __name__ == "__main__":
    asyncio.run(main())
