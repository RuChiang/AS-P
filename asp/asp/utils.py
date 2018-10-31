from asp.models import Category, Item, UserExt, Ordered_Item, Available_Item

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

def getTotalWeight(orderID):
    sumWeight = 0.0
    # ID of all ordered items from current order
    for i in Available_Item.objects.filter(order_id = orderID).values('item'):
        # Find its weight
        # sumWeight += Item.objects.get(name = i['item']).weight
        sumWeight += Item.objects.filter(name = i['item'])[0].weight
    return sumWeight

def generateCSV():
    pass