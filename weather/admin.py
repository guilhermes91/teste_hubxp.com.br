from django.contrib import admin
from .models import SearchHistory

# Registra o modelo SearchHistory no painel de administração do Django.
# Isso nos permite visualizar e gerenciar os dados do histórico facilmente.
@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('city', 'timestamp')
    list_filter = ('timestamp', 'city')
    search_fields = ('city',)