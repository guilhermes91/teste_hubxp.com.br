from rest_framework import serializers
from .models import SearchHistory

# Serializers convertem tipos de dados complexos, como querysets e instâncias de modelo,
# em tipos de dados nativos do Python que podem ser facilmente renderizados em JSON.

class WeatherSerializer(serializers.Serializer):
    """
    Serializer para formatar a resposta final da nossa API de clima.
    Ele não está ligado a um modelo, apenas define a estrutura de saída.
    """
    city = serializers.CharField()
    temperature_celsius = serializers.FloatField()
    description = serializers.CharField()
    humidity = serializers.IntegerField()

class SearchHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo SearchHistory.
    Ele converte as instâncias do modelo em representações JSON.
    """
    class Meta:
        model = SearchHistory
        # Define os campos do modelo que serão incluídos na serialização
        fields = ['id', 'city', 'timestamp', 'data']