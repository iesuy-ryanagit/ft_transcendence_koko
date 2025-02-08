app_name = "user"
from django.urls import path
from .views import CustomLoginView, LogoutView, SetupOTPView, SignUpView, VerifyOTPView

app_name = "user"
urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("setup-otp/", SetupOTPView.as_view(), name="setup_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
