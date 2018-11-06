from django.conf.urls import url, include


from django.contrib import admin
urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^', include('Sender.urls')),
]
