from django.contrib import admin
from .models import TransportGuess, MapGuess, GameEvaluation

@admin.register(TransportGuess)
class TransportGuessAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_transports_list', 'is_verified', 'score', 'created_at')
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
    list_display = ('user', 'city_name', 'is_correct', 'score', 'distance_to_target', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('user__username', 'city_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(GameEvaluation)
class GameEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'evaluated_by', 'evaluated_at')
    list_filter = ('evaluated_at',)
    search_fields = ('user__username', 'evaluated_by__username')
    readonly_fields = ('evaluated_at',)
    ordering = ('-evaluated_at',)

    def get_transport_score(self, obj):
        try:
            transport_guess = TransportGuess.objects.get(user=obj.user)
            return transport_guess.score if transport_guess.score is not None else '-'
        except TransportGuess.DoesNotExist:
            return '-'
    get_transport_score.short_description = 'Score Transport'

    def get_map_score(self, obj):
        try:
            map_guess = MapGuess.objects.get(user=obj.user)
            return map_guess.score if map_guess.score is not None else '-'
        except MapGuess.DoesNotExist:
            return '-'
    get_map_score.short_description = 'Score Map'

    def get_total_score(self, obj):
        try:
            transport_guess = TransportGuess.objects.get(user=obj.user)
            map_guess = MapGuess.objects.get(user=obj.user)
            transport_score = transport_guess.score if transport_guess.score is not None else 0
            map_score = map_guess.score if map_guess.score is not None else 0
            return transport_score + map_score
        except (TransportGuess.DoesNotExist, MapGuess.DoesNotExist):
            return '-'
    get_total_score.short_description = 'Score Total'
