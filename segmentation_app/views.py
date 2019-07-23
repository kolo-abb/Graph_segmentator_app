from PIL import Image
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render

from segmentator import main_api as seg


# Create your views here.
from django.views.decorators.csrf import ensure_csrf_cookie

context = {}


def home(request):
    context.clear()
    return render(request, 'home.html')


def segmentation(request):
    if request.method == 'POST':
        context.clear()
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['image'] = fs.url(name)
    return render(request, 'segmentation.html', context)


def tracking(request):
    return render(request, 'home.html')


def mst(request):
    print(context)
    if request.method == 'POST':

        edges8=request.POST.get("Edges")
        const=float(request.POST.get("Const"))
        min_size=int(request.POST.get("Min_size"))

        result= seg.mst_1const(Image.open(context['image']), edges_8=edges8,
                                            const=const,min_size=min_size)
        result[0].save('static/media/temporary.png')
        context['segmented_image'] = "/static/media/temporary.png"
        context['counter'] = result[1]
    return render(request, 'mst.html', context)


@ensure_csrf_cookie
def choose_alg(request):
    if request.method == 'POST':
        name = request.POST.get("algos")
        if(name == "mst"):
            return render(request, 'mst.html', context)
        else:
            return HttpResponseForbidden('Something is wrong, check if you filled all required positions!2')

    return HttpResponseForbidden('Something is wrong, check if you filled all required positions!1')




