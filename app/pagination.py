from rest_framework.pagination import PageNumberPagination


class LMSPageNumberPagination(PageNumberPagination):
    """Custom pagination for the LMS API."""
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100