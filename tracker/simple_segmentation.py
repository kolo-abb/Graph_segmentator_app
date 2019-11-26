from skimage import measure
from PIL import Image, ImageFilter, ImageEnhance
from skimage import data, io, segmentation, color
from skimage.future import graph
import numpy as np
import cv2


def preparing_image(image, shape):
    # przy tym skalowaniu mozna dodac zeby do jakiegos konkretnego rozmiaru sie rzutowalo np 256 x scaled_y
    if (shape[1] > 700 or shape[0] > 700):
        scale_percent = 70 
        width = int(shape[0] * scale_percent / 100)
        height = int(shape[1] * scale_percent / 100)
        new_shape= (width, height)    
        scaled_image = image.resize(new_shape) 
    else:
        scaled_image = image
    enhanced_image = ImageEnhance.Contrast(scaled_image).enhance(1.2)
    enhanced_image = ImageEnhance.Brightness(enhanced_image).enhance(1.03)
    enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(0.96) 
#     image_arr = np.array(enhanced_image, dtype=np.uint8)
    return enhanced_image

def drop_invalid_objects(labels, lower_threshold=100, upper_threshold=900):
    def get_object_volume(labels, label):
        return sum(sum(labels == label))

    for lab in np.unique(labels):
        lab_volume = get_object_volume(labels, lab)
        if lab_volume < lower_threshold or lab_volume > upper_threshold:
            # zerujemy te obszary:
            labels[labels == lab] = 0
    
    labels[labels > 0] = 1
    return labels

def simple_segmentation(image):
    image = preparing_image(image, image.size)
    gray = image.convert('L') 
    bw = gray.point(lambda x: 0 if x < 100 else 255, '1')
    arr = 1 - np.array(bw)
    labels = measure.label(arr)
    return np.array(drop_invalid_objects(labels, lower_threshold=100, upper_threshold=1200), dtype='int16')

### RAG Merging method

def _weight_mean_color(graph, src, dst, n):
    """Callback to handle merging nodes by recomputing mean color.

    The method expects that the mean color of `dst` is already computed.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    n : int
        A neighbor of `src` or `dst` or both.

    Returns
    -------
    data : dict
        A dictionary with the `"weight"` attribute set as the absolute
        difference of the mean color between node `dst` and `n`.
    """

    diff = graph.nodes[dst]['mean color'] - graph.nodes[n]['mean color']
    diff = np.linalg.norm(diff)
    return {'weight': diff}


def merge_mean_color(graph, src, dst):
    """Callback called before merging two nodes of a mean color distance graph.

    This method computes the mean color of `dst`.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    """
    graph.nodes[dst]['total color'] += graph.nodes[src]['total color']
    graph.nodes[dst]['pixel count'] += graph.nodes[src]['pixel count']
    graph.nodes[dst]['mean color'] = (graph.nodes[dst]['total color'] /
                                      graph.nodes[dst]['pixel count'])

def rag_merging_segmentation(image):
    # input - PIL Image
    img = np.array(image)
    labels = segmentation.slic(img, compactness=30, n_segments=350)
    g = graph.rag_mean_color(img, labels)

    labels2 = graph.merge_hierarchical(labels, g, thresh=45, rag_copy=False,
                                       in_place_merge=True,
                                       merge_func=merge_mean_color,
                                       weight_func=_weight_mean_color)

    # for x in np.unique(labels2):
    #     vol = sum(sum(labels2 == x))
    #     if vol > 1200 or vol < 100:
    #         labels2[labels2 == x] = 0

    return np.array(drop_invalid_objects(labels2, lower_threshold=100, upper_threshold=1200), dtype='int16')


def simple_threshold(image, threshold):
    img = np.array(image)[:,:,0]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.medianBlur(img, 5)
    ret, th1 = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    binary = (th1 == 255).astype(int)
    arr = 1 - binary
    labels = measure.label(arr)[:,:,0]
    return np.array(drop_invalid_objects(labels, lower_threshold=100, upper_threshold=1200), dtype='int16')