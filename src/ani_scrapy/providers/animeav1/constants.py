"""AnimeAV1 constants."""

from ani_scrapy.core.schemas import _AnimeType, _RelatedType

BASE_URL = "https://animeav1.com"
SEARCH_ENDPOINT = "/catalogo"
ANIME_COVER_URL = "https://cdn.animeav1.com"

ANIME_TYPE_MAP = {
    "TV Anime": _AnimeType.TV,
    "Pelicula": _AnimeType.MOVIE,
    "OVA": _AnimeType.OVA,
    "Especial": _AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    1: _RelatedType.PREQUEL,
    2: _RelatedType.SEQUEL,
}
