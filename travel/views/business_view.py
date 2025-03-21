from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models.business import Business
from ..serializers import BusinessSerializer

class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['business_type', 'is_verified']  # Ensure these are valid model fields
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['name', 'is_verified']