from segmentator.mst_algorithms import threshold_mst_1, mst_segmentation_1const, merge_small, \
    get_segmented_image, count_objects, Forest
from segmentator.preprocessing import prepare_graph


def mst_1const(img, edges_8=True, threshold=threshold_mst_1, const=3.0, min_size=200):
    G = prepare_graph(img, edges_8=edges_8)
    forest = mst_segmentation_1const(G, threshold=threshold, const=const)
    forest = merge_small(forest, G, min_size)
    return get_segmented_image(forest, G), count_objects(forest), forest,G


def mst_1const_additional(G, forest, threshold=threshold_mst_1, const=3.0, min_size=200, max_size=200):
    forest = mst_segmentation_1const_additional(G, forest, threshold=threshold, const=const,max_size=max_size)
    forest = merge_small(forest, G, min_size)
    return get_segmented_image(forest, G), count_objects(forest), forest,G


