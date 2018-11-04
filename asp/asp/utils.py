from asp.models import Category, Item, UserExt, Ordered_Item, Available_Item, Distance, Hospital
import csv
from collections import defaultdict

class Graph:
    def __init__(self):
        self.edges = defaultdict(list)
        self.weights = {}

    def add_edge(self, from_node, to_node, weight):
        # Note: assumes edges are bi-directional
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight

def arrange_items_by_category(logged_in_user):
    items_stored_by_category = {}
    items = Available_Item.objects.filter(supplying_hospital = UserExt.objects.get(user = logged_in_user).hospital.supplying_hospital)
    for item in items:
        if item.item_abstract.category.name not in items_stored_by_category:
            items_stored_by_category[item.item_abstract.category.name] = []
        items_stored_by_category[item.item_abstract.category.name].append(item.item_abstract)
    return items_stored_by_category

def transform_priority_to_integer(priority):
    if priority == 'low':
        req_priority = 1
    elif priority == 'medium':
        req_priority = 2
    else:
        req_priority = 3
    return req_priority

# def getTotalWeight(orderID):
#     sumWeight = 0.0
#     # ID of all ordered items from current order
#     for i in Ordered_Item.objects.filter(order = orderID.id):
#         # Find its weight
#         sumWeight += Item.objects.get(name = i.item.name).weight * i.quantity
#     return sumWeight

def generateCSV(content):
    path_to_file = 'asp/static/asp/itinerary.csv'
    with open(path_to_file, 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(content)
    csvFile.close()
    return path_to_file

# get the supplying_hospital of the hospital where the requester work at
# relationship: supplying_hospital deliver the order to the hospital of the requester
def getSupplyingHospital(order):
    return order.requester.hospital.supplying_hospital

def shortest_route(graph, initial, num):
    # shortest paths is a dict of nodes
    # whose value is a tuple of (previous node, weight)
    shortest_paths = {initial: (None, 0)}
    count = 1
    current_node = initial.name
    visited = set()
    path = []
    while count != num:
        visited.add(current_node)
        destinations = graph.edges[current_node]
        distance = 10000000000
        for clinic in destinations:
            if clinic not in visited:
                if graph.weights[(current_node, clinic)] < distance:
                    next_node = clinic
                    distance = graph.weights[(current_node, clinic)]
        path.append(next_node)

        current_node = next_node
        count += 1
    path.append(initial.name)
    return path

def generateItinerary(listOfHospitals):
    '''
    dispatched_order_hospitals will be a list containing the Hospital name(a string)

    distance will be a list of tuples which looks like (hospital_a:string, hostpial_b:string, distance:float)
    '''
    graph = Graph()
    edges = list()
    for i in range(0, len(listOfHospitals)):
        for j in range(i+1, len(listOfHospitals)):
            d = Distance.objects.filter(hospital_a = listOfHospitals[i]).get(hospital_b= listOfHospitals[j])
            edges.append((d.hospital_a.name, d.hospital_b.name, d.distance))
    for edge in edges:
        graph.add_edge(*edge)
    order = shortest_route(graph, listOfHospitals[len(listOfHospitals)-1], len(listOfHospitals))
    ityData = list()
    for i in order:
        ityData.append(Hospital.objects.get(name = i))
    print(ityData)
    '''
    format the output
    '''
    itinerary_string = []
    itinerary_string.append(["Name", "latitude", "longtitude","altitude"])
    for hospital_object in ityData:
        itinerary_string.append([hospital_object.name, hospital_object.latitude, hospital_object.longtitude, hospital_object.altitude])
    return itinerary_string
