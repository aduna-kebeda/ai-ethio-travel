from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models.travel_guide import TravelGuide
from ..serializers import TravelGuideSerializer

class TravelGuideViewSet(viewsets.ModelViewSet):
    queryset = TravelGuide.objects.all()
    serializer_class = TravelGuideSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination']
    search_fields = ['title', 'content']
    ordering_fields = ['published_date']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 