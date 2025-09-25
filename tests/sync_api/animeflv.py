from ani_scrapy.sync_api import AnimeFlvScraper, SyncBrowser

query = "grand"
anime_id = "grand-blue-season-2"
episode_id = 7


with SyncBrowser(
    headless=False,
) as browser:
    scraper = AnimeFlvScraper(verbose=True, level="DEBUG")
    search_results = scraper.search_anime(query=query, page=1)
    print(search_results)

    anime_info = scraper.get_anime_info(anime_id=anime_id)
    print(anime_info)

    new_episodes = scraper.get_new_episodes(
        anime_id=anime_id, last_episode_number=8
    )
    print(new_episodes)

    table_links = scraper.get_table_download_links(
        anime_id=anime_id, episode_id=episode_id
    )
    print(table_links)

    iframe_links = scraper.get_iframe_download_links(
        anime_id=anime_id, episode_id=episode_id, browser=browser
    )
    print(iframe_links)

    try:
        file_links = scraper.get_file_download_link(
            download_info=iframe_links.download_links[0], browser=browser
        )
        print(file_links)
    except Exception:
        pass


iframe_links = scraper.get_iframe_download_links(
    anime_id=anime_id, episode_id=episode_id
)
print(iframe_links)

try:
    file_links = scraper.get_file_download_link(
        download_info=iframe_links.download_links[0]
    )
    print(file_links)
except Exception:
    pass
