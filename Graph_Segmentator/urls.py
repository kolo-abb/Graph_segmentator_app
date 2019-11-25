"""erteterter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from segmentation_app import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^segmentation/', views.segmentation, name='segmentation'),
    url(r'^tracking/', views.tracking, name='tracking'),
    url(r'^mst/', views.mst, name='mst'),
    url(r'^mst_additional/', views.mst_additional, name='mst_additional'),
    url(r'^two_cc/', views.two_cc, name='two_cc'),
    url(r'^ngc/', views.ngc, name='ngc'),
    url(r'^interactive/', views.interactive, name='interactive'),
    url(r'^choose_alg/', views.choose_alg, name='choose_alg'),
    url(r'^algorithms_desc/', views.algorithms_desc, name='algorithms_desc'),
    url(r'^mst_desc/', views.mst_desc, name='mst_desc'),
    url(r'^gft_desc/', views.gft_desc, name='gft_desc'),
    url(r'^ngc_desc/', views.ngc_desc, name='ngc_desc'),
    url(r'^two_cc_desc/', views.two_cc_desc, name='two_cc_desc'),
    url(r'^interactive_desc/', views.interactive_desc, name='interactive_desc'),
    url(r'^save_mst/', views.save_mst, name='save_mst'),
    url(r'^save_ngc/', views.save_ngc, name='save_ngc'),
    url(r'^save_two_cc/', views.save_two_cc, name='save_two_cc'),
    url(r'^save_interactive/', views.save_interactive, name='save_interactive'),
    url(r'^save_video/', views.save_video, name='save_video'),
    url(r'^load_segmentation/', views.load_segmentation, name='load_segmentation'),
    url(r'^load_tracking/', views.load_tracking, name='load_tracking'),
    url(r'^choose_alg_tracking/', views.choose_alg_tracking, name='choose_alg_tracking'),
    url(r'^multi_tracking_desc/', views.multi_tracking_desc, name='multi_tracking_desc'),
    # url(r'^two_cc_track/', views.two_cc_track, name='two_cc_track'),
    # url(r'^mst_track/', views.mst_track, name='mst_track'),
    # url(r'^ngc_track/', views.ngc_track, name='ngc_track'),
    # url(r'^simple_tr_track/', views.simple_tr_track, name='simple_tr_track'),
]

urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
