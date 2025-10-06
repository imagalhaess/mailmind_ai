import re
import logging
from typing import List

logger = logging.getLogger(__name__)


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
    Pré-processamento ULTRA OTIMIZADO: foco máximo em velocidade.
    Versão super rápida para devs iniciantes.
    """
    # OTIMIZAÇÃO 1: Se o texto for muito grande, processa apenas uma parte
    if len(text) > 5000:  # Se maior que 5k caracteres (mais agressivo)
        text = text[:5000]  # Pega apenas os primeiros 5k
        logger.info("Texto truncado para 5k caracteres para otimizar processamento")
    
    # OTIMIZAÇÃO 2: Normaliza espaços de uma vez só (mais rápido)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # OTIMIZAÇÃO 3: Remove stopwords apenas se o texto for pequeno (mais rápido)
    if len(text) < 2000:  # Só remove stopwords se for texto muito pequeno
        text = remove_stopwords(text)
    
    return text


