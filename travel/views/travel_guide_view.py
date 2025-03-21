from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models.travel_guide import TravelGuide
from ..serializers import TravelGuideSerializer

class TravelGuideViewSet(viewsets.ModelViewSet):
    queryset = TravelGuide.objects.all()
    serializer_class = TravelGuideSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Remove 'destination' from filterset_fields if it doesn't exist in the model
    filterset_fields = []
    search_fields = ['title', 'content']
    ordering_fields = ['published_date']

    def perform_create(self, serializer):
        travel_guide = serializer.save(author=self.request.user)
        travel_guide.update_weather_info()

    def perform_update(self, serializer):
        travel_guide = serializer.save()
        travel_guide.update_weather_info()