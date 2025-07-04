import os
import requests
from typing import Dict, Any, Optional

# Este arquivo isola a lógica de comunicação com a API externa (OpenWeatherMap).
# Isso é um exemplo do Princípio de Responsabilidade Única (SRP) do SOLID.
# A view não precisa saber como os dados do clima são obtidos, apenas que pode pedi-los a este serviço.

class OpenWeatherMapService:
    """
    Serviço para interagir com a API do OpenWeatherMap.
    """
    API_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key para o OpenWeatherMap não foi fornecida.")
        self.api_key = api_key

    def get_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Busca os dados de clima para uma cidade específica.

        Args:
            city (str): O nome da cidade.

        Returns:
            Optional[Dict[str, Any]]: Um dicionário com os dados do clima se a
                                      cidade for encontrada, ou None caso contrário.
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',  # Para obter temperatura em Celsius
            'lang': 'pt_br'   # Para obter descrições em português
        }

        try:
            response = requests.get(self.API_URL, params=params)
            # Levanta uma exceção para respostas com códigos de erro (4xx ou 5xx)
            response.raise_for_status()

            # Se a cidade não for encontrada, a API retorna 404, que é tratado por raise_for_status.
            # Se for sucesso (200), retornamos o JSON.
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            # Especificamente, o erro 404 significa "Cidade não encontrada"
            if response.status_code == 404:
                return None
            # Para outros erros HTTP (ex: 401 Unauthorized - API key inválida), relançamos a exceção
            # para ser tratada em uma camada superior.
            print(f"HTTP error occurred: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            # Para outros erros de rede (DNS, conexão, etc.)
            print(f"Request error occurred: {req_err}")
            raise