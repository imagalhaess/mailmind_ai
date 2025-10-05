"""
Testes para funções utilitárias.
"""
import pytest
from app.utils.text_preprocess import normalize_whitespace, remove_stopwords, basic_preprocess


class TestTextPreprocess:
    """Testes para funções de pré-processamento de texto."""
    
    def test_normalize_whitespace_removes_extra_spaces(self):
        """Verifica se espaços extras são removidos."""
        text = "Teste   com    espaços    extras"
        result = normalize_whitespace(text)
        assert "   " not in result
        assert result == "Teste com espaços extras"
    
    def test_normalize_whitespace_removes_newlines(self):
        """Verifica se quebras de linha são normalizadas."""
        text = "Linha 1\n\n\nLinha 2"
        result = normalize_whitespace(text)
        assert result == "Linha 1 Linha 2"
    
    def test_remove_stopwords_removes_common_words(self):
        """Verifica se stopwords comuns são removidas."""
        text = "o email de teste para análise"
        result = remove_stopwords(text)
        
        # Stopwords como "o", "de", "para" devem ser removidas
        assert "email" in result
        assert "teste" in result
        assert "análise" in result
    
    def test_remove_stopwords_preserves_important_words(self):
        """Verifica se palavras importantes são preservadas."""
        text = "urgente proposta comercial importante"
        result = remove_stopwords(text)
        
        assert "urgente" in result
        assert "proposta" in result
        assert "comercial" in result
        assert "importante" in result
    
    def test_basic_preprocess_combines_operations(self):
        """Verifica se basic_preprocess combina normalização e remoção de stopwords."""
        text = "  O   email   de   teste   "
        result = basic_preprocess(text)
        
        # Deve normalizar espaços e remover stopwords
        assert "   " not in result
        assert result.strip() != ""
    
    def test_basic_preprocess_handles_empty_string(self):
        """Verifica se basic_preprocess trata string vazia."""
        result = basic_preprocess("")
        assert result == ""
    
    def test_basic_preprocess_handles_only_stopwords(self):
        """Verifica se basic_preprocess trata texto com apenas stopwords."""
        text = "o a e de da do"
        result = basic_preprocess(text)
        # Resultado pode ser vazio ou conter apenas espaços
        assert len(result.strip()) == 0
