from asp.models import Category, Item, UserExt, Ordered_Item, Available_Item
import csv

def arrange_items_by_category(logged_in_user):
    items_stored_by_category = {}
    items = Available_Item.objects.filter(supplying_hospital = UserExt.objects.get(user = logged_in_user).hospital)
    for item in items:
        print("item ", item)
        if item.item_abstract.category.name not in items_stored_by_category:
            items_stored_by_category[item.item_abstract.category.name] = []
        items_stored_by_category[item.item_abstract.category.name].append(item.item_abstract)
    print(str(items_stored_by_category))
    return items_stored_by_category

def transform_priority_to_integer(priority):
    if priority == 'low':
        req_priority = 1
    elif priority == 'medium':
        req_priority = 2
    else:
        req_priority = 3
    return req_priority


def getTotalWeight(orderID):
    sumWeight = 0.0
    # ID of all ordered items from current order
    for i in Ordered_Item.objects.filter(order = orderID.id):
        # Find its weight
        sumWeight += Item.objects.get(name = i.item.name).weight * i.quantity
    return sumWeight

def generateCSV(content):
    csvData = [['Person', 'Age'], ['Peter', '22'], ['Jasmine', '21'], ['Sam', '24']]

    with open('asp/static/asp/person.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)

    csvFile.close()

