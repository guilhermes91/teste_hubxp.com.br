from django.db import models

class SearchHistory(models.Model):
    """
    Modelo para armazenar o histórico de pesquisas de clima.
    """
    city = models.CharField(max_length=100, help_text="Nome da cidade pesquisada")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Data e hora da pesquisa")
    # Usamos JSONField para armazenar a resposta completa da API, o que nos dá flexibilidade.
    data = models.JSONField(help_text="Dados da resposta da API de clima")

    class Meta:
        # Ordena os resultados mais recentes primeiro por padrão
        ordering = ['-timestamp']
        # Nome plural para exibição no Django Admin
        verbose_name_plural = "Search Histories"

    def __str__(self):
        return f"{self.city} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"