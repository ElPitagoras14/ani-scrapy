from ani_scrapy.sync_api import JKAnimeScraper, SyncBrowser

brave_path = (
    "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
)

query = "grand"
anime_id = "grand-blue-season-2"
episode_id = 7


with SyncBrowser(
    headless=True,
    # executable_path=brave_path,
) as browser:
    scraper = JKAnimeScraper(verbose=True, level="DEBUG")
    search_results = scraper.search_anime(query=query)
    print(search_results)

    anime_info = scraper.get_anime_info(anime_id=anime_id, browser=browser)
    print(anime_info)

    table_links = scraper.get_table_download_links(
        anime_id=anime_id, episode_id=episode_id, browser=browser
    )
    print(table_links)

    iframe_links = scraper.get_iframe_download_links(
        anime_id=anime_id, episode_id=episode_id, browser=browser
    )
    print(iframe_links)

    try:
        file_links = scraper.get_file_download_link(
            download_info=table_links.download_links[1], browser=browser
        )
        print(file_links)
    except Exception:
        pass

anime_info = scraper.get_anime_info(anime_id=anime_id)
print(anime_info)

table_links = scraper.get_table_download_links(
    anime_id=anime_id, episode_id=episode_id
)
print(table_links)

iframe_links = scraper.get_iframe_download_links(
    anime_id=anime_id, episode_id=episode_id
)
print(iframe_links)

try:
    file_links = scraper.get_file_download_link(
        download_info=table_links.download_links[1]
    )
    print(file_links)
except Exception:
    pass
