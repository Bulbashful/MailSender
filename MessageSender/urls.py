from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings


from django.contrib import admin
urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^', include('Sender.urls')),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)