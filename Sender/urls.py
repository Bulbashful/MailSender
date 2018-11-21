from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


from . import views

urlpatterns = [
    # Home pages
    path('', views.HomePage.as_view(), name='home'),
    path('home/', views.HomePage.as_view(), name='home'),

    # user account
    path('account-settings/', views.AccountSettings.as_view(), name='account-settings'),
    path('change-password/', views.ChangePassword.as_view(), name='change-password'),

    # user messages
    path('campaigns/', views.SendEmail.as_view(), name='campaigns'),
    # view user sended messages by ID
    path('view-email/id-<int:mail_id>/', views.SendEmailView.as_view(), name='view-email'),
    # view message send results
    path('result-emails/', views.SendEmailResults.as_view(), name='send-email-result'),
    # view message send results by tag
    path('result-emails/tag-<str:tag>/', views.SendEmailResults.as_view(), name='send-email-result'),

    # Account activation
    path('activation/<int:id>/<slug:activation_string>/', views.MailVerify.as_view(), name='account_activation'),

    # Login, logout and registration
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('registration/', views.RegistrationPage.as_view(), name='registration'),

    # Password reset
    path('password-reset/', views.PasswordRecovery.as_view(), name='password_reset'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
