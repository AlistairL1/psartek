from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import MapGuess, TransportGuess, GameEvaluation
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.urls import reverse
from math import radians, sin, cos, sqrt, atan2

def is_organizer(user):
    return user.is_staff or user.groups.filter(name='Organisateur').exists()

@login_required
def game_home(request):
    return render(request, 'games/game_home.html')

@login_required
def poll(request):
    # Vérifier si l'utilisateur a déjà répondu
    has_responded = TransportGuess.objects.filter(user=request.user).exists()
    can_modify = True  # À implémenter selon vos règles de modification
    want_to_modify = request.GET.get('modify') == 'true'
    
    if request.method == 'POST':
        # Supprimer les anciennes réponses si modification
        if want_to_modify:
            TransportGuess.objects.filter(user=request.user).delete()
        
        # Récupérer les transports sélectionnés
        selected_transports = request.POST.getlist('transport')
        
        if not selected_transports:
            messages.error(request, 'Veuillez sélectionner au moins un mode de transport.')
            return redirect('poll')
        
        # Créer une nouvelle réponse avec la liste des transports
        TransportGuess.objects.create(
            user=request.user,
            transports=selected_transports
        )
        
        messages.success(request, 'Votre réponse a été enregistrée avec succès !')
        return redirect('poll')
    
    # Récupérer les transports déjà sélectionnés
    guess = TransportGuess.objects.filter(user=request.user).first()
    selected_transport_values = guess.transports if guess else []
    
    return render(request, 'games/poll.html', {
        'has_responded': has_responded,
        'can_modify': can_modify,
        'selected_transports': guess,
        'selected_transport_values': selected_transport_values,
        'want_to_modify': want_to_modify
    })

@login_required
def map_guess_view(request):
    has_responded = MapGuess.objects.filter(user=request.user).exists()
    can_modify = True  # À implémenter selon vos règles de modification
    want_to_modify = request.GET.get('modify') == 'true'
    
    if request.method == 'POST':
        # Supprimer l'ancienne réponse si modification
        if want_to_modify:
            MapGuess.objects.filter(user=request.user).delete()
        
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        city_name = request.POST.get('city_name')
        
        if not latitude or not longitude:
            messages.error(request, 'Veuillez sélectionner un emplacement sur la carte.')
            return redirect('map_guess')
        
        # Créer ou mettre à jour la réponse
        MapGuess.objects.create(
            user=request.user,
            latitude=latitude,
            longitude=longitude,
            city_name=city_name
        )
        
        messages.success(request, 'Votre réponse a été enregistrée avec succès !')
        return redirect('map_guess')
    
    # Récupérer la réponse existante
    guess = MapGuess.objects.filter(user=request.user).first()
    latitude = guess.latitude if guess else None
    longitude = guess.longitude if guess else None
    city_name = guess.city_name if guess else None
    
    return render(request, 'games/map_guess.html', {
        'has_responded': has_responded,
        'can_modify': can_modify,
        'want_to_modify': want_to_modify,
        'latitude': latitude,
        'longitude': longitude,
        'city_name': city_name
    })

