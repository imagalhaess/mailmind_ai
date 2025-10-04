import re
from typing import List


_DEFAULT_STOPWORDS: List[str] = [
    "a", "o", "e", "de", "da", "do", "das", "dos", "um", "uma",
    "em", "para", "por", "no", "na", "nos", "nas", "com", "sem",
    "que", "se", "os", "as", "ao", "à", "às", "aos"
]


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_stopwords(text: str, stopwords: List[str] = None) -> str:
    if stopwords is None:
        stopwords = _DEFAULT_STOPWORDS
    tokens = re.findall(r"[\wÀ-ÿ'-]+", text.lower())
    filtered = [t for t in tokens if t not in stopwords]
    return " ".join(filtered)


def basic_preprocess(text: str) -> str:
    """
    Pré-processamento simples: normaliza espaços e remove stopwords comuns.
    Mantemos leve para não adicionar dependências pesadas.
    """
    text = normalize_whitespace(text)
    text = remove_stopwords(text)
    return text


