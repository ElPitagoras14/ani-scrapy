import re


def clean_text(text: str) -> str:
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_related_type(text: str) -> str:
    text = re.sub(r"[\(\)]", "", text)
    return text.strip()
