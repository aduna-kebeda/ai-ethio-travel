from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models.user_feedback import UserFeedback
from ..serializers import UserFeedbackSerializer

class UserFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = UserFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFeedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 