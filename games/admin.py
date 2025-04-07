from django.contrib import admin
from .models import TransportGuess, MapGuess

@admin.register(TransportGuess)
class TransportGuessAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_transports_list', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_transports_list(self, obj):
        """Retourne la liste des transports sélectionnés sous forme de chaîne"""
        return ', '.join(obj.get_transports_display())
    get_transports_list.short_description = 'Transports'

@admin.register(MapGuess)
class MapGuessAdmin(admin.ModelAdmin):
    list_display = ('user', 'city_name', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'city_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
