from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


# Общие параметры для всех viewset
SEARCH_PARAM = OpenApiParameter('search', str, OpenApiParameter.QUERY, description='Поиск по названию и описанию')
ORDERING_PARAM = OpenApiParameter('ordering', str, OpenApiParameter.QUERY, description='Сортировка')


# Параметры для GenreViewSet
GENRE_SCHEMA = extend_schema(
    tags=['Movies'],
    parameters=[
        SEARCH_PARAM,
        OpenApiParameter('ordering', str, OpenApiParameter.QUERY, description='Сортировка: name, created_at'),
    ]
)


# Параметры для MovieViewSet
MOVIE_SCHEMA = extend_schema(
    tags=['Movies'],
    parameters=[
        OpenApiParameter('genres', int, OpenApiParameter.QUERY, description='Фильтр по ID жанра'),
        OpenApiParameter('release_year', int, OpenApiParameter.QUERY, description='Фильтр по году выпуска'),
        OpenApiParameter('rating', str, OpenApiParameter.QUERY, description='Фильтр по рейтингу'),
        SEARCH_PARAM,
        OpenApiParameter('ordering', str, OpenApiParameter.QUERY, description='Сортировка: title, release_year, rating'),
    ],
    examples=[
        OpenApiExample(
            'Create Movie',
            value={
                'title': 'Пример фильма',
                'description': 'Описание фильма',
                'duration': 120,
                'rating': 7.5,
                'release_year': 2024,
                'genre_ids': [1, 2],
                'poster': 'https://example.com/poster.jpg'
            },
            request_only=True
        )
    ]
)
