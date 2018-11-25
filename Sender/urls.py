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

    # user campaigns
    path('campaigns/', views.CampaignsListView.as_view(), name='campaigns'),
    # view campaigns by tag
    path('campaigns/tag-<str:tag>/', views.CampaignsListView.as_view(), name='campaigns-tag'),
        
    # view campaigns list
    path('saved-campaigns/', views.SavedCampaignsListView.as_view(), name='campaigns-saved'),
    # view campaigns by tag
    path('saved-campaigns/tag-<str:tag>/', views.SavedCampaignsListView.as_view(), name='campaigns-saved-tag'),

    # view user campaigns by ID
    path('view-campaign/id-<int:campaign_id>/', views.CampaignDetailView.as_view(), name='view-campaign'),

    # Account activation
    path('activation/<int:id>/<slug:activation_string>/', views.MailVerify.as_view(), name='account_activation'),


    # Login, logout and registration
    path('login/', views.LoginPage.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('registration/', views.RegistrationPage.as_view(), name='registration'),

    # Password reset
    path('password-reset/', views.PasswordRecovery.as_view(), name='password_reset'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
