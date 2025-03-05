app_name = "user"
from django.urls import path
from .views import SignupView, LoginView, LogoutView, ProfileView, SetupTFAView,LoginTFAView, UpdateUserSettingsView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('setup-tfa/', SetupTFAView.as_view(), name='signup-tfa'),
    path('login-tfa/', LoginTFAView.as_view(), name='login-tfa'),
    path('setup-game/', UpdateUserSettingsView.as_view(),name='setup-game'),
]