from PIL import Image

from segmentator.mst_algorithms import threshold_blood_cells_1, mst_segmentation_1const, merge_small, \
    get_segmented_image, count_objects, Forest
from segmentator.preprocessing import prepare_graph


def mst_get_imge_1const(img, edges_8=True, threshold=threshold_blood_cells_1, const=3.0,min_size=200):
    G=prepare_graph(img,edges_8=edges_8)
    forest=mst_segmentation_1const(G, threshold=threshold, const=const)
    forest=merge_small(forest, G, min_size)
    return get_segmented_image(forest,G)

def mst_count_1const(img, edges_8=True, threshold=threshold_blood_cells_1, const=3.0,min_size=200):
    G=prepare_graph(img,edges_8=edges_8)
    forest=mst_segmentation_1const(G, threshold=threshold, const=const)
    forest=merge_small(forest, G, min_size)
    return count_objects(forest)

# print(mst_count_1const(Image.open("../static/images/red_blood_cells.png")))