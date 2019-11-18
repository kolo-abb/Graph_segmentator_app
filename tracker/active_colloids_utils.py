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

def active_colloids_tracking_pipeline(frames):
    tracking_start = time.time()
    # segmentacja
    num_frames = len(frames)
    num_cores = multiprocessing.cpu_count()
    segments = Parallel(n_jobs=num_cores)(delayed(two_cc.two_connected_components)(frames[i], channel="red",thresh=86) for i in range(num_frames))
#     segments = Parallel(n_jobs=num_cores)(delayed(simple_segmentation)(frames[i]) for i in range(num_frames))
    
    G = nx.DiGraph()
    
    all_mass_centers = []
    start = time.time()
    all_mass_centers = Parallel(n_jobs=num_cores)(delayed(get_frame_mass_centers)(segments[i]) for i in range(num_frames))
    end = time.time()
    print('Elapsed seconds of segmentation:', end - start)
    
    # adding nodes
    for i in range(num_frames):
        frame_mass_centers = all_mass_centers[i]
        for j in range(len(frame_mass_centers)):
            pos_x = frame_mass_centers[j][0]
            pos_y = frame_mass_centers[j][1]
            frame_number = i
            G.add_node((pos_x, pos_y, frame_number), pos=(pos_x, pos_y))
    end = time.time()
    
    # adding edges (arcs)
    d_max = 20 # TODO generalize
    
    for frame_number in range(num_frames - 1): # we set attributes for FF
        for vertex1 in vertices_from_ith_frame(G, frame_number):
            for vertex2 in vertices_from_ith_frame(G, frame_number + 1):
                if get_distance(vertex1, vertex2) < d_max:
                    weight = int(10 * get_distance(vertex1, vertex2) / d_max)
                    G.add_edge(vertex1, vertex2, capacity=10, weight=weight)
    
    dist_border = 100000 #### TODO generalize
    
    print('Number of edges before the refinement', len(G.edges))
    initial_graph_refinement(G, d_max, dist_border)
    print('Number of edges before the refinement', len(G.edges))
    
    # new nodes
    source = (-1,-1,-1)
    G.add_node(source, pos=(-1,1)) # source
    sink = (-2,-2,-2)
    G.add_node(sink, pos=(700,1)) # sink
    
    # new edges
    for vertex in vertices_from_ith_frame(G, 0):
        G.add_edge(source, vertex, capacity=10, weight=0)

    for vertex in vertices_from_ith_frame(G, get_num_frames(G) - 1):
        G.add_edge(vertex, sink, capacity=10, weight=0)
        
    # weights should not be floats! We use only integers, otherwise calculations will last forever!
    resultFlowDict = nx.max_flow_min_cost(G, source, sink, capacity='capacity', weight='weight')
    
    tracking_end = time.time()
    print('Tracking finished, elapsed seconds:', tracking_end - tracking_start)
    
    detected_objects = []
    
    visited = {}
    for node in G.nodes:
        visited[node] = False

    results = [np.array(f) for f in frames]
    
    radius = 20
    for node in G.nodes:
        if not visited[node]:
            detected_objects.append(node)
            color = (int(random() * 255), int(random() * 255), int(random() * 255))
            while node != (-2,-2,-2):
                center = (node[1], node[0])
                frame = node[2]
                results[frame] = cv2.circle(results[frame], center, radius, color, thickness=3)
                if resultFlowDict[node] == {}:
                    break
                visited[node] = True
                node = list(resultFlowDict[node].keys())[0]
    
    results = [Image.fromarray(r) for r in results]
    
    return results, G, resultFlowDict # type: list<Image>
