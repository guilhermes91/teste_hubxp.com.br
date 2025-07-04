from django.urls import reverse
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
import requests

from .models import SearchHistory
from .services import OpenWeatherMapService

# Não precisamos mais do @override_settings, pois a nova solução é mais robusta.
# Vamos removê-lo para evitar confusão.

class WeatherAPITests(APITestCase):
    """
    Suite de testes para a API de Clima, cobrindo endpoints, cache e histórico.
    """

    def setUp(self):
        """
        Configuração inicial para cada teste. Limpa o cache e o banco de dados.
        """
        cache.clear()
        SearchHistory.objects.all().delete()

    @patch('weather.services.OpenWeatherMapService.get_weather')
    def test_get_weather_success_and_history_creation(self, mock_get_weather):
        """
        TESTE DE INTEGRAÇÃO:
        Verifica se o endpoint /api/weather/ retorna sucesso (200),
        cria um registro no histórico e se o serviço externo é chamado.
        """
        mock_response = {
            'name': 'London',
            'main': {'temp': 15.0, 'humidity': 80},
            'weather': [{'description': 'céu limpo'}]
        }
        mock_get_weather.return_value = mock_response
        url = reverse('weather-api')
        response = self.client.get(url, {'city': 'London'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'London')
        self.assertEqual(response.data['temperature_celsius'], 15.0)
        mock_get_weather.assert_called_once_with('london')
        self.assertEqual(SearchHistory.objects.count(), 1)
        self.assertEqual(SearchHistory.objects.first().city, 'London')

    @patch('weather.services.OpenWeatherMapService.get_weather')
    def test_cache_functionality(self, mock_get_weather):
        """
        TESTE DE INTEGRAÇÃO:
        Verifica se o cache está funcionando corretamente. O serviço externo
        deve ser chamado apenas na primeira vez.
        """
        mock_response = {
            'name': 'Paris',
            'main': {'temp': 20.0, 'humidity': 60},
            'weather': [{'description': 'algumas nuvens'}]
        }
        mock_get_weather.return_value = mock_response
        url = reverse('weather-api')
        self.client.get(url, {'city': 'Paris'})
        mock_get_weather.assert_called_once_with('paris')
        response = self.client.get(url, {'city': 'Paris'})
        self.assertEqual(mock_get_weather.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Paris')

    @patch('weather.services.OpenWeatherMapService.get_weather')
    def test_history_limit(self, mock_get_weather):
        """
        TESTE DE INTEGRAÇÃO:
        Verifica se o histórico é limitado a 10 registros.
        """
        mock_get_weather.return_value = {
            'name': 'Test City',
            'main': {'temp': 10.0, 'humidity': 50},
            'weather': [{'description': 'teste'}]
        }
        
        weather_url = reverse('weather-api')
        
        # --- A SOLUÇÃO DEFINITIVA APLICADA AQUI ---
        # Fazemos 12 chamadas, cada uma com um endereço de IP forjado diferente.
        # O AnonRateThrottle usa o IP para contar as requisições. Ao mudar o IP,
        # cada requisição é contada como a primeira de um novo usuário.
        for i in range(12):
            city_name = f'City{i}'
            mock_get_weather.return_value['name'] = city_name
            # Forjamos o endereço de IP usando o parâmetro extra REMOTE_ADDR
            ip_address = f'192.168.1.{i}'
            response = self.client.get(weather_url, {'city': city_name}, REMOTE_ADDR=ip_address)
            # Verificamos que nenhuma dessas chamadas foi bloqueada
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verifica se o número total de registros no banco de dados é 10
        self.assertEqual(SearchHistory.objects.count(), 10)

        # Faz a requisição para o endpoint de histórico (com mais um IP diferente)
        history_url = reverse('history-api')
        response = self.client.get(history_url, REMOTE_ADDR='192.168.1.100')

        # Este assert agora passará, pois o rate limiter nunca foi ativado.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        cities_in_history = [item['city'] for item in response.data]
        self.assertNotIn('City0', cities_in_history)
        self.assertNotIn('City1', cities_in_history)
        self.assertIn('City11', cities_in_history)

# ===================================================================
# TESTES UNITÁRIOS
# ===================================================================
class OpenWeatherMapServiceUnitTests(TestCase):
    """
    Suite de testes unitários para o OpenWeatherMapService.
    Testa a lógica do serviço em total isolamento, sem chamadas de rede reais.
    """
    def test_init_raises_error_if_no_api_key(self):
        with self.assertRaises(ValueError) as context:
            OpenWeatherMapService(api_key=None)
        self.assertTrue('API key para o OpenWeatherMap não foi fornecida.' in str(context.exception))

    @patch('weather.services.requests.get')
    def test_get_weather_success(self, mock_requests_get):
        fake_api_response = {
            "name": "Fortaleza",
            "main": {"temp": 28.5, "humidity": 75},
            "weather": [{"description": "sol forte"}]
        }
        mock_requests_get.return_value = Mock(status_code=200)
        mock_requests_get.return_value.json.return_value = fake_api_response
        mock_requests_get.return_value.raise_for_status.return_value = None
        service = OpenWeatherMapService(api_key="fake_key_123")
        result = service.get_weather(city="Fortaleza")
        self.assertEqual(result, fake_api_response)
        expected_params = {
            'q': 'Fortaleza',
            'appid': 'fake_key_123',
            'units': 'metric',
            'lang': 'pt_br'
        }
        mock_requests_get.assert_called_once_with(
            "https://api.openweathermap.org/data/2.5/weather",
            params=expected_params
        )

    @patch('weather.services.requests.get')
    def test_get_weather_city_not_found(self, mock_requests_get):
        mock_response = Mock(status_code=404)
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_requests_get.return_value = mock_response
        service = OpenWeatherMapService(api_key="fake_key_123")
        result = service.get_weather(city="CidadeInexistente")
        self.assertIsNone(result)