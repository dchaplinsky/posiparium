from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views

urlpatterns = [
    url(r'^ajax/suggest$', core_views.suggest, name='suggest'),
    url(r'^$', core_views.home, name='home'),
    url(r'^(?P<county_slug>\w+)$', core_views.county, name='county'),

    url(r'^admin/', admin.site.urls),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
