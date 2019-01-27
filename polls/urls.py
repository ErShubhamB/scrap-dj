from django.urls import path
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    url('^login', views.login, name='login'),
    url('^$', views.index, name='index'),
    url('^hotel', views.hotel, name='hotel'),
    url('user_login', views.user_login, name='user_login'),
    url('data_fetch', views.data_fetch, name='data_fetch'),
    url('scrap_list', views.hotel_scrap, name='hotel_scrap'),
    url('^logout', views.logout, name='logout'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)