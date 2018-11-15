from asp.models import Category, Item, UserExt, Ordered_Item, Available_Item, Distance, Hospital, Order
import csv
import itertools



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

class Graph:
    def __init__(self):
        self.edges = {}
        # Note: assumes edges are bi-directional
        # check if the key exists
    def add_edge(self, from_node, to_node, weight):
        if from_node not in self.edges.keys():
            self.edges[from_node] = {}
        if to_node not in self.edges.keys():
            self.edges[to_node] = {}
        self.edges[from_node][to_node] = weight
        self.edges[to_node][from_node] = weight

        # returns a list containing the routes with the minimum value
        # the elements in the list have the format of ([list_of_hospital_names], path_cost)
    def shortest_route(self, startpoint):
        hospitals_to_permute =list(self.edges.keys())
        hospitals_to_permute.remove(startpoint)
        routes = []
        for route in itertools.permutations(hospitals_to_permute, len(self.edges)-1):
            route_length = self.edges[startpoint][route[0]] + sum(self.edges[i][j] for i, j in zip(route[:-1], route[1:])) \
                            + self.edges[route[-1]][startpoint]
            route_list = list(route)
            route_list.append(startpoint)
            routes.append((route_list, route_length))
        min_value = min(routes, key=lambda x:x[1])[1]
        min_routes = list(filter( lambda x:x[1] == min_value, routes))

        return min_routes


def generateItinerary(listOfHospitals, ordersToDispatch):
    '''
    dispatched_order_hospitals will be a list containing the Hospital name(a string)

    distance will be a list of tuples which looks like (hospital_a:string, hostpial_b:string, distance:float)
    '''
    graph = Graph()
    edges = list()
    for i in range(0, len(listOfHospitals)):
        for j in range(i+1, len(listOfHospitals)):
            # need to check both directions. the order might be flipped
            d = Distance.objects.filter(hospital_a = listOfHospitals[i], hospital_b= listOfHospitals[j])
            if len(d) == 0:
                d = Distance.objects.filter(hospital_a = listOfHospitals[j], hospital_b= listOfHospitals[i])

            edges.append((d[0].hospital_a.name, d[0].hospital_b.name, d[0].distance))
    for edge in edges:
        graph.add_edge(*edge)
    routes = graph.shortest_route(str(listOfHospitals[-1].name))
    '''
    see the priority of the orders that points to the first hospital in the route
    '''
    # first create a list of lists
    list_of_lists_of_priorities = []
    for num in range(len(routes)):
        list_of_lists_of_priorities.append([0] * (len(listOfHospitals) - 1))

    for iter in range(len(listOfHospitals) - 1):
        for index, route in enumerate(routes):
            hospital_name = route[0][0]
            for order in ordersToDispatch:
                hospital = Order.objects.get(id = order.id).requester.hospital.name
                if hospital == hospital_name:
                    if list_of_lists_of_priorities[index][iter] < order.priority:
                        list_of_lists_of_priorities[index][iter] = order.priority

        # make sure there is only one with the highest priority
        list_of_priorities = []
        for col in list_of_lists_of_priorities:
            list_of_priorities.append(sum(col))
        # print(f"sum of cols of the list_of_lists_of_priorities {list_of_priorities}")
        max_value = max(list_of_priorities)
        if len(list(filter(lambda x:x == max_value, list_of_priorities))) == 1:
            break

    max_index = list_of_priorities.index(max(list_of_priorities))

    ityData = []
    for hospital_stop in routes[max_index][0]:
        ityData.append(Hospital.objects.get(name = hospital_stop))
    # print(f"this is the ityData: \n {ityData}")
    '''
    format the output
    '''
    itinerary_string = []
    # itinerary_string.append(["Location Name", "Latitude", "Longtitude","Altitude"])
    for hospital_object in ityData:
        itinerary_string.append([hospital_object.latitude, hospital_object.longtitude, hospital_object.altitude])
    return itinerary_string

def generateShippingData(ordersToProcess):
    return [ item for item in Ordered_Item.objects.filter(order_id = ordersToProcess.id)]
