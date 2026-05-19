from ani_scrapy.core.schemas import AnimeType, RelatedType

BASE_URL = "https://jkanime.net"
SEARCH_ENDPOINT = "buscar"
SW_DOWNLOAD_URL = "https://flaswish.com/f"

ANIME_TYPE_MAP = {
    "Serie": AnimeType.TV,
    "Pelicula": AnimeType.MOVIE,
    "OVA": AnimeType.OVA,
    "Especial": AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    "Adicional": RelatedType.PARALLEL_HISTORY,
    "Resumen": RelatedType.PARALLEL_HISTORY,
    "Version Alternativa": RelatedType.PARALLEL_HISTORY,
    "Personaje Incluido": RelatedType.PARALLEL_HISTORY,
    "Secuela": RelatedType.SEQUEL,
    "Precuela": RelatedType.PREQUEL,
}

SUPPORTED_SERVERS = ["Streamwish", "Mediafire"]