@login_required
def results_view(request):
    # Récupérer les réponses de l'utilisateur
    transport_guess = TransportGuess.objects.filter(user=request.user).first()
    map_guess = MapGuess.objects.filter(user=request.user).first()
    
    # Récupérer le classement
    leaderboard = []
    # Exclure les utilisateurs du groupe Technicien
    users = User.objects.exclude(groups__name='Technicien')
    for user in users:
        transport_guess_user = TransportGuess.objects.filter(user=user).first()
        map_guess_user = MapGuess.objects.filter(user=user).first()
        
        # Calculer le score total
        transport_score = transport_guess_user.score if transport_guess_user and transport_guess_user.score is not None else 0
        map_score = map_guess_user.score if map_guess_user and map_guess_user.score is not None else 0
        total_score = transport_score + map_score
        
        leaderboard.append({
            'username': user.username,
            'first_name': user.first_name,
            'total_score': total_score,
            'is_current_user': user == request.user
        })
    
    # Trier le classement par score décroissant
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Si l'utilisateur est un organisateur, ajouter les données supplémentaires
    if is_organizer(request.user):
        # Récupérer tous les utilisateurs qui ont participé (exclure les techniciens)
        all_users = User.objects.exclude(groups__name='Technicien').filter(
            transportguess__isnull=False,
            mapguess__isnull=False
        ).distinct()
        
        # Récupérer toutes les réponses pour l'évaluation
        all_responses = []
        for user in all_users:
            transport_guess = TransportGuess.objects.filter(user=user).first()
            map_guess = MapGuess.objects.filter(user=user).first()
            evaluation = GameEvaluation.objects.filter(user=user).first()
            
            all_responses.append({
                'user': user,
                'transport_guess': transport_guess,
                'map_guess': map_guess,
                'evaluation': evaluation
            })
        
        return render(request, 'games/results.html', {
            'transport_guess': transport_guess,
            'map_guess': map_guess,
            'leaderboard': leaderboard,
            'is_organizer': True,
            'all_responses': all_responses
        })
    
    # Pour les utilisateurs normaux, retourner uniquement leurs réponses et le classement
    return render(request, 'games/results.html', {
        'transport_guess': transport_guess,
        'map_guess': map_guess,
        'leaderboard': leaderboard,
        'is_organizer': False
    })

@login_required
@user_passes_test(is_organizer)
def evaluate_responses(request):
    # Récupérer tous les utilisateurs qui ont participé aux jeux
    users = User.objects.filter(
        transportguess__isnull=False,
        mapguess__isnull=False
    ).distinct()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # Récupérer les réponses de l'utilisateur
        transport_guess = TransportGuess.objects.get(user=user)
        map_guess = MapGuess.objects.get(user=user)
        
        # Mettre à jour les évaluations individuelles
        transport_guess.is_verified = request.POST.get('transport_correct') == 'true'
        transport_guess.score = int(request.POST.get('transport_score', 0))
        transport_guess.feedback = request.POST.get('transport_feedback', '')
        transport_guess.save()
        
        map_guess.is_correct = request.POST.get('map_correct') == 'true'
        map_guess.score = int(request.POST.get('map_score', 0))
        map_guess.distance_to_target = float(request.POST.get('distance_to_target', 0))
        map_guess.feedback = request.POST.get('map_feedback', '')
        map_guess.save()
        
        # Créer ou mettre à jour l'évaluation globale
        evaluation, created = GameEvaluation.objects.update_or_create(
            user=user,
            defaults={
                'evaluated_by': request.user,
                'feedback': request.POST.get('global_feedback', '')
            }
        )
        
        messages.success(request, f'Les réponses de {user.username} ont été évaluées avec succès.')
        return redirect('evaluate_responses')
    
    return render(request, 'games/evaluate_responses.html', {
        'users': users
    })

@login_required
@user_passes_test(is_organizer)
def evaluate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    try:
        transport_guess = TransportGuess.objects.get(user=user)
        map_guess = MapGuess.objects.get(user=user)
        evaluation = GameEvaluation.objects.filter(user=user).first()
    except (TransportGuess.DoesNotExist, MapGuess.DoesNotExist):
        messages.error(request, 'Cet utilisateur n\'a pas participé aux deux jeux.')
        return redirect('evaluate_responses')
    
    if request.method == 'POST':
        # Mettre à jour les évaluations individuelles
        transport_guess.is_verified = request.POST.get('transport_correct') == 'true'
        transport_guess.score = int(request.POST.get('transport_score', 0))
        transport_guess.feedback = request.POST.get('transport_feedback', '')
        transport_guess.save()
        
        map_guess.is_correct = request.POST.get('map_correct') == 'true'
        map_guess.score = int(request.POST.get('map_score', 0))
        map_guess.distance_to_target = float(request.POST.get('distance_to_target', 0))
        map_guess.feedback = request.POST.get('map_feedback', '')
        map_guess.save()
        
        # Créer ou mettre à jour l'évaluation globale
        evaluation, created = GameEvaluation.objects.update_or_create(
            user=user,
            defaults={
                'evaluated_by': request.user,
                'feedback': request.POST.get('global_feedback', '')
            }
        )
        
        messages.success(request, f'Les réponses de {user.username} ont été évaluées avec succès.')
        return redirect('evaluate_responses')
    
    return render(request, 'games/evaluate_user.html', {
        'user': user,
        'transport_guess': transport_guess,
        'map_guess': map_guess,
        'evaluation': evaluation
    })

