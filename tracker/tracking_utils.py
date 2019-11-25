import multiprocessing
import time
from random import random
import munkres
import cv2
import numpy as np
from PIL import Image
from joblib import Parallel, delayed
from scipy import ndimage
import matplotlib.pyplot as plt
from tracker import two_cc, simple_segmentation
import math



def construct_blocks(support_map):
    sms=support_map.shape
    width=math.ceil(sms[0]/8)
    height=math.ceil(sms[1]/8)
    blocks=np.zeros( (width, height) )
    for i in range(width):
        for j in range(height):
            fore_pixels=0
            for k in range(min(8, sms[0]-8*i)):
                for l in range(min(8, sms[1]-8*j)):
                    if support_map[8*i+k][8*j+l]==1:
                        fore_pixels+=1
            if fore_pixels>10:
                blocks[i][j]=1
    return blocks


def dfs(array,box,i,j,index,nums,indices):
    nums+=1
    if i-1 > 0 and array[i-1][j]==1.0 and box[i-1][j]==0.0:
            box[i-1][j]=index
            indices[index].append((i-1,j))
            nums=dfs(array,box,i-1,j,index,nums,indices)
    if j-1 > 0 and array[i][j-1]==1.0 and box[i][j-1]==0.0:
            box[i][j-1]=index
            indices[index].append((i,j-1))
            nums=dfs(array,box,i,j-1,index,nums,indices)
    if i+1 < array.shape[0] and array[i+1][j]==1.0 and box[i+1][j]==0.0:
            box[i+1][j]=index
            indices[index].append((i+1,j))
            nums=dfs(array,box,i+1,j,index,nums,indices)
    if j+1 < array.shape[1] and array[i][j+1]==1.0 and box[i][j+1]==0.0:
            box[i][j+1]=index
            indices[index].append((i,j+1))
            nums=dfs(array,box,i,j+1,index,nums,indices)
    return nums

def connected_blocks(array):
    counts=dict()
    indices=dict()
    nums=0
    index=1
    indices[index]=[]
    box=np.zeros(array.shape)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            if array[i][j]==1.0 and box[i][j]==0.0:
                box[i][j]=index
                indices[index].append((i,j))
                nums=dfs(array,box,i,j,index,nums,indices)
                counts[index]=nums
                index+=1
                indices[index]=[]
                nums=0
    indices.pop(index)
    return counts, indices


def update_matching(FD1, matching):
    for k in range(len(matching)): # we consider all first element in pairs in matching
        key_prev = FD1.objects[k].index #key/index of object in FD[i-1], that color
        key_curr = matching[k][1] + 1
        matching[k] = (key_prev, key_curr)
    return matching


def find_borders(block_array): # used in borders_on_the_frame
    borders = np.zeros((block_array.shape[0],block_array.shape[1]),dtype='int16')
    count_neighbours=0
    neighbours_color=0
    for i in range(block_array.shape[0]):
        for j in range(block_array.shape[1]):
            if i-1 > 0 and block_array[i-1][j] > 0:
                count_neighbours+=1
                neighbours_color=block_array[i-1][j]
            if j-1 > 0 and block_array[i][j-1] > 0:
                count_neighbours+=1
                neighbours_color=block_array[i][j-1]
            if i+1 < block_array.shape[0] and block_array[i+1][j] > 0:
                count_neighbours+=1
                neighbours_color=block_array[i+1][j]
            if j+1 < block_array.shape[1] and block_array[i][j+1] > 0:
                count_neighbours+=1
                neighbours_color=block_array[i][j+1]
            if 0 < count_neighbours < 4:
                borders[i][j]=neighbours_color
            count_neighbours=0
            neighbours_color=0
    return borders

def colors(width, height): # used in set_colors()
    random_color = lambda: (int(random()*255), int(random()*255), int(random()*255))
    colors = [random_color() for i in range(width*height)]
    return colors

def set_colors(block_map, colors): # used in borders_on_the_frame
    width = block_map.shape[0]
    height = block_map.shape[1]
    colored_map = np.zeros((width,height,3), dtype='int16')
    for j in range(height):
        for i in range(width):
            colored_map[i][j] = colors[int(block_map[i][j])]
    return colored_map


# def show_final_frame(FD, i, colors):
#     f1=plt.title(f"{i+1}. frame - {len(FD[i].objects)} objects")
#     f1=plt.imshow(FD[i].borders_on_frame(colors))
#     plt.show()
#
# def show_match_frame(FD, i, colors):
#      return FD[i].borders_on_frame(colors)


class Object:
    def __init__(self, index, size, position=None):

        self.index = index
        self.size = size
        self.position = position



