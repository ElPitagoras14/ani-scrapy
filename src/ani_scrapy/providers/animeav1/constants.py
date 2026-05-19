"""AnimeAV1 constants."""

from ani_scrapy.core.schemas import AnimeType, RelatedType

BASE_URL = "https://animeav1.com"
SEARCH_ENDPOINT = "/catalogo"
ANIME_COVER_URL = "https://cdn.animeav1.com"

ANIME_TYPE_MAP = {
    "TV Anime": AnimeType.TV,
    "Pelicula": AnimeType.MOVIE,
    "OVA": AnimeType.OVA,
    "Especial": AnimeType.SPECIAL,
}

RELATED_TYPE_MAP = {
    1: RelatedType.PREQUEL,
    2: RelatedType.SEQUEL,
}

SUPPORTED_SERVERS = ["PDrain", "UPNShare"]
