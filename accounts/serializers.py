from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        # Проверяем что пароли совпадают
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password_confirm': 'Пароли не совпадают'}
            )

        # Проверяем что username не занят
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким именем уже существует'}
            )

        return data

    def create(self, validated_data):
        # Удаляем password_confirm перед созданием
        validated_data.pop('password_confirm')

        # Создаём пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # Создаём токен для автоматического входа
        Token.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate

        user = authenticate(
            username=data['username'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError(
                {'error': 'Неверное имя пользователя или пароль'}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'error': 'Аккаунт деактивирован'}
            )

        # Получаем или создаём токен
        token, _ = Token.objects.get_or_create(user=user)

        return {
            'user': user,
            'token': token.key,
            'username': user.username,
            'email': user.email
        }


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']