class Frame_Data:
    def __init__(self, blocks_data, list_boxes, frame):
        keys =  list(blocks_data.keys())
        self.objects = [Object(keys[i], blocks_data[i+1]) for i in range(len(blocks_data))].copy()
        self.boxes = list_boxes.copy()
        self.frame = frame.copy()


    def list_of_indices(self):
        indices=[]
        for obj in self.objects:
            indices.append(obj.index)
        return indices

    def smallest_missing_key(self):
        key=1
        keys = self.boxes.keys()
        while (True):
            if key in keys:
                key+=1
            else:
                return key


    def set_positions(self):
        for key, points in self.boxes.items():
            array = np.zeros(self.frame.size)
            for point in points:
                array[point]=1
            self.objects[self.list_of_indices().index(key)].position = ndimage.measurements.center_of_mass(array)


    def array_boxes(self):
        array = np.zeros(self.frame.size)
        for key in self.boxes.keys():
            for pixels in self.boxes[key]:
                array[pixels]=key
        return array

    def reconstruct_array(self):
        blocks=self.array_boxes()
        shape=self.frame.size
        frame_array = np.zeros((shape[1],shape[0]), dtype='int16')
        for index,block in np.ndenumerate(blocks):
            if block > 0:
                for i in range(8*index[0], min(shape[1], 8*index[0]+8)):
                    for j in range(8*index[1], min(shape[0], 8*index[1]+8)):
                        frame_array[i][j]=block
        return frame_array

    def borders_on_frame(self, colors):
        borders_map = find_borders(self.reconstruct_array())
        shape=self.frame.size
        frame_array = np.array(self.frame, dtype='int16')
        colored_borders=set_colors(borders_map, colors)
        for i in range(shape[1]):
            for j in range(shape[0]):
                if borders_map[i][j]>0:
                    frame_array[i][j]=colored_borders[i][j]
        return frame_array


    def add_objects(self, object_list): # adding new objects which are in the object_list
        for new in object_list:
            self.objects.append(new)

    def update_add(self, card):
        for i in range(len(self.boxes), card):
            key = self.smallest_missing_key()
            self.add_objects([Object(key, 0)])
            self.boxes[key]=[]

    def change_frame(self, boxes, matching):
        for ind, pair in enumerate(matching):
            self.boxes[pair[0]] = boxes[pair[1]]
            self.objects[pair[1]-1].index = pair[0]

    def update_remove(self): # remove too much boxes
        self.boxes = {key:val for key, val in self.boxes.items() if ( val != [] and key in self.list_of_indices() )}
        self.objects = [ obj for obj in self.objects if obj.size!=0]



class Matching:
    def __init__(self, FD1, FD2):
        self.X_set = FD1.objects.copy()
        self.Y_set = FD2.objects.copy()
        self.set_card = max(len(FD1.objects), len(FD2.objects))

    def create_cost_matrix(self):
        card = self.set_card
        cost_matrix = np.zeros((card, card))
        for i in range(card):
            for j in range(card):
                value=0.00
                if (self.X_set[i].size != 0) and (self.Y_set[j].size != 0):
                    for k in [0,1]:
                        value += (self.X_set[i].position[k] - self.Y_set[j].position[k])**2
                cost_matrix[i][j] = round(math.sqrt(value),3)
        return cost_matrix

    def find_matching(self):
        C = self.create_cost_matrix()
        m = munkres.Munkres()
        indexes = m.compute(C)
        return indexes



def pipeline_final(frames, segmentation_method):

    width, height = math.ceil(frames[0].size[0] / 8), math.ceil(frames[0].size[1] / 8)
    diameter = math.sqrt(width ** 2 + height ** 2)
    color = colors(width, height)
    segments, blocks, count_boxes, list_boxes, FD, matchings = [], [] ,[], [], [], []
    start_frame = 0
    end_frame = len(frames)
    num_cores = multiprocessing.cpu_count()
    for i in range(start_frame):
        segments.append(None)
        blocks.append(None)
        count_boxes.append(None)
        list_boxes.append(None)
        FD.append(None)
        matchings.append(None)

    start = time.time()
    if segmentation_method == 'two_cc':
        segments = Parallel(n_jobs=num_cores)(delayed(two_cc.two_connected_components)(frames[i], channel="red",thresh=86) for i in range(start_frame, end_frame))
    elif segmentation_method == 'watershed':
        segments = Parallel(n_jobs=num_cores)(delayed(simple_segmentation.simple_segmentation)(frames[i]) for i in range(len(frames)))
    elif segmentation_method == 'simple_threshold':
        pass
    end = time.time()
    print('elapsed seconds:', end - start)
    
    for i in range(start_frame, end_frame):
        blocks.append(construct_blocks(segments[i]))
        count_boxes_, list_boxes_ = connected_blocks(blocks[i])
        count_boxes.append(count_boxes_)
        list_boxes.append(list_boxes_)
        FD.append(Frame_Data(count_boxes[i],list_boxes[i], frames[i]))
        FD[i].set_positions()
        if i>start_frame:
            card = max(len(FD[i-1].boxes), len(FD[i].boxes))
            FD[i-1].update_add( card)
            FD[i].update_add( card)
            M = Matching(FD[i-1], FD[i])
            matching = M.find_matching()
            matching = update_matching(FD[i-1], matching)
            boxes=FD[i].boxes.copy()
            FD[i].change_frame(boxes, matching)
            FD[i].update_remove()
            FD[i].set_positions()
#         show_final_frame(FD, i, color)
        matchings.append(show_match_frame(FD, i, color))
    return matchings


def show_final_frame(FD, i, colors):
    f1=plt.title(f"{i+1}. frame - {len(FD[i].objects)} objects")
    f1=plt.imshow(FD[i].borders_on_frame(colors))
    plt.show()

def show_match_frame(FD, i, colors):
     return FD[i].borders_on_frame(colors)
