from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash
from .models import User
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    UserCreateSerializer, ChangePasswordSerializer
)
from .permissions import IsAdmin, IsAdminOrManager


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Messages clairs selon la situation du compte
        username = request.data.get('username', '').strip()
        user = User.objects.filter(username__iexact=username).first()
        if user is None:
            return Response(
                {'detail': "Aucun compte n'existe avec cet identifiant. Contactez votre administrateur."},
                status=401)
        if not user.is_active:
            return Response(
                {'detail': "Votre compte a été désactivé. Contactez votre administrateur pour le réactiver."},
                status=401)
        try:
            response = super().post(request, *args, **kwargs)
            from apps.history.models import ActivityLog
            ActivityLog.objects.create(user=user, action='LOGIN', description=f'Connexion de {user.username}.')
            return response
        except Exception:
            return Response({'detail': 'Mot de passe incorrect. Veuillez réessayer.'}, status=401)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'list']:
            return [IsAdmin()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAdminOrManager()]
        return [IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        target = self.get_object()
        # Interdire de désactiver son propre compte (risque de verrouillage total)
        if target.id == request.user.id and str(request.data.get('is_active')).lower() in ('false', '0'):
            return Response({'error': 'Vous ne pouvez pas désactiver votre propre compte.'}, status=400)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_password(self, request, pk=None):
        """L'admin définit un nouveau mot de passe pour un utilisateur."""
        target = self.get_object()
        new_password = request.data.get('new_password', '')
        if len(new_password) < 6:
            return Response({'error': 'Le mot de passe doit faire au moins 6 caractères.'}, status=400)
        target.set_password(new_password)
        target.save()
        from apps.history.models import ActivityLog
        ActivityLog.objects.create(
            user=request.user, action='CREATE_USER',
            description=f"Réinitialisation du mot de passe de {target.username}.")
        return Response({'message': f'Mot de passe de {target.username} modifié avec succès.'})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Mot de passe actuel incorrect.'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès.'})

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie.'})
        except Exception:
            return Response({'error': 'Token invalide.'}, status=400)
