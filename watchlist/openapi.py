from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


WATCHLIST_SCHEMA = extend_schema(
    tags=['Watchlist'],
    parameters=[
        OpenApiParameter('status', str, OpenApiParameter.QUERY, description='Фильтр по статусу: want_to_watch, watching, watched'),
        OpenApiParameter('search', str, OpenApiParameter.QUERY, description='Поиск по названию фильма'),
        OpenApiParameter('ordering', str, OpenApiParameter.QUERY, description='Сортировка: added_at, movie__title'),
    ],
    examples=[
        OpenApiExample(
            'Add to Watchlist',
            value={
                'movie': 1,
                'status': 'want_to_watch'
            },
            request_only=True
        )
    ]
)