def logout_view(request):
    logout(request)
    return redirect('users_home')


def tempo_view(request):
    # Récupérer les réponses de l'utilisateur
    transport_guess = TransportGuess.objects.filter(user=request.user).first()
    map_guess = MapGuess.objects.filter(user=request.user).first()

    # Récupérer le classement
    leaderboard = []
    # Exclure les utilisateurs du groupe Technicien
    users = User.objects.exclude(groups__name='Technicien')
    for user in users:
        transport_guess_user = TransportGuess.objects.filter(user=user).first()
        map_guess_user = MapGuess.objects.filter(user=user).first()

        # Calculer le score total
        transport_score = transport_guess_user.score if transport_guess_user and transport_guess_user.score is not None else 0
        map_score = map_guess_user.score if map_guess_user and map_guess_user.score is not None else 0
        total_score = transport_score + map_score

        leaderboard.append({
            'username': user.username,
            'first_name': user.first_name,
            'total_score': total_score,
            'is_current_user': user == request.user
        })

    # Trier le classement par score décroissant
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)

    # Si l'utilisateur est un organisateur, ajouter les données supplémentaires
    if is_organizer(request.user):
        # Récupérer tous les utilisateurs qui ont participé (exclure les techniciens)
        all_users = User.objects.exclude(groups__name='Technicien').filter(
            transportguess__isnull=False,
            mapguess__isnull=False
        ).distinct()

        # Récupérer toutes les réponses pour l'évaluation
        all_responses = []
        for user in all_users:
            transport_guess = TransportGuess.objects.filter(user=user).first()
            map_guess = MapGuess.objects.filter(user=user).first()
            evaluation = GameEvaluation.objects.filter(user=user).first()

            all_responses.append({
                'user': user,
                'transport_guess': transport_guess,
                'map_guess': map_guess,
                'evaluation': evaluation
            })

        return render(request, 'games/tempo.html', {
            'transport_guess': transport_guess,
            'map_guess': map_guess,
            'leaderboard': leaderboard,
            'is_organizer': True,
            'all_responses': all_responses
        })

    # Pour les utilisateurs normaux, retourner uniquement leurs réponses et le classement
    return render(request, 'games/tempo.html', {
        'transport_guess': transport_guess,
        'map_guess': map_guess,
        'leaderboard': leaderboard,
        'is_organizer': False
    })

@login_required
def all_responses(request):
    # Vérifier si l'utilisateur est un organisateur
    if not request.user.groups.filter(name='Organisateur').exists():
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('home')
    
    # Récupérer toutes les réponses avec les informations nécessaires
    all_responses = []
    users = User.objects.all()
    
    for user in users:
        transport_guess = TransportGuess.objects.filter(user=user).first()
        map_guess = MapGuess.objects.filter(user=user).first()
        
        if transport_guess or map_guess:
            total_score = 0
            if transport_guess and transport_guess.is_verified:
                total_score += transport_guess.score
            if map_guess and map_guess.is_correct:
                total_score += map_guess.score
                
            all_responses.append({
                'user': user,
                'transport_guess': transport_guess,
                'map_guess': map_guess,
                'total_score': total_score
            })
    
    # Trier les réponses par score total décroissant
    all_responses.sort(key=lambda x: x['total_score'], reverse=True)
    
    context = {
        'all_responses': all_responses
    }
    return render(request, 'games/all_responses.html', context)