from skimage import measure
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np


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
    return drop_invalid_objects(labels, lower_threshold=100, upper_threshold=1200)