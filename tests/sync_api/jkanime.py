from ani_scrapy.sync_api import JKAnimeScraper, SyncBrowser
from ani_scrapy.core.constants.jkanime import supported_servers


query = "grand"
anime_id = "grand-blue-season-2"
episode_number = 10


with SyncBrowser(
    headless=True,
) as browser:
    scraper = JKAnimeScraper(verbose=True, level="DEBUG")

    search_results = scraper.search_anime(query=query)
    print(search_results)

    anime_info = scraper.get_anime_info(
        anime_id=anime_id, include_episodes=False, browser=browser
    )
    print(anime_info)

    new_episodes = scraper.get_new_episodes(
        anime_id="one-piece", last_episode_number=1130, browser=browser
    )
    print(new_episodes)

    table_links = scraper.get_table_download_links(
        anime_id=anime_id, episode_number=episode_number, browser=browser
    )
    print(table_links)

    selected_link = None
    for link in table_links.download_links:
        if link.server in supported_servers:
            selected_link = link
            break

    iframe_links = scraper.get_iframe_download_links(
        anime_id=anime_id, episode_number=episode_number, browser=browser
    )
    print(iframe_links)

    try:
        file_links = scraper.get_file_download_link(
            download_info=selected_link, browser=browser
        )
        print(file_links)
    except Exception:
        pass

anime_info = scraper.get_anime_info(anime_id=anime_id)
print(anime_info)

new_episodes = scraper.get_new_episodes(
    anime_id=anime_id,
    last_episode_number=10,
)
print(new_episodes)

table_links = scraper.get_table_download_links(
    anime_id=anime_id, episode_number=episode_number
)
print(table_links)

iframe_links = scraper.get_iframe_download_links(
    anime_id=anime_id, episode_number=episode_number
)
print(iframe_links)

try:
    file_links = scraper.get_file_download_link(
        download_info=table_links.download_links[1]
    )
    print(file_links)
except Exception:
    pass
