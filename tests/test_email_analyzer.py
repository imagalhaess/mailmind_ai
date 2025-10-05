"""
Testes para o serviço de análise de emails.
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.services.email_analyzer import EmailAnalyzerService


class TestEmailAnalyzerService:
    """Testes para o EmailAnalyzerService."""
    
    def test_build_prompt_includes_email_content(self):
        """Verifica se o prompt inclui o conteúdo do email."""
        mock_client = Mock()
        service = EmailAnalyzerService(client=mock_client)
        
        email_content = "Teste de email"
        prompt = service.build_prompt(email_content)
        
        assert email_content in prompt
        assert "JSON" in prompt
        assert "categoria" in prompt.lower()
    
    def test_build_prompt_includes_categories(self):
        """Verifica se o prompt inclui as categorias esperadas."""
        mock_client = Mock()
        service = EmailAnalyzerService(client=mock_client)
        
        prompt = service.build_prompt("teste")
        
        assert "Spam" in prompt
        assert "Produtivo" in prompt
        assert "Reclamação" in prompt
    
    def test_analyze_calls_client_generate_json(self):
        """Verifica se analyze chama o método correto do cliente."""
        mock_client = Mock()
        mock_client.generate_json = MagicMock(return_value='{"categoria": "Spam"}')
        
        service = EmailAnalyzerService(client=mock_client)
        result = service.analyze("teste")
        
        mock_client.generate_json.assert_called_once()
        assert result['categoria'] == 'Spam'
    
    def test_analyze_handles_invalid_json(self):
        """Verifica se analyze trata JSON inválido corretamente."""
        mock_client = Mock()
        mock_client.generate_json = MagicMock(return_value='invalid json')
        
        service = EmailAnalyzerService(client=mock_client)
        result = service.analyze("teste")
        
        assert 'erro' in result
        assert 'conteudo' in result
    
    def test_analyze_returns_dict(self):
        """Verifica se analyze sempre retorna um dicionário."""
        mock_client = Mock()
        mock_client.generate_json = MagicMock(return_value='{"test": "value"}')
        
        service = EmailAnalyzerService(client=mock_client)
        result = service.analyze("teste")
        
        assert isinstance(result, dict)
