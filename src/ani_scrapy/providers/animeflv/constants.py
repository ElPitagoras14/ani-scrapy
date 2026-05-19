from ani_scrapy.core.schemas import AnimeType, RelatedType

BASE_URL = "https://www4.animeflv.net"
SEARCH_ENDPOINT = "browse"
ANIME_VIDEO_ENDPOINT = "ver"
BASE_EPISODE_IMG_URL = "https://cdn.animeflv.net/screenshots"
SW_DOWNLOAD_URL = "https://hgplaycdn.com/f"

ANIME_TYPE_MAP = {
    "Anime": AnimeType.TV,
    "Pelicula": AnimeType.MOVIE,
    "OVA": AnimeType.OVA,
    "Especial": AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    "Precuela": RelatedType.PREQUEL,
    "Secuela": RelatedType.SEQUEL,
    "Historia Paralela": RelatedType.PARALLEL_HISTORY,
    "Historia Principal": RelatedType.MAIN_HISTORY,
}

SUPPORTED_SERVERS = ["SW", "YourUpload"]
