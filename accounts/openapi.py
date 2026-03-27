from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


REGISTER_SCHEMA = extend_schema(
    tags=['Accounts'],
    examples=[
        OpenApiExample(
            'Register User',
            value={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'strongpassword123',
                'password_confirm': 'strongpassword123'
            },
            request_only=True
        )
    ]
)


LOGIN_SCHEMA = extend_schema(
    tags=['Accounts'],
    examples=[
        OpenApiExample(
            'Login',
            value={
                'username': 'testuser',
                'password': 'strongpassword123'
            },
            request_only=True
        )
    ]
)


LOGOUT_SCHEMA = extend_schema(tags=['Accounts'])


ME_SCHEMA = extend_schema(tags=['Accounts'])
