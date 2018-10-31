from asp.models import Category, Available_Item, UserExt

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
