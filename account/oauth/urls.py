from django.urls import path
from .views import OauthView, CallbackView

urlpatterns = [
    path('login', OauthView.as_view(), name='oauth_login'),
    path('callback', CallbackView.as_view(), name='oauth_callback'),
]
