import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx
from PIL import Image, ImageFilter, ImageEnhance
from joblib import Parallel, delayed
import multiprocessing
import two_cc
from skimage import measure
from statistics import median
import time
import cv2
from random import random
import scipy.misc

def get_arc_weight(vertex1, vertex2, d_max):
    # vertex = (x,y,z), where x,y - coords, z - frame number
    dist = np.linalg.norm(np.array(vertex1[:2]) - np.array(vertex2[:2]))
    return dist / d_max

def get_num_frames(graph):
    num_frames = -1
    for vertex in graph:
        if vertex[2] > num_frames:
            num_frames = vertex[2]
    return num_frames + 1 # frames indexing starts from 0

def vertices_from_ith_frame(graph, i):
    vertices = []
    for vertex in graph:
        if vertex[2] == i:
            vertices.append(vertex)
    return vertices

def get_distance(vertex1, vertex2):
    return np.linalg.norm(np.array(vertex1[:2]) - np.array(vertex2[:2]))

def get_neighbors(vertex, vertices, d_max):
    neighbors = []
    for vertex2 in vertices:
        if get_distance(vertex, vertex2) <= d_max:
            neighbors.append(vertex2)
    return neighbors

def get_most_distant_neighbor(vertex, neighbors):
    d_max = 0
    most_distant_neighbor = neighbors[0]
    for neighbor in neighbors:
        if d_max < get_distance(vertex, neighbor):
            d_max = get_distance(vertex, neighbor)
            most_distant_neighbor = neighbor
    return most_distant_neighbor

def get_common_neighbors(vertex1, vertex2, vertices_from_next_frame, d_max):
    neighbors1 = get_neighbors(vertex1, vertices_from_next_frame, d_max)
    neighbors2 = get_neighbors(vertex2, vertices_from_next_frame, d_max)
    return list(set(neighbors1).intersection(set(neighbors2)))

def initial_graph_refinement(graph, dist_max, dist_border):
    # graph.nodes consists of vertices as follows: (x,y,z), where x,y - are Cartesian coordinates,
    # z -  frame's number
    
    num_frames = get_num_frames(graph)
    
    for i in range(num_frames - 1):
        for vertex in vertices_from_ith_frame(graph, i):
            neighbors = get_neighbors(vertex, vertices_from_ith_frame(graph, i + 1), dist_max)
            # configuration I
            if len(neighbors) == 0:
                dist = dist_max
                while len(neighbors) == 0 and dist < dist_border:
                    dist = dist * 1.5
                    neighbors = get_neighbors(vertex, vertices_from_ith_frame(graph, i + 1), dist_max)
                if len(neighbors) > 0:
                    graph.add_edge(vertex, neighbors[0])    
            
            # configuration II
            if len(neighbors) > 1:
                # simplified
                neighbor = get_most_distant_neighbor(vertex, neighbors)
                if (vertex, neighbor) in graph.edges:
                    graph.remove_edge(vertex, neighbor)
            
            # configuration III
            for vertex2 in vertices_from_ith_frame(graph, i):
                neighbors = get_common_neighbors(vertex, vertex2, vertices_from_ith_frame(graph, i + 1), dist_max)
                if vertex != vertex2 and len(neighbors) > 0:
                    if len(get_neighbors(vertex, vertices_from_ith_frame(graph, i + 1), dist_max)) > 2 and len(get_neighbors(vertex2, vertices_from_ith_frame(graph, i + 1), dist_max)) <= 2: 
                        if (vertex, neighbors[0]) in graph.edges:
                            print("Removing", vertex, "-", neighbors[0])
                            graph.remove_edge(vertex, neighbors[0])
                    elif len(get_neighbors(vertex2, vertices_from_ith_frame(graph, i + 1), dist_max)) > 2 and len(get_neighbors(vertex, vertices_from_ith_frame(graph, i + 1), dist_max)) <= 2: 
                        if (vertex2, neighbors[0]) in graph.edges:
                            print("Removing", vertex2, "-", neighbors[0])
                            graph.remove_edge(vertex2, neighbors[0])
                    else:
                        dist1 = get_distance(vertex, neighbors[0])
                        dist2 = get_distance(vertex2, neighbors[0])
                        if dist1 > dist2:
                            if (vertex, neighbors[0]) in graph.edges:
                                print("Removing", vertex, "-", neighbors[0])
                                graph.remove_edge(vertex, neighbors[0])
                        else:
                            if (vertex2, neighbors[0]) in graph.edges:
                                print("Removing", vertex2, "-", neighbors[0])
                                graph.remove_edge(vertex2, neighbors[0])

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

def find_mass_center(arr, val):
    xx = []
    yy = []
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i][j] == val:
                xx.append(i)
                yy.append(j)
    return (int(median(xx)), int(median(yy)))

def get_all_mass_centers(labels):
    mass_centers = []
    for i in range(1, labels.max() + 1): # 0 label is representing the background
        mass_centers.append(find_mass_center(labels, i))
    return mass_centers

def get_frame_mass_centers(frame):
    frame_arr = np.array(frame)
    labels = measure.label(frame_arr)
    return get_all_mass_centers(labels)
