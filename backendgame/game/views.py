from rest_framework import generics, permissions
from .models import GameSetting
from .serializers import GameSettingSerializer, GameSettingUpdateSerializer

class GameSettingView(generics.RetrieveUpdateAPIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = GameSetting.objects.get_or_create(user=self.request.user)
        return obj
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return GameSettingUpdateSerializer
        return GameSettingSerializer
