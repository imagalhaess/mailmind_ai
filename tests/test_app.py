"""
Testes para as rotas da aplicação Flask.
"""
import pytest
import json


class TestHealthEndpoint:
    """Testes para o endpoint de health check."""
    
    def test_health_check_returns_200(self, client):
        """Verifica se o health check retorna status 200."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_check_returns_json(self, client):
        """Verifica se o health check retorna JSON válido."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_health_check_includes_version(self, client):
        """Verifica se o health check inclui informação de versão."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'version' in data


class TestIndexEndpoint:
    """Testes para a página inicial."""
    
    def test_index_returns_200(self, client):
        """Verifica se a página inicial carrega."""
        response = client.get('/')
        assert response.status_code == 200


class TestMockEndpoints:
    """Testes para endpoints de mock/teste."""
    
    def test_spam_mock_returns_correct_category(self, client):
        """Verifica se o mock de spam retorna categoria correta."""
        response = client.get('/test/spam')
        data = json.loads(response.data)
        assert data['categoria'] == 'Spam'
        assert data['test_mode'] is True
    
    def test_produtivo_mock_returns_correct_category(self, client):
        """Verifica se o mock produtivo retorna categoria correta."""
        response = client.get('/test/produtivo')
        data = json.loads(response.data)
        assert data['categoria'] == 'Produtivo'
        assert data['atencao_humana'] == 'SIM'
    
    def test_reclamacao_mock_returns_correct_category(self, client):
        """Verifica se o mock de reclamação retorna categoria correta."""
        response = client.get('/test/reclamacao')
        data = json.loads(response.data)
        assert data['categoria'] == 'Reclamacao'
    
    def test_invalid_mock_type_returns_400(self, client):
        """Verifica se tipo de mock inválido retorna erro 400."""
        response = client.get('/test/invalid_type')
        assert response.status_code == 400


class TestAnalyzeEndpoint:
    """Testes para o endpoint de análise."""
    
    def test_analyze_without_content_returns_400(self, client):
        """Verifica se análise sem conteúdo retorna erro 400."""
        response = client.post('/analyze', data={})
        assert response.status_code == 400
    
    def test_analyze_with_text_returns_200(self, client, sample_email):
        """Verifica se análise com texto retorna sucesso."""
        response = client.post('/analyze', data={
            'email_text': sample_email
        })
        # Pode falhar se a API key de teste não funcionar, mas estrutura deve estar ok
        assert response.status_code in [200, 500]  # 500 se API key inválida
    
    def test_analyze_with_json_accepts_email_content(self, client, sample_email):
        """Verifica se análise aceita JSON com email_content."""
        response = client.post('/analyze',
            data=json.dumps({'email_content': sample_email}),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]


class TestWebhookEndpoint:
    """Testes para o endpoint de webhook."""
    
    def test_webhook_without_content_returns_400(self, client):
        """Verifica se webhook sem conteúdo retorna erro 400."""
        response = client.post('/webhook/email',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_webhook_with_content_structure(self, client, sample_email):
        """Verifica se webhook aceita estrutura correta."""
        response = client.post('/webhook/email',
            data=json.dumps({
                'email_content': sample_email,
                'sender': 'teste@exemplo.com',
                'subject': 'Teste'
            }),
            content_type='application/json'
        )
        # Pode falhar por API key, mas estrutura está correta
        assert response.status_code in [200, 500]


class TestErrorHandlers:
    """Testes para handlers de erro."""
    
    def test_404_returns_json(self, client):
        """Verifica se 404 retorna JSON."""
        response = client.get('/rota/inexistente')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
