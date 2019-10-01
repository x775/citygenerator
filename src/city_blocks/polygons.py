import numpy as np
from operator import itemgetter

# INPUT:    Dictionary
# OUTPUT:   List
# Creates a list of all polygons in the generated road network
def get_polygons(vertex_dict):
    angles = get_angles(vertex_dict)
    polygons = []

    # INPUT:    Tuple
    # OUTPUT:   Tuple | None
    # Find a new set of vertices forming an angle that shares
    # a segment with the input vertices. This ensures the list
    # returned is in a clockwise order.
    def search(angle):
        for ang in angles:            
            if angle[1] is ang[0] and angle[2] is ang[1]:
                return ang
        return None

    while len(angles) > 0:
        start = current_angle = angles[0]
        current_polygon = []

        while True:
            current_polygon.append(current_angle[0])
            current_angle = search(current_angle)
            if current_angle is not None:
                angles.remove(current_angle)
                if current_angle is start:
                    polygons.append(current_polygon)
                    break
    
    return polygons


# INPUT:    Dictionary
# OUTPUT:   List
# Get tuples of vertices forming angles. I.e. each tuple contains three vertices.
# Each vertex in the road network is considered one at a time.
# A vertex with four segments connected to it will have four different angles as output.
def get_angles(vertex_dict):
    all_angles = []
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
            all_angles.append((alpha[0], vertex, next_alpha[0], angle))

    return all_angles
