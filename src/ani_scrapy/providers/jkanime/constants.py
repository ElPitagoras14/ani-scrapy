from ani_scrapy.core.schemas import _AnimeType, _RelatedType

BASE_URL = "https://jkanime.net"
SEARCH_ENDPOINT = "buscar"
BASE_EPISODE_IMG_URL = "https://cdn.jkdesu.com/assets/images/animes/video/image_thumb"
SW_DOWNLOAD_URL = "https://flaswish.com/f"
IMPERSONATE = "chrome"

ANIME_TYPE_MAP = {
    "Serie": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    "Adicional": _RelatedType.PARALLEL_HISTORY,
    "Resumen": _RelatedType.PARALLEL_HISTORY,
    "Version Alternativa": _RelatedType.PARALLEL_HISTORY,
    "Personaje Incluido": _RelatedType.PARALLEL_HISTORY,
    "Secuela": _RelatedType.SEQUEL,
    "Precuela": _RelatedType.PREQUEL,
}

SUPPORTED_SERVERS = ["Streamwish", "Mediafire"]
