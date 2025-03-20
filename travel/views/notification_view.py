from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models.notification_setting import NotificationSetting
from ..serializers import NotificationSettingSerializer

class NotificationSettingViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationSetting.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 