from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .services import AccountService
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

        data = serializer.validated_data
        user, token = AccountService.register(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password'],
            password_confirm=data['password_confirm'],
        )

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

    data = serializer.validated_data
    user, token = AccountService.login(
        username=data['username'],
        password=data['password'],
    )

    return Response({
        'status': 'success',
        'message': 'Вход выполнен успешно',
        'user': {
            'username': user.username,
            'email': user.email
        },
        'token': token.key
    })


@LOGOUT_SCHEMA
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Выход пользователя (удаление токена)
    POST /api/accounts/logout/
    """
    AccountService.logout(request.user)

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


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_user(request):
    """
    Проверка токена и возврат прав администратора/суперпользователя
    GET /api/accounts/verify/
    Authorization: Token <token>
    """
    user = request.user
    if not user.is_active:
        return Response(
            {'detail': 'Аккаунт деактивирован'},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'can_moderate': user.is_staff or user.is_superuser,
    })