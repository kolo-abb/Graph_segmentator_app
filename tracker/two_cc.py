from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
import networkx as nx
from graphviz import Graph
from networkx.algorithms import approximation as apxa
from random import randint,random
import matplotlib.pyplot as plt

def define_nodes(graph, shape):
    for i in range(shape[0]):
        for j in range(shape[1]):
            graph.add_node((i, j))

def abs_value(image_arr, x1, y1, x2, y2):
    return abs(image_arr[x1, y1] - image_arr[x2, y2])

def define_edges(graph, image_arr, shape, max_degree=4, diff=abs_value, p=0):
    if max_degree==4:
        for i in range(shape[0]):
            for j in range(shape[1]):
                if i - 1 >= 0 and diff(image_arr,i,j,i-1,j)<=p:
                    graph.add_edge((i, j), (i-1, j), weight=diff(image_arr,i,j,i-1,j))
                if j - 1 >= 0 and diff(image_arr,i,j,i,j-1)<=p:
                    graph.add_edge((i, j), (i, j-1), weight=diff(image_arr,i,j,i,j-1))
    if max_degree==8:
        for i in range(shape[0]):
            for j in range(shape[1]):
                if i - 1 >= 0 and diff(image_arr,i,j,i-1,j)<=p:
                    graph.add_edge((i, j), (i-1, j), weight=diff(image_arr,i,j,i-1,j))
                if j - 1 >= 0 and diff(image_arr,i,j,i,j-1)<=p:
                    graph.add_edge((i, j), (i, j-1), weight=diff(image_arr,i,j,i,j-1))
                if i - 1 >= 0 and j - 1 >= 0 and diff(image_arr,i,j,i-1,j-1)<=p:
                    graph.add_edge((i, j), (i-1, j-1), weight=diff(image_arr,i,j,i-1,j-1))
                if i - 1 >= 0 and j + 1 < shape[0] and diff(image_arr,(i,j),(i-1,j+1))<=p:
                    graph.add_edge((i, j), (i-1, j+1), weight=diff(image_arr,i,j,i-1,j+1))

def creating_graph(image_arr):
    graph=nx.Graph()
    define_nodes(graph, image_arr.shape)
    define_edges(graph, image_arr, image_arr.shape)
    return graph

def preparing_image(image,shape):
    if(shape[1] > 700 or shape[0] > 700):
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
    image_arr = np.array(enhanced_image, dtype=np.uint8)
    return image_arr

def converting_to_binary(image_arr, channel, fill_in, p):
    # 1. Choosinf channel
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
    if fill_in == True:
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
    t_up = int(18*median)
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

# def get_result(channel, two_connected_components):
#     im=Image.new('L', (channel.shape[1], channel.shape[0]))
#     result=im.load()
#     for comp in two_connected_components:
#         for node in comp:
#             result[node[1],node[0]]=255
#     return result

def get_result(channel, two_connected_components):
    result=np.zeros((channel.shape[0], channel.shape[1]))
    for comp in two_connected_components:
        for node in comp:
            result[node[0],node[1]]=255
    image=Image.fromarray(result).convert("L")
    return

def get_result_array(channel, two_connected_components):
    result=np.zeros((channel.shape[0], channel.shape[1]))
    for comp in two_connected_components:
        for node in comp:
            result[node[0],node[1]]=1
    return result

def two_connected_components(img, channel = "all", fill_in = True, thresh = None):
    image_arr = preparing_image(img, img.size)
    binary = converting_to_binary(image_arr, channel, fill_in, thresh)
    comps_smaller = get_components(binary)
    return get_result_array(image_arr,comps_smaller)
