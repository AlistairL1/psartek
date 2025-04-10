from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TransportGuess(models.Model):
    TRANSPORT_CHOICES = [
        ('car', 'Voiture'),
        ('train', 'Train'),
        ('bus', 'Bus'),
        ('plane', 'Avion'),
        ('ship', 'Bateau'),
        ('walking', 'Marche'),
        ('bike', 'Vélo'),
        ('subway', 'Métro/RER')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transports = models.JSONField(default=list)  # Liste des transports sélectionnés
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {', '.join(self.get_transports_display())}"

    def get_transports_display(self):
        """Retourne les noms affichables des transports sélectionnés"""
        return [dict(self.TRANSPORT_CHOICES)[transport] for transport in self.transports]

    def add_transport(self, transport):
        """Ajoute un transport à la liste s'il n'existe pas déjà"""
        if transport not in self.transports:
            self.transports.append(transport)
            self.save()

    def remove_transport(self, transport):
        """Retire un transport de la liste"""
        if transport in self.transports:
            self.transports.remove(transport)
            self.save()

    def clear_transports(self):
        """Vide la liste des transports"""
        self.transports = []
        self.save()

class MapGuess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city_name = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    total_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.city_name or 'Ville inconnue'}"
