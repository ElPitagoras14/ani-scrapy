import asyncio
import time
from ani_scrapy.async_api import JKAnimeScraper, AsyncBrowser
from ani_scrapy.core.constants.jkanime import supported_servers

query = "grand"
anime_id = "steins-gate"
episode_number = 1


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
        print(len(anime_info.episodes))

        new_episodes = await scraper.get_new_episodes(
            anime_id="one-piece", last_episode_number=1100, browser=browser
        )
        print(new_episodes)

        table_links = await scraper.get_table_download_links(
            anime_id=anime_id, episode_number=episode_number, browser=browser
        )
        print(table_links)

        selected_link = None
        for link in table_links.download_links:
            if link.server in supported_servers:
                selected_link = link
                break

        iframe_links = await scraper.get_iframe_download_links(
            anime_id=anime_id, episode_number=episode_number, browser=browser
        )
        print(iframe_links)

        try:
            file_links = await scraper.get_file_download_link(
                download_info=selected_link, browser=browser
            )
            print(file_links)
        except Exception:
            pass

    anime_info = await scraper.get_anime_info(anime_id=anime_id)
    print(anime_info)

    new_episodes = await scraper.get_new_episodes(
        anime_id="one-piece", last_episode_number=1130
    )
    print(new_episodes)

    table_links = await scraper.get_table_download_links(
        anime_id=anime_id, episode_number=episode_number
    )
    print(table_links)

    iframe_links = await scraper.get_iframe_download_links(
        anime_id=anime_id, episode_number=episode_number
    )
    print(iframe_links)

    try:
        file_links = await scraper.get_file_download_link(
            download_info=table_links.download_links[1]
        )
        print(file_links)
    except Exception:
        pass


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    print(f"Time taken: {time.time() - start_time} seconds")
