from django.urls import path
from .views import SendCompletionEmail,RequestPaymentEmail, ChangePasswordView, PasswordTokenCheckAPI, RegisterAdminAPI, RequestPasswordResetEmail, SetNewPasswordAPIView,UpdateUserProfileAPI,BlacklistTokenUpdateView,UserProfileAPI

app_name = 'users'

urlpatterns = [
    path('profile/', UserProfileAPI.as_view(), name="user"),
    path('profile/update/', UpdateUserProfileAPI.as_view(), name="updateprofile"),
    path('changepassword/', ChangePasswordView.as_view(), name="changepassword"),
    path('register/admin/', RegisterAdminAPI.as_view(), name="register_admin"),
    path('logout/blacklist/', BlacklistTokenUpdateView.as_view(), name="blacklist"),
    path('request-reset-password/', RequestPasswordResetEmail.as_view(),
         name="request-reset-password"),
    path('password-reset-validation/<uidb64>/<token>/',
         PasswordTokenCheckAPI.as_view(),name='password-reset-validation'),
    path('setpassword/',SetNewPasswordAPIView.as_view(),
         name='setpassword'),

     path('request-payment/',RequestPaymentEmail.as_view(),
         name='request-payment'),
     
     path('send-completion-email/', SendCompletionEmail.as_view(), name='send-completion-email'),
]