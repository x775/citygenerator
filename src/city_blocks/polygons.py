import numpy as np
from operator import itemgetter

# INPUT:    Dictionary
# OUTPUT:   List
# Creates a list of all polygons in the generated road network
def get_polygons(vertex_dict):
    wedges = get_wedges(vertex_dict)
    polygons = []

    # INPUT:    Tuple
    # OUTPUT:   Tuple | None
    # Find a new set of vertices forming a wedge that shares a segment with the
    # input vertices. This ensures the list returned is in a clockwise order.
    def search(wedge):
        for w in wedges:            
            if wedge[1] is w[0] and wedge[2] is w[1]:
                return w
        return None

    while len(wedges) > 0:
        start = current_wedge = wedges[0]
        current_polygon = []

        while current_wedge is not None:
            current_polygon.append(current_wedge[0])
            wedges.remove(current_wedge)
            if current_wedge[1] is start[0] and current_wedge[2] is start[1]:
                polygons.append(current_polygon)
                break
            current_wedge = search(current_wedge)
    
    return polygons


# INPUT:    Dictionary
# OUTPUT:   List
# Get tuples of vertices forming wedges. I.e. each tuple contains three
# vertices. Each vertex in the road network is considered one at a time. A
# vertex with four segments connected to it will have four different wedges as
# output.
def get_wedges(vertex_dict):
    all_wedges = []
    for vertex, segments in vertex_dict.items():

        alphas = []

        for segment in segments:
            if vertex is segment.start_vert:
                alpha = np.degrees(np.arctan2(segment.end_vert.position[1] - segment.start_vert.position[1],
                                              segment.end_vert.position[0] - segment.start_vert.position[0]))
            else:
                alpha = np.degrees(np.arctan2(segment.start_vert.position[1] - segment.end_vert.position[1],
                                              segment.start_vert.position[0] - segment.end_vert.position[0]))
            
            if alpha < 0:
                alpha += 360
            
            if vertex is segment.start_vert:
                alphas.append((segment.end_vert, alpha))
            else:
                alphas.append((segment.start_vert, alpha))
        
        # Sort list ascendingly based on angle values. 
        alphas.sort(key=itemgetter(1))

        for i in range(len(alphas)):
            alpha = alphas[i-1]
            next_alpha = alphas[i]
            if i == 0:
                angle = next_alpha[1] - alpha[1] + 360
            else:
                angle = next_alpha[1] - alpha[1]

            angle %= 360
            all_wedges.append((alpha[0], vertex, next_alpha[0], angle))

    return all_wedges
