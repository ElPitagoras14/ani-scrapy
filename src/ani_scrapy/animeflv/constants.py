from ani_scrapy.core.schemas import _AnimeType, _RelatedType

BASE_URL = "https://animeflv.net"
SEARCH_ENDPOINT = "browse"
ANIME_VIDEO_ENDPOINT = "ver"
ANIME_ENDPOINT = "anime"
BASE_EPISODE_IMG_URL = "https://cdn.animeflv.net/screenshots"
SW_DOWNLOAD_URL = "https://hgplaycdn.com/f"

ANIME_TYPE_MAP = {
    "Anime": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    "Precuela": _RelatedType.PREQUEL,
    "Secuela": _RelatedType.SEQUEL,
    "Historia Paralela": _RelatedType.PARALLEL_HISTORY,
    "Historia Principal": _RelatedType.MAIN_HISTORY,
}
