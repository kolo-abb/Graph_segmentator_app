from PIL import Image
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from segmentator import main_api as seg


# Create your views here.
from django.views.decorators.csrf import ensure_csrf_cookie

from segmentation_app.forms import ImageUploadForm


def home(request):
    return render(request, 'home.html')

def segmentation(request):
    return render(request, 'segmentation.html')

def tracking(request):
    return render(request, 'home.html')


def mst(request):
    return render(request, 'home.html')

@ensure_csrf_cookie
def upload_pic(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = Image.open(request.FILES['image'])
            result= seg.mst_count_1const(image)
            return HttpResponse('object number: '+str(result))
            return HttpResponse(request.FILES['image'])
    return HttpResponseForbidden('allowed only via POST')

