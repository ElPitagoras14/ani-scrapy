from anime_scraper.scrapers.jkanime.scraper import JKAnimeScraper
from anime_scraper.scrapers.animeflv import AnimeFLVScraper

animeflv_scraper = AnimeFLVScraper(verbose=False)
jkanime_scraper = JKAnimeScraper(verbose=False)

# Search anime
an_results = animeflv_scraper.search_anime(query="mushoku", page=1)
print(an_results)
jk_results = jkanime_scraper.search_anime(query="mushoku")
print(jk_results)

# Get anime info
an_info = animeflv_scraper.get_anime_info(anime_id=an_results.animes[0].id)
print(an_info)
jk_info = jkanime_scraper.get_anime_info(anime_id=jk_results.animes[0].id)
print(jk_info)

# Get table download links
an_table_links = animeflv_scraper.get_table_download_links(
    anime_id=an_info.id, episode_id=1
)
print(an_table_links)
jk_table_links = jkanime_scraper.get_table_download_links(
    anime_id=jk_info.id, episode_id=1
)
print(jk_table_links)

# Get iframe download links
an_iframe_links = animeflv_scraper.get_iframe_download_links(
    anime_id=an_info.id, episode_id=1
)
print(an_iframe_links)
jk_iframe_links = jkanime_scraper.get_iframe_download_links(
    anime_id=jk_info.id, episode_id=1
)
print(jk_iframe_links)

# Get file download links
an_file_links = animeflv_scraper.get_file_download_links(
    download_info=an_iframe_links.download_links[0]
)
print(an_file_links)
jk_file_links = jkanime_scraper.get_file_download_links(
    download_info=jk_table_links.download_links[0]
)
print(jk_file_links)
