import os
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SearchHistory
from .serializers import WeatherSerializer, SearchHistorySerializer
from .services import OpenWeatherMapService

class WeatherAPIView(APIView):
    """
    Endpoint da API para obter o clima atual de uma cidade.
    GET /api/weather/?city=<nome_da_cidade>
    """
    # Define o limite máximo de consultas no histórico
    HISTORY_LIMIT = 10

    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response(
                {"error": "O parâmetro 'city' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Normaliza o nome da cidade para a chave do cache
        city_normalized = city.lower().strip()
        cache_key = f"weather_{city_normalized}"

        # 1. Tenta buscar os dados do cache
        cached_data = cache.get(cache_key)
        if cached_data:
            # Se encontrou no cache, retorna os dados diretamente
            return Response(cached_data)

        # 2. Se não está no cache, busca na API externa
        api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        service = OpenWeatherMapService(api_key=api_key)

        try:
            weather_data = service.get_weather(city_normalized)
        except Exception as e:
            # Captura erros de rede ou da API key
            return Response(
                {"error": f"Erro ao comunicar com a API de clima: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        if not weather_data:
            return Response(
                {"error": "Cidade não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Formata a resposta para o nosso padrão desejado
        formatted_response = {
            "city": weather_data['name'],
            "temperature_celsius": weather_data['main']['temp'],
            "description": weather_data['weather'][0]['description'],
            "humidity": weather_data['main']['humidity']
        }

        serializer = WeatherSerializer(data=formatted_response)
        if not serializer.is_valid():
            # Isso é uma salvaguarda, mas a formatação manual deve ser confiável
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        validated_data = serializer.validated_data

        # 4. Salva a resposta no cache por 10 minutos (600 segundos)
        cache.set(cache_key, validated_data, timeout=600)

        # 5. Salva a consulta no histórico do banco de dados
        SearchHistory.objects.create(city=validated_data['city'], data=validated_data)

        # 6. Garante que o histórico não exceda o limite de 10 entradas
        # Pega os IDs dos registros mais antigos que o 10º
        oldest_records_ids = SearchHistory.objects.order_by('-timestamp').values_list('id', flat=True)[self.HISTORY_LIMIT:]
        if oldest_records_ids:
            # Deleta os registros excedentes
            SearchHistory.objects.filter(id__in=list(oldest_records_ids)).delete()

        return Response(validated_data, status=status.HTTP_200_OK)


class HistoryAPIView(APIView):
    """
    Endpoint da API para obter o histórico das últimas 10 pesquisas.
    GET /api/history/
    """
    def get(self, request):
        # Busca as últimas 10 entradas do histórico, já ordenadas pelo modelo
        history_records = SearchHistory.objects.all()[:10]
        # Serializa os dados para o formato JSON
        serializer = SearchHistorySerializer(history_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)