from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from .models import MapGuess, TransportGuess
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.urls import reverse
from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST

def is_organizer(user):
    return user.is_staff or user.groups.filter(name='Organisateur').exists()

@login_required
def game_home(request):
    return render(request, 'games/game_home.html')

@login_required
def poll(request):
    # Vérifier si l'utilisateur a déjà répondu
    guess = TransportGuess.objects.filter(user=request.user).first()
    has_responded = guess is not None
    can_modify = has_responded and not guess.is_verified if guess else True
    want_to_modify = request.GET.get('modify') == 'true'
    
    if request.method == 'POST':
        # Vérifier si la modification est autorisée
        if has_responded and guess.is_verified:
            messages.error(request, "Vous ne pouvez plus modifier votre réponse car elle a été validée par l'administrateur.")
            return redirect('poll')
            
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
    # Vérifier si l'utilisateur a déjà répondu
    guess = MapGuess.objects.filter(user=request.user).first()
    has_responded = guess is not None
    can_modify = has_responded and not guess.is_verified if guess else True
    want_to_modify = request.GET.get('modify') == 'true'
    
    if request.method == 'POST':
        # Vérifier si la modification est autorisée
        if has_responded and guess.is_verified:
            messages.error(request, "Vous ne pouvez plus modifier votre réponse car elle a été validée par l'administrateur.")
            return redirect('map_guess')
            
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
        map_guess_user = MapGuess.objects.filter(user=user).first()
        
        # Utiliser le total_score de MapGuess
        total_score = map_guess_user.total_score if map_guess_user and map_guess_user.is_verified else 0
        
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
            
            all_responses.append({
                'user': user,
                'transport_guess': transport_guess,
                'map_guess': map_guess,
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

def logout_view(request):
    logout(request)
    return redirect('users_home')

@login_required
@user_passes_test(is_organizer)
def all_responses(request):
    # Vérifier si l'utilisateur est un organisateur
    if not request.user.groups.filter(name='Organisateur').exists():
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('home')
    
    # Gérer la soumission du formulaire
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        try:
            transport_guess = TransportGuess.objects.get(user=user)
            map_guess = MapGuess.objects.get(user=user)
            
            # Récupérer le score total
            total_score = int(request.POST.get('total_score', 0))
            
            # Mettre à jour TransportGuess
            transport_guess.is_verified = request.POST.get('transport_verified') == 'on'
            transport_guess.total_score = total_score
            transport_guess.save()
            
            # Mettre à jour MapGuess
            map_guess.is_verified = request.POST.get('city_verified') == 'on'
            map_guess.total_score = total_score
            map_guess.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Évaluation enregistrée avec succès',
                'total_score': total_score
            })
            
        except (TransportGuess.DoesNotExist, MapGuess.DoesNotExist):
            return JsonResponse({
                'success': False,
                'message': 'Réponses non trouvées pour cet utilisateur'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # Affichage normal de la page (GET request)
    all_responses = []
    users = User.objects.all()
    
    for user in users:
        transport_guess = TransportGuess.objects.filter(user=user).first()
        map_guess = MapGuess.objects.filter(user=user).first()

        if transport_guess or map_guess:
            total_score = 0
            if transport_guess and transport_guess.is_verified:
                total_score = transport_guess.total_score
            elif map_guess and map_guess.is_verified:
                total_score = map_guess.total_score
                
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


@login_required
@user_passes_test(is_organizer)
def evaluate_response(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        transport_guess = TransportGuess.objects.get(user=user)
        map_guess = MapGuess.objects.get(user=user)
        
        # Calculer le score total
        total_score = int(request.POST.get('total_score', 0))
        
        # Répartir le score total entre transport et ville
        transport_score = total_score // 2
        map_score = total_score - transport_score
        
        # Mettre à jour TransportGuess
        transport_guess.is_verified = request.POST.get('transport_verified') == 'on'
        transport_guess.score = transport_score
        transport_guess.save()
        
        # Mettre à jour MapGuess
        map_guess.is_verified = request.POST.get('city_verified') == 'on'
        map_guess.is_correct = request.POST.get('city_verified') == 'on'
        map_guess.score = map_score
        map_guess.save()

        
        return JsonResponse({
            'success': True,
            'message': 'Évaluation enregistrée avec succès',
            'transport_score': transport_score,
            'map_score': map_score,
            'total_score': total_score
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    }, status=405)

@login_required
@require_POST
def delete_response(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'success': False, 'message': 'ID utilisateur manquant'})
        
        # Vérifier si l'utilisateur est un organisateur
        if not request.user.groups.filter(name='Organisateur').exists():
            return JsonResponse({'success': False, 'message': 'Permission refusée'})
        
        # Récupérer et supprimer les réponses
        transport_guess = TransportGuess.objects.filter(user_id=user_id).first()
        map_guess = MapGuess.objects.filter(user_id=user_id).first()
        
        if transport_guess:
            transport_guess.delete()
        if map_guess:
            map_guess.delete()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
