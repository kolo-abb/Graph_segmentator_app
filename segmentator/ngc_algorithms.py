import math
from random import random
from PIL import Image
import numpy as np
import networkx as nx
from scipy import ndimage, spatial

from segmentator.preprocessing import ngc_open_image, ngc_get_image_arr, \
     find_median

def get_NCut(t, M, NCut_min):
    cutAB = 0
    assoAA = 0
    assoBB = 0
    for i in range(0,t+1):
        for j in range(t+1,256):
            cutAB += M[i][j]
    for i in range(0,t+1):
        for j in range(i,t+1):
            assoAA += M[i][j]
    for i in range(t+1,256):
        for j in range(i, 256):
            assoBB += M[i][j]
    A = assoAA + cutAB
    B = assoBB + cutAB
    if A != 0 and B != 0:
        NCutAB = (cutAB / A) + (cutAB / B)
    else:
        NCutAB = NCut_min
    return NCutAB

def ngc_get_treshold(M):
    
    # Initialization
    t = 0
    t_min = 0
    NCut_min = 2
    
    # Search for best treshold and cut
    while t <= 255:
        NCutAB = get_NCut(t, M, NCut_min)
        if NCutAB < NCut_min:
            NCut_min = NCutAB
            t_min = t
        t += 1
        
    return NCut_min, t_min

def ngc_threshold_image(image_arr, threshold):
    result = image_arr
    width = result.shape[0]
    height = result.shape[1]
    for i in range(width):
        for j in range(height):
            if image_arr[i][j] > threshold:
                result[i][j] = 0
            else:
                result[i][j] = 1
    return result

def create_binary_graph(image_arr):
    width = image_arr.shape[0]
    height = image_arr.shape[1]
    G = nx.Graph()
    for i in range(width):
        for j in range(height):
            G.add_node((i,j), weight = image_arr[i][j], reached = 0)
            if i > 0:
                G.add_edge((i,j),(i-1,j))
                if j > 0:
                    G.add_edge((i-1,j-1),(i,j))
                if j < width - 1:
                    G.add_edge((i-1,j+1),(i,j))
            if j > 0:
                G.add_edge((i,j),(i,j-1))
    return G

def ngc_colour_binary_image(image_arr):
    G = create_binary_graph(image_arr)
    result = image_arr
    colour = 50
    stack = []
    colours = []
    for node in G.nodes():
        counter = 0
        if G.nodes[node]['reached'] == 0 and G.nodes[node]['weight'] == 1:
            counter += 1
            colour += 1
            G.nodes[node]['reached'] = 1
            result[node[0]][node[1]] = colour
            stack.append(node)
            while len(stack) != 0:
                taken_node = stack.pop(0)
                counter += 1
                for neighbor in G.neighbors(taken_node):
                    if G.nodes[neighbor]['reached'] == 0 and G.nodes[neighbor]['weight'] == 1:
                        G.nodes[neighbor]['reached'] = 1
                        result[neighbor[0]][neighbor[1]] = colour
                        stack.append(neighbor)
            colours.append([colour, counter])
    return colours, result

def ngc_find_outliners(colours):
    values = []
    outliners = []
    for x in colours:
        values.append(x[1])
    median, median_indices = find_median(sorted(values))
    Q1, Q1_indices = find_median(sorted(values)[:median_indices[0]])
    Q2, Q2_indices = find_median(sorted(values)[median_indices[-1] + 1:])
    for x in colours:
        if Q1 <= x[1] and x[1] < Q2:
            pass
        else:
            outliners.append(x[0])
    return outliners

def ngc_remove_banned_objects(colour_arr, outliners):
    result = colour_arr
    for i in range(result.shape[0]):
        for j in range(result.shape[1]):
            if colour_arr[i][j] in outliners:
                result[i][j] = 0
    return result

def ngc_count_objects(segmentation_arr):
    unique_values = np.unique(segmentation_arr)
    counter = len(unique_values) - 1
    return counter

def ngc_segmented_image(segmentation_arr):
    width = segmentation_arr.shape[0]
    height = segmentation_arr.shape[1]
    # im = Image.fromarray((segmentation_arr * 255).astype('uint8'))
    random_color = lambda: (int(random()*255), int(random()*255), int(random()*255))
    colors = [random_color() for i in range(width*height)]
    img = Image.new('RGB', (width, height))
    im = img.load()
    for j in range(height):
        for i in range(width):
            im[i,j] = colors[segmentation_arr[i][j]]
    return img.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)


