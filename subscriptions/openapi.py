from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


SUBSCRIPTION_SCHEMA = extend_schema(
    tags=['Subscriptions'],
    parameters=[
        OpenApiParameter('search', str, OpenApiParameter.QUERY, description='Поиск по названию тарифа'),
        OpenApiParameter('ordering', str, OpenApiParameter.QUERY, description='Сортировка: price, duration_days'),
    ]
)


USER_SUBSCRIPTION_SCHEMA = extend_schema(
    tags=['Subscriptions'],
    parameters=[
        OpenApiParameter('status', str, OpenApiParameter.QUERY, description='Фильтр по статусу: active, expired, cancelled'),
    ],
    examples=[
        OpenApiExample(
            'Buy Subscription',
            value={'subscription': 1},
            request_only=True
        )
    ]
)
