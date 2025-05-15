from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # By default, only staff or admin users can see the list of all users
        if self.request.user.is_staff or self.request.user.role == 'admin':
            return User.objects.all().order_by('id')
        # Regular users can only see themselves and possibly other related users
        return User.objects.filter(id=self.request.user.id)