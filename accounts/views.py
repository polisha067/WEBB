from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .openapi import REGISTER_SCHEMA, LOGIN_SCHEMA, LOGOUT_SCHEMA, ME_SCHEMA


@REGISTER_SCHEMA
class RegisterViewSet(viewsets.GenericViewSet):
    """
    Регистрация нового пользователя
    POST /api/accounts/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = Token.objects.get(user=user)

        return Response({
            'status': 'success',
            'message': 'Пользователь успешно зарегистрирован',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


@LOGIN_SCHEMA
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Вход пользователя
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    validated_data = serializer.validated_data

    return Response({
        'status': 'success',
        'message': 'Вход выполнен успешно',
        'user': {
            'username': validated_data['username'],
            'email': validated_data['email']
        },
        'token': validated_data['token']
    })


@LOGOUT_SCHEMA
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Выход пользователя (удаление токена)
    POST /api/accounts/logout/
    """
    request.user.auth_token.delete()

    return Response({
        'status': 'success',
        'message': 'Выход выполнен успешно'
    })


@ME_SCHEMA
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    """
    Получить данные текущего пользователя
    GET /api/accounts/me/
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
