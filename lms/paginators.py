from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 5                     # Количество элементов на одной странице по умолчанию
    page_size_query_param = 'page_size' # Позволяет клиенту задать свой размер страницы (например, ?page_size=10)
    max_page_size = 50                # Максимально разрешенный размер страницы
