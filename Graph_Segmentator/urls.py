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
    url(r'^ball_ngc/', views.ball_ngc, name='ball_ngc'),
    url(r'^choose_ngc/', views.choose_ngc, name='choose_ngc'),
    url(r'^interactive/', views.interactive, name='interactive'),
    url(r'^choose_alg/', views.choose_alg, name='choose_alg'),
    url(r'^algorithms_desc/', views.algorithms_desc, name='algorithms_desc'),
    url(r'^mst_desc/', views.mst_desc, name='mst_desc'),
    url(r'^ngc_desc/', views.ngc_desc, name='ngc_desc'),
    url(r'^two_cc_desc/', views.two_cc_desc, name='two_cc_desc'),
    url(r'^interactive_desc/', views.interactive_desc, name='interactive_desc'),
    url(r'^save_mst/', views.save_mst, name='save_mst'),
    url(r'^save_ngc/', views.save_ngc, name='save_ngc'),
    url(r'^save_ball_ngc/', views.save_ball_ngc, name='save_ball_ngc'),
    url(r'^save_two_cc/', views.save_two_cc, name='save_two_cc'),
    url(r'^save_interactive/', views.save_interactive, name='save_interactive'),
    url(r'^load_segmentation/', views.load_segmentation, name='load_segmentation'),
]

urlpatterns+=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
