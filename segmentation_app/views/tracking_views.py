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

available_segmentation_methods = ['two_cc', 'simple_threshold', 'watershed']
available_tracking_algorithms = ['local_tracking', 'active_colloids_tracking']

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
        tracking_algorithm = request.POST.get("tracking_algorithm")

        segmentation_method = request.POST.get("segmentation_method")

        if segmentation_method not in available_segmentation_methods:
            return HttpResponseForbidden('Invalid segmentation method.')
        
        if tracking_algorithm not in available_tracking_algorithms:
            return HttpResponseForbidden('Invalid tracking algorithm')

        n_frames = int(request.POST.get("n_frames"))

        a = int(request.POST.get("a"))
        b = int(request.POST.get("b"))
        c = int(request.POST.get("c"))
        d = int(request.POST.get("d"))
        
        video = cv2.VideoCapture('static/media/temp_video.mp4')
        frames = main_api.prepare_frames(video, n_frames, (a, b, c, d))

        if tracking_algorithm == "local_tracking":
            video_out = main_api.tracking_local(frames, segmentation_method)
        elif tracking_algorithm == 'active_colloids_tracking':
            video_out = main_api.active_colloids_tracking(frames, segmentation_method)
            
        context['video_out'] = '/' + video_out
        return render(request, 'local_video.html', context)

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')


def mst_track(request):
    name = context['name']
    n_frames = context['n_frames']
    a = context['a']
    b = context['b']
    c = context['c']
    d = context['d']
    if request.method == 'POST':
        params = {
            'Edges': request.POST.get("Edges"),
            'Threshold': int(request.POST.get("Threshold")),
            'Const': int(request.POST.get("Const")),
            'Min_size': int(request.POST.get("Min_size"))
        }

        if name == "local tracking":
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.tracking_local(video,n_frames,(a,b,c,d), 'mst', params)
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        elif name == 'active colloids tracking':
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.active_colloids_tracking(video, n_frames, (a,b,c,d), 'mst', params)
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')


def ngc_track(request):
    name = context['name']
    n_frames = context['n_frames']
    a = context['a']
    b = context['b']
    c = context['c']
    d = context['d']
    if request.method == 'POST':
        params = {
            'Algorithm_type': int(request.POST.get("Algorithm_type")),
            'Intensivity': int(request.POST.get("Intensivity")),
            'Distance': int(request.POST.get("Distance"))
        }

        if name == "local tracking":
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.tracking_local(video,n_frames,(a,b,c,d), 'ngc', params)
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        elif name == 'active colloids tracking':
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.active_colloids_tracking(video, n_frames, (a,b,c,d), 'ngc', params)
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!')


def simple_tr_track(request):
    name = context['name']
    n_frames = context['n_frames']
    a = context['a']
    b = context['b']
    c = context['c']
    d = context['d']
    if request.method == 'POST':
        params = {
            'Treshold': int(request.POST.get("Treshold"))
        }

        if name == "local tracking":
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.tracking_local(video,n_frames,(a,b,c,d), 'simple_tr', params)
            context['video_out'] = '/' + video_out
            return render(request, 'local_video.html', context)
        elif name == 'active colloids tracking':
            video = cv2.VideoCapture('static/media/temp_video.mp4')
            video_out = main_api.active_colloids_tracking(video, n_frames, (a,b,c,d), 'simple_tr', params)
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

def load_tracking(request):
    if request.method == 'POST':
        context.clear()
        name = request.POST.get("tracking")
        name=name.split(':')[0]
        print(name)
        all_info=connector.load_tracking(name)

        context['video_out'] = all_info['tracking_name']
        context['video'] = all_info['base_name']
        context['description'] = all_info['description']
        context['name'] = name
        return render(request, 'local_video.html', context)

    return render(request, 'load_segmentation.html', context)
