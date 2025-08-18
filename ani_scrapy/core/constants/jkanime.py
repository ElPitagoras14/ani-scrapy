from ani_scrapy.core.schemas import _AnimeType, _RelatedType


BASE_URL = "https://jkanime.net"
SEARCH_URL = "https://jkanime.net/buscar"
BASE_EPISODE_IMG_URL = (
    "https://cdn.jkdesu.com/assets/images/animes/video/image_thumb"
)

SW_DOWNLOAD_URL = "https://flaswish.com/f"

IMPERSONATE = "chrome"

related_type_map = {
    "Adicional": _RelatedType.PARALLEL_HISTORY,
    "Resumen": _RelatedType.PARALLEL_HISTORY,
    "Version Alternativa": _RelatedType.PARALLEL_HISTORY,
    "Personaje Incluido": _RelatedType.PARALLEL_HISTORY,
    "Secuela": _RelatedType.SEQUEL,
    "Precuela": _RelatedType.PREQUEL,
}


anime_type_map = {
    "Serie": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}

month_map = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}

not_supported_yet = [
    "Mega",
    "VOE",
    "Vidhie",
    "Filemoon",
    "Mixdrop",
    "Mp4upload",
    "Streamtape",
    "Doodstream",
]
