import json

def road_network_to_json(road_network):
    output = {}
    output['roadSegments'] = []
    output['roadVertices'] = []
    for segment in road_network:
        output['roadVertices'].append({
            'position': {
                'x': float(segment.start_vert.position[0]),
                'y': float(segment.start_vert.position[1])
                }})
        output['roadVertices'].append({
            'position': {
                'x': float(segment.end_vert.position[0]),
                'y': float(segment.end_vert.position[1])
        }})
        output['roadSegments'].append({
            'startVertIndex': len(output['roadVertices']) - 2,
            'endVertIndex': len(output['roadVertices']) - 1
        })

    with open("roadnetwork.json", "w") as out:
        json.dump(output, out)




    