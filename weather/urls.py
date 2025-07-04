from django.urls import path
from .views import WeatherAPIView, HistoryAPIView

# Mapeia as URLs para as Views correspondentes
urlpatterns = [
    # Rota para o endpoint de clima
    path('weather/', WeatherAPIView.as_view(), name='weather-api'),
    # Rota para o endpoint de histórico
    path('history/', HistoryAPIView.as_view(), name='history-api'),
]