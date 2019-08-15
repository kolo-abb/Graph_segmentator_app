import datetime

from segmentator.mst_algorithms import threshold_mst_1, mst_segmentation_1const, merge_small, \
    get_segmented_image, count_objects,  mst_segmentation_1const_additional
from segmentator.two_cc_algorithms import converting_to_binary, reject_comp, get_components, get_result_random
from segmentator.preprocessing import prepare_graph, define_nodes, abs_value, define_edges, creating_graph, preparing_image


def mst_1const(img, edges_8=True, threshold=threshold_mst_1, const=3.0, min_size=200):
    print(datetime.datetime.now())
    G = prepare_graph(img, edges_8=edges_8)
    print(datetime.datetime.now())
    forest = mst_segmentation_1const(G, threshold=threshold, const=const)
    print(datetime.datetime.now())
    forest = merge_small(forest, G, min_size)
    print(datetime.datetime.now())
    return get_segmented_image(forest, G), count_objects(forest), forest,G


def mst_1const_additional(G, forest, threshold=threshold_mst_1, const=3.0, min_size=200, max_size=200):
    print(datetime.datetime.now())
    forest = mst_segmentation_1const_additional(G, forest, threshold=threshold, const=const,max_size=max_size)
    print(datetime.datetime.now())
    forest = merge_small(forest, G, min_size)
    print(datetime.datetime.now())
    return get_segmented_image(forest, G), count_objects(forest)


def two_connected_components(img, channel, fill_in, thresh):
    
    image_arr = preparing_image(img, img.size)    
    binary = converting_to_binary(image_arr, channel, fill_in, thresh)
    comps_smaller = get_components(binary)
    final_result = get_result_random(image_arr, comps_smaller)
    number_of_comps = len(comps_smaller)

    return final_result, number_of_comps
