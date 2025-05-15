from django.urls import path
from .views import UserProfileView, UserListView

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('', UserListView.as_view(), name='user-list'),  # This is for listing users
]