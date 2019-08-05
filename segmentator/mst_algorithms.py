from random import random

import math
from PIL import Image
from segmentator.preprocessing import Node


class Forest:
    def __init__(self, num_nodes):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.num_sets = num_nodes

    def size_of(self, i):
        return self.nodes[i].size

    def find(self, n):
        temp = n
        print(type(temp))
        while temp != self.nodes[temp].parent:
            temp = self.nodes[temp].parent

        self.nodes[n].parent = temp
        return temp

    def merge(self, a, b):
        if self.nodes[a].size > self.nodes[b].size:
            self.nodes[b].parent = a
            self.nodes[a].size = self.nodes[a].size + self.nodes[b].size
        else:
            self.nodes[a].parent = b
            self.nodes[b].size = self.nodes[b].size + self.nodes[a].size

        self.num_sets = self.num_sets - 1


def get_sorted_edges(G):
    return sorted(G.edges(data=True), key=lambda e: e[2]['weight'])


def threshold_mst_1(size, const):
    return const * 1.0 * math.sqrt(size)


def threshold_mst_2(size, const):
    return (const * 1.0) / math.sqrt(size)


def threshold_mst_3(const):
    return const


def mst_segmentation_1const(G, threshold=threshold_mst_1, const=3.0):
    forest = Forest(G.width * G.height)

    vertex_id = lambda x, y: y * G.width + x

    if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
        Threshold = [threshold(1, const) for _ in range(G.width * G.height)]
    elif threshold == threshold_mst_3:
        Threshold = [threshold(const) for _ in range(G.width * G.height)]

    for e in get_sorted_edges(G):
        parent_a = forest.find(vertex_id(e[0][0], e[0][1]))
        parent_b = forest.find(vertex_id(e[1][0], e[1][1]))
        a_condition = e[2]['weight'] <= Threshold[parent_a]
        b_condition = e[2]['weight'] <= Threshold[parent_b]

        if parent_a != parent_b and a_condition and b_condition:
            forest.merge(parent_a, parent_b)
            a = forest.find(parent_a)
            if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
                Threshold[a] = e[2]['weight'] + threshold(forest.nodes[a].size, const)

    return forest


def merge_small(forest, G, min_size):
    vertex_id = lambda x, y: y * G.width + x
    for e in get_sorted_edges(G):
        a = forest.find(vertex_id(e[0][0],e[0][1]))
        b = forest.find(vertex_id(e[1][0],e[1][1]))

        if a != b and (forest.size_of(a) < min_size or forest.size_of(b) < min_size):
            forest.merge(a, b)

    return forest


def count_objects(forest):
    return forest.num_sets


def get_segmented_image(forest,G):
    random_color = lambda: (int(random()*255), int(random()*255), int(random()*255))
    colors = [random_color() for i in range(G.width*G.height)]
    img = Image.new('RGB', (G.width, G.height))
    im = img.load()
    for y in range(G.height):
        for x in range(G.width):
            comp = forest.find(y * G.width + x)
            im[x, y] = colors[comp]

    return img.transpose(Image.ROTATE_270).transpose(Image.FLIP_LEFT_RIGHT)


# change algforithms
def mst_segmentation_1const_additional(G, forest, threshold, const, max_size):
    vertex_pos = lambda x: (x.nr-int(x.nr/G.width)*G.width,int(x.nr/G.width))
    vertex_id = lambda x, y: y * G.width + x
    dict={}
    for a in forest.nodes:
        if a.parent in dict.keys():
            dict[a.parent].append(a)
        else:
            dict[a.parent]=[a,forest.nodes[a.parent]]
    max=0
    max_x=None
    for x in dict:
        if len(dict[x])>max_size:
            print(len(dict[x]))
            if len(dict[x])>max:
                if max>0:

                    lst=[]
                    for a in dict[max_x]:
                        lst.append(vertex_pos(a))
                        a.parent=a.nr
                        forest.num_sets+=1
                    forest.num_sets-=1
                    K=G.subgraph(lst)
                    if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
                        Threshold = [threshold(1, const) for _ in range(G.width * G.height)]
                    elif threshold == threshold_mst_3:
                        Threshold = [threshold(const) for _ in range(G.width * G.height)]

                    for e in get_sorted_edges(K):
                        parent_a = forest.find(vertex_id(e[0][0], e[0][1]))
                        parent_b = forest.find(vertex_id(e[1][0], e[1][1]))
                        a_condition = e[2]['weight'] <= Threshold[parent_a]
                        b_condition = e[2]['weight'] <= Threshold[parent_b]

                        if parent_a != parent_b and a_condition and b_condition:
                            forest.merge(parent_a, parent_b)
                            a = forest.find(parent_a)
                            if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
                                Threshold[a] = e[2]['weight'] + threshold(forest.nodes[a].size, const)

                max=len(dict[x])
                max_x=x
            else:

                lst=[]
                for a in dict[x]:
                    lst.append(vertex_pos(a))
                    a.parent=a.nr
                    forest.num_sets+=1
                forest.num_sets-=1
                K=G.subgraph(lst)
                if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
                    Threshold = [threshold(1, const) for _ in range(G.width * G.height)]
                elif threshold == threshold_mst_3:
                    Threshold = [threshold(const) for _ in range(G.width * G.height)]

                for e in get_sorted_edges(K):
                    parent_a = forest.find(vertex_id(e[0][0], e[0][1]))
                    parent_b = forest.find(vertex_id(e[1][0], e[1][1]))
                    a_condition = e[2]['weight'] <= Threshold[parent_a]
                    b_condition = e[2]['weight'] <= Threshold[parent_b]

                    if parent_a != parent_b and a_condition and b_condition:
                        forest.merge(parent_a, parent_b)
                        a = forest.find(parent_a)
                        if (threshold == threshold_mst_1) | (threshold == threshold_mst_2):
                            Threshold[a] = e[2]['weight'] + threshold(forest.nodes[a].size, const)

    return forest


