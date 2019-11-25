import cv2
import numpy as np

def simple_treshold(image, treshold):
    img=np.array(image)[:,:,0]
    img=cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = cv2.medianBlur(img,5)
    ret,th1 = cv2.threshold(img,treshold,255,cv2.THRESH_BINARY)

    return th1


