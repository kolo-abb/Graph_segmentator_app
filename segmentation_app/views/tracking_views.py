import numpy as np
from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
import django
import io
import cv2

from Graph_Segmentator.settings import BASE_DIR
from segmentator import main_api as seg
from segmentation_app import connector
from segmentation_app.utils import convertToBinaryData


# Create your views here.
from django.views.decorators.csrf import ensure_csrf_cookie

from segmentator.mst_algorithms import threshold_mst_1, threshold_mst_2, threshold_mst_3
from segmentation_app.views.segmentation_views import context
from tracker import main_api


def tracking(request):
    if request.method == 'POST':
        context.clear()
        uploaded_file = request.FILES.get('video')
        fs = FileSystemStorage(base_url=BASE_DIR + '/static/media/')
        if (uploaded_file is None):
            return render(request, 'tracking.html', context)
        name = uploaded_file.name
        # uploaded_file=cv2.VideoCapture(uploaded_file.read())
        # print(uploaded_file)
        file = open('static/media/temp_video.mp4', 'wb')
        file.write(uploaded_file.read())
        file.close()
        context['video'] = '/static/media/temp_video.mp4'

    return render(request, 'tracking.html', context)


@ensure_csrf_cookie
def choose_alg_tracking(request):
    if request.method == 'POST':
        name = request.POST.get("algos")
        n_frames = int(request.POST.get("n_frames"))
        a = int(request.POST.get("a"))
        b = int(request.POST.get("b"))
        c = int(request.POST.get("c"))
        d = int(request.POST.get("d"))
        if name == "local tracking": ## local, poprawic
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.tracking_local(video,n_frames,(a,b,c,d))
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        elif name == 'active colloids tracking':
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.active_colloids_tracking(video, n_frames, (a,b,c,d))
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')


def gft_desc(request):
    return render(request, 'gft_desc.html')

def multi_tracking_desc(request):
    return render(request, 'multi_tracking_desc.html')

def save_video(request):
    video_base = convertToBinaryData('static/media/temp_video.mp4')
    video_out = convertToBinaryData(BASE_DIR + context['video_out'])
    name = request.POST.get("Name")
    description = request.POST.get("Description")

    connector.save_video(video_base,video_out,name,description)
    return render(request, 'home.html')
