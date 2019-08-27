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

def transform_rgb_to_yuv(image):
    r_channel = image[:,:,0]
    g_channel = image[:,:,1]
    b_channel = image[:,:,2]
    
    y_channel = 0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel
    u_channel = 0.492 * (b_channel - y_channel)
    v_channel = 0.877 * (r_channel - y_channel) 
    
    return y_channel, u_channel, v_channel

def get_distributions(foreground, background):
    # foreground, background - Images
    
    y_foreground, _, _ = transform_rgb_to_yuv(np.array(foreground))
    y_background, _, _ = transform_rgb_to_yuv(np.array(background))
    
    foreground_data = y_foreground.reshape(y_foreground.shape[0] * y_foreground.shape[1], 1)
    background_data = y_background.reshape(y_background.shape[0] * y_background.shape[1], 1)
    
    mu1, std1 = norm.fit(y_foreground)
    mu2, std2 = norm.fit(y_background)
        
    return mu1, std1, mu2, std2

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

def image_processing_pipeline(image, foreground, background):
    # image is a np.array, in RGB model
    width, height, depth = np.array(image).shape
    # rescaling
    size_y = 128
    size_x = int(width * size_y / height)
    image = image.resize((size_x, size_y), Image.ANTIALIAS)
    y, u, v = transform_rgb_to_yuv(np.array(image))
    im_g = np.array(y)
    im_arr = im_g.reshape((im_g.shape[0],im_g.shape[1],1))    
    mu1, std1, mu2, std2 = get_distributions(foreground, background)
    
    G = create_graph(im_arr, mu1, std1, mu2, std2)
    
    R = edmonds_karp(G, 's', 't')

    print('Current flow:', R.graph['flow_value'], end=' ')

    dimx = im_arr.shape[0]
    dimy = im_arr.shape[1]
    flows = [R['s'][(i,j)]['flow'] for i in range(dimx) for j in range(dimy)]
    threshold = 2 * np.mean(flows)
    bitmap = get_bitmap(R, threshold, dimx, dimy)

    result_image = im_arr[:,:,0] * bitmap
    
    print('Slice {}: done!'.format(0))

    for i in range(result_image.shape[0]):
        for j in range(result_image.shape[1]):
            if result_image[i,j] == 0:
                result_image[i,j] = 255
                        
    # return R # ??
    return Image.fromarray(np.transpose(result_image), 'L')