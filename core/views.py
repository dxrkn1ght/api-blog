from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.models import Follow
from users.models import Profile
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
            return Response({"error": "O'zingizni kuzatolmaysiz."}, status=400)

        if not Follow.objects.filter(user=user_profile, followed_user=target_profile).exists():
            Follow.objects.create(user=user_profile, followed_user=target_profile)
            return Response({"status": "followed"})
        else:
            return Response({"status": "already following"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def unfollow(self, request, pk=None):
        target_profile = self.get_object()
        user_profile = getattr(request.user, 'profile', None)

        if user_profile is None:
            return Response({"error": "Sizning profilingiz mavjud emas."}, status=status.HTTP_403_FORBIDDEN)

        if target_profile == user_profile:
            return Response({"error": "O'zingizni kuzatolmaysiz."}, status=400)

        follow_record = Follow.objects.filter(user=user_profile, followed_user=target_profile).first()
        if follow_record:
            follow_record.delete()
            return Response({"status": "unfollowed"})
        return Response({"status": "not following"}, status=status.HTTP_400_BAD_REQUEST)
