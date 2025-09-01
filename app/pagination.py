from rest_framework.pagination import PageNumberPagination

class ProductPageNumberPagination(PageNumberPagination):
    
    page_size_query_param = "size"