import numpy as np
import networkx as nx
from PIL.Image import Image
import math

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
    if(img.width>=500) | (img.height>=500):
        img = img.resize((500,500))
    image_arr = np.array(img, dtype='int16')
    G = nx.Graph()
    width=image_arr.shape[0]
    height=image_arr.shape[1]
    for i in range(width):
        for j in range(height):
            G.add_node((i,j))

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

# NGC processes

def norm(x1, y1, x2, y2):
    norm = math.sqrt( (x1-x2) ** 2 + (y1-y2) ** 2 )
    return norm

def ngc_set_capacity(image_arr, x1, y1, x2, y2, I, X):
    capacity = np.exp(-(abs((image_arr[x1][y1] - image_arr[x2][y2])/I + norm(x1, y1, x2, y2)/X)))
    return capacity

def find_median(sorted_list):
    
    indices = []

    list_size = len(sorted_list)
    median = 0

    if list_size % 2 == 0:
        indices.append(int(list_size / 2) - 1)  # -1 because index starts from 0
        indices.append(int(list_size / 2))

        median = (sorted_list[indices[0]] + sorted_list[indices[1]]) / 2
        pass
    else:
        indices.append(int(list_size / 2))

        median = sorted_list[indices[0]]
        pass

    return median, indices

def ngc_open_image(img):
    image = Image.open(img).convert('L')
    return image

def ngc_get_image_arr(image):
    image_arr = np.array(image, dtype='int64')
    return image_arr

def create_cut_matrix(image_arr, I, X):
    M = np.zeros((256,256))
    width = image_arr.shape[0]
    height = image_arr.shape[1]
    for i in range(width):
        for j in range(height):
            if i > 0:
                capacity = ngc_set_capacity(image_arr, i, j, i-1, j, I, X)
                M[image_arr[i-1][j]][image_arr[i][j]] += capacity
                M[image_arr[i][j]][image_arr[i-1][j]] += capacity
                if j > 0:
                    capacity = ngc_set_capacity(image_arr, i-1, j-1, i, j, I, X)
                    M[image_arr[i-1][j-1]][image_arr[i][j]] += capacity
                    M[image_arr[i][j]][image_arr[i-1][j-1]] += capacity
                if j < width - 1:
                    capacity = ngc_set_capacity(image_arr, i-1, j+1, i, j, I, X)
                    M[image_arr[i-1][j+1]][image_arr[i][j]] += capacity
                    M[image_arr[i][j]][image_arr[i-1][j+1]] += capacity
            if j > 0:
                capacity = ngc_set_capacity(image_arr, i, j-1, i, j, I, X)
                M[image_arr[i][j-1]][image_arr[i][j]] += capacity
                M[image_arr[i][j]][image_arr[i][j-1]] += capacity
    return M
