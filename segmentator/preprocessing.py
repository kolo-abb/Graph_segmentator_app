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
