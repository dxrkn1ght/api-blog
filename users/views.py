from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Profile
from .serializers import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').prefetch_related('following', 'followers')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        user_profile = getattr(self.request.user, 'profile', None)
        if user_profile is None:
            return Response({"error": "Sizning profilingiz mavjud emas."}, status=status.HTTP_403_FORBIDDEN)
        if user_profile != self.get_object():
            return Response({"error": "Siz faqat o'z profilingizni o'zgartira olasiz."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def follow(self, request, pk=None):
        target_profile = self.get_object()
        user_profile = getattr(request.user, 'profile', None)

        if user_profile is None:
            return Response({"error": "Sizning profilingiz mavjud emas."}, status=status.HTTP_403_FORBIDDEN)

        if target_profile == user_profile:
            return Response({"error": "O'zingizni kuzatolmaysiz."}, status=status.HTTP_400_BAD_REQUEST)

        if target_profile in user_profile.following.all():
            user_profile.following.remove(target_profile)
            return Response({"status": "unfollowed"})
        else:
            user_profile.following.add(target_profile)
            return Response({"status": "followed"})
