from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    PublicUserSerializer,
    PasswordSerializer
)
from .permissions import IsSelfOrAdmin, IsAdminUser

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSelfOrAdmin]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['GET'], permission_classes=[IsAdminUser])
    def admins(self, request):
        admins = User.objects.filter(role=User.Role.ADMIN)
        serializer = self.get_serializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAdminUser])
    def instructors(self, request):
        instructors = User.objects.filter(role=User.Role.INSTRUCTOR)
        serializer = self.get_serializer(instructors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[IsSelfOrAdmin])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'status': 'password set'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = serializer.save()
        password = self.request.data.get('password')
        if password:
            user.set_password(password)
            user.save()

    def perform_update(self, serializer):
        if not self.request.user.is_admin:
            serializer.validated_data.pop('role', None)
        serializer.save()


class PublicProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    lookup_field = 'username'

    @action(detail=True, methods=['GET'])
    def courses(self, request, username=None):
        user = get_object_or_404(User, username=username)
        return Response({
            'username': user.username,
            'courses': []
        })
