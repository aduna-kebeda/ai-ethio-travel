from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ..models.travel_history import TravelHistory
from ..serializers import TravelHistorySerializer

class TravelHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = TravelHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['destination']
    ordering_fields = ['start_date', 'created_at']

    def get_queryset(self):
        return TravelHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 