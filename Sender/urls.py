from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # Home pages
    url(r'^home/', views.HomePage.as_view(), name='home'),
    url(r'^$', views.HomePage.as_view(), name='home'),

    # Account activation
    url(r'^activation/(?P<id>[0-9]+)/(?P<activation_string>\w+)/$', views.MailVerify.as_view(), name='account_activation'),

    # Login, logout and registration
    url(r'^login/', views.LoginPage.as_view(), name='login'),
    url(r'^logout/', views.Logout.as_view(), name='logout'),
    url(r'^registration/', views.RegistrationPage.as_view(), name='registration'),

    # Password reset
    url(r'^password-reset/', views.PasswordRecovery.as_view(), name='password_reset'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
