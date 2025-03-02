from django.urls import path
from .views import OauthUrlView, OauthLoginView

urlpatterns = [
    path('url-42', OauthUrlView.as_view(), name='oauth_url'),
    path('login-42', OauthLoginView.as_view(), name='oauth_login'),
]
