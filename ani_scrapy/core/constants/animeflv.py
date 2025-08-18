from ani_scrapy.core.schemas import _AnimeType, _RelatedType


BASE_URL = "https://animeflv.net"
SEARCH_URL = "https://animeflv.net/browse"
ANIME_VIDEO_URL = "https://animeflv.net/ver"
ANIME_URL = "https://animeflv.net/anime"
BASE_EPISODE_IMG_URL = "https://cdn.animeflv.net/screenshots"

SW_DOWNLOAD_URL = "https://hgplaycdn.com/f"


related_type_map = {
    "Precuela": _RelatedType.PREQUEL,
    "Sequel": _RelatedType.SEQUEL,
    "Historia Paralela": _RelatedType.PARALLEL_HISTORY,
    "Historia Principal": _RelatedType.MAIN_HISTORY,
}

anime_type_map = {
    "Anime": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}
