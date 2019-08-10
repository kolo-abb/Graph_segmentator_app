from PIL import Image, ImageEnhance
import cv2
import numpy as np
import networkx as nx
from graphviz import Graph
from networkx.algorithms import approximation as apxa
from random import randint,random
from datetime import timedelta
import time

from segmentator.preprocessing import creating_graph

def converting_to_binary(image_arr, channel, fill_in, p):
    # 1. Choosing channel
    if len(image_arr.shape)!=2:
        if channel == "red":
            image = image_arr[:,:,0]            
        elif channel == "green":
            image = image_arr[:,:,1]                    
        elif channel == "blue":
            image = image_arr[:,:,2]                   
        elif channel == "all":
            image = cv2.cvtColor(image_arr, cv2.COLOR_RGB2GRAY)
    else:
        image = image_arr     
    # 2. Choosing threshold and creating binary version of image
    if p is None:
        ret, thresh=cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        ret, thresh=cv2.threshold(image, p, 255, cv2.THRESH_BINARY_INV)    
    # 3. Filling in holes
    if fill_in == 1: #True
        contours, hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            cv2.drawContours(thresh,[cnt],0,255,-1)
        kernel = np.ones((3,3),np.uint8)
        filled_in = cv2.morphologyEx(thresh,cv2.MORPH_OPEN, kernel,iterations=2)   
        binary = Image.fromarray(filled_in)    
    else:
        binary = thresh
    return binary

def reject_comp(bicomponents): # We can add option for user to add parameters for t_down adn t_up
    volume = []
    for comp in bicomponents:
        volume.append(len(comp))
    median = np.quantile(volume, 0.5, axis=0)
    t_down = int(median/2)
    t_up=int(18*median)
    bicomponents.remove(max(bicomponents, key=len)) #We reject the background regardless of t_up
    reject_set = []
    for comp in bicomponents:
        if len(comp) <= t_down:
            reject_set.append(comp)
        elif len(comp) >= t_up:
            reject_set.append(comp)
    normal_comp = [item for item in bicomponents if item not in reject_set]
    return normal_comp

def get_components(img_binary):
    image_arr = np.array(img_binary, dtype='int16')
    graph = creating_graph(image_arr)
    comps = apxa.k_components(graph)
    comps = comps[2]
    return reject_comp(comps)

def get_result_random(channel, two_connected_components):
    im=Image.new('RGB', (channel.shape[1], channel.shape[0]))
    result=im.load()
    random_color = lambda: (int(random()*255), int(random()*255), int(random()*255))
    colors = [random_color() for i in range(len(two_connected_components))]
    i=0
    for component in two_connected_components:
        for pair in component:
            result[pair[1],pair[0]] = colors[i]
        i+=1
    return im