import datetime

import numpy as np
import networkx as nx
from PIL.Image import Image


def diff(image_arr, x1, y1, x2, y2):
    _out = np.sum((image_arr[x1, y1] - image_arr[x2, y2]) ** 2)
    return np.sqrt(_out)

class Node:
    def __init__(self, parent, rank=0, size=1):
        self.parent = parent
        self.rank = rank
        self.size = size
        self.nr = parent

def prepare_graph(img, edges_8=True):
    print('inside prepare_graph'+str(datetime.datetime.now()))
    if(img.width>=500) | (img.height>=500):
        img = img.resize((500,500))
    image_arr = np.array(img, dtype='int16')
    G = nx.Graph()
    width=image_arr.shape[0]
    height=image_arr.shape[1]
    print('inside prepare_graph'+str(datetime.datetime.now()))
    for i in range(width):
        for j in range(height):
            G.add_node((i,j))
    print('inside prepare_graph'+str(datetime.datetime.now()))

    for y in range(height):
            for x in range(width):
                if x > 0:
                    G.add_edge((x,y),(x-1,y),weight=diff(image_arr,x,y,x-1,y))

                if y > 0:
                    G.add_edge((x,y),(x,y-1),weight=diff(image_arr,x,y,x,y-1))

                if edges_8:
                    if x > 0 and y > 0:
                        G.add_edge((x,y),(x-1,y-1),weight=diff(image_arr,x,y,x-1,y-1))

                    if x > 0 and y <width-1:
                        G.add_edge((x,y),(x-1,y+1),weight=diff(image_arr,x,y,x-1,y+1))
    G.width=width
    G.height=height
    return G

#Two connected componentc:

from PIL import Image, ImageEnhance
import numpy as np
import networkx as nx
from graphviz import Graph

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
    enhanced_image = ImageEnhance.Brightness(enhanced_image).enhance(1.05)
    enhanced_image = ImageEnhance.Sharpness(enhanced_image).enhance(0.95) 
    image_arr = np.array(enhanced_image, dtype=np.uint8)
    return image_arr
