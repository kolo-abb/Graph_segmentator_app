from scipy.stats import norm
import numpy as np
import networkx as nx
from networkx.algorithms.flow import edmonds_karp
from PIL import Image


def get_probability(mu, std, value):
    # given a 'mu' and 'std' parameters describing normal distribution
    # we calculate the probability of 'value'
    # to belong to this dataset
    return norm(mu, std).pdf(value)

def get_distributions(): # foreground, background):
    # foreground, background - Images
    
    # foreground_data = np.array(foreground.getchannel('G'))
    # background_data = np.array(background.getchannel('G'))
    
    # foreground_data = foreground_data.reshape(foreground_data.shape[0] * foreground_data.shape[1], 1)
    # background_data = background_data.reshape(background_data.shape[0] * background_data.shape[1], 1)
    
    # mu1, std1 = norm.fit(foreground_data)
    # mu2, std2 = norm.fit(background_data)
    
    return 128, 0.2, 192, 0.2 # mu1, std1, mu2, std2

def create_graph(arr, mu1, std1, mu2, std2):
    G = nx.DiGraph()
    
    # defining vertex set
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            G.add_node((i,j))
    G.add_node('s')
    G.add_node('t')
    
    # definig edges set with proper weigths (capacities)
    for i1 in range(arr.shape[0]):
        for j1 in range(arr.shape[1]):
            for i2 in range(i1, arr.shape[0]):
                for j2 in range(j1, arr.shape[1]):
                    if (i1 == i2 and j1 == j2 - 1) or (i1 == i2 - 1 and j1 == j2):
                        capacity = np.exp((-0.5 * 1./((std1 + std2)/2.)**2)) * ((arr[i1,j1] - arr[i2,j2])**2)
                        G.add_edge((i1,j1), (i2,j2), capacity=capacity)
                        G.add_edge((i2,j2), (i1,j1), capacity=capacity)

    # capacities of (s, e) and (e, t)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            cap_s = get_probability(mu1, std1, arr[i, j])
            cap_t = get_probability(mu2, std2, arr[i, j])
            cap_sum = cap_s + cap_t
            G.add_edge('s', (i,j), capacity = 2 * cap_s / cap_sum)
            G.add_edge((i,j), 't', capacity = 2 * cap_t / cap_sum)
            
    return G

def get_bitmap(R, threshold, dimx, dimy):
    bitmap = np.zeros((dimx, dimy))
    for i in range(dimx):
        for j in range(dimy):
            if R['s'][(i,j)]['flow'] > threshold:
                bitmap[i][j] = 1
    return bitmap

def image_processing_pipeline(image): #, foreground_sample, background_sample):
    # image is a np.array, in RGB model
    width, height, depth = np.array(image).shape

    result_image = np.zeros((width, height, depth))
    
    mu1, std1, mu2, std2 = get_distributions() # foreground_sample, background_sample)
    
    w_coords = list(range(0, width, 32)) # 32 (krok) - to moze byc parametr wybierany na stronce
    h_coords = list(range(0, height, 32))
    
    if w_coords[-1] != width - 1:
        w_coords.append(width-1)
    if h_coords[-1] != height - 1:
        h_coords.append(height-1)

    for d in range(depth):
        # we split the image into w_coords x h_coords subimages
        for w in range(len(w_coords) - 1): # not considering last element
            for h in range(len(h_coords) - 1):
                arr = image[w_coords[w]:w_coords[w+1], h_coords[h]:h_coords[h+1], d]
                
                G = create_graph(arr, mu1, std1, mu2, std2)
                
                R = edmonds_karp(G, 's', 't')
                
                print('Current flow:', R.graph['flow_value'], end=' ')
                
                dimx = w_coords[w+1] - w_coords[w]
                dimy = h_coords[h+1] - h_coords[h]
                bitmap = get_bitmap(R, 0.3, dimx, dimy)
                
                arr2 = arr * bitmap
                
                result_image[w_coords[w]:w_coords[w+1], h_coords[h]:h_coords[h+1], d] = arr2
                
                print('Slice {}:{},{}:{},{} done!'.format(w_coords[w], w_coords[w+1], h_coords[h], h_coords[h+1], d))
                
    return Image.fromarray(result_image, 'RGB')