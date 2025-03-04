from django.urls import path
from .views import OauthUrlView, OauthLoginView

urlpatterns = [
    path('url42/', OauthUrlView.as_view(), name='oauth_url'),
    path('login42/', OauthLoginView.as_view(), name='oauth_login'),
]
