from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "NetOps Pro Hub — Administration"
admin.site.site_title = "NetOps Admin"
admin.site.index_title = "Gestion des procédures réseau"

handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('procedures/', include('procedures.urls')),
    path('concepts/', include('concepts.urls')),
    path('docs/', include('docs.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
