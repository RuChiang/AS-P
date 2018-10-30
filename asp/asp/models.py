from django.db import models

# Create your models here.


class Hospital(models.Model):
    SUPPLY='SP'
    DEMAND='DM'
    ROLES = (
        (SUPPLY, 'Supplying Hospital'),
        (DEMAND, 'Demanding Hospital')
    )
    name = models.CharField(max_length = 200)
    latitude = models.FloatField()
    longtitude = models.FloatField()
    altitude = models.FloatField()
    role = models.CharField(
        max_length = 2,
        choices = ROLES,
        default = DEMAND
    )

    def __str__(self):
        return f"{self.name}"

class User(models.Model):
    CLINIC_MANAGER = 'CM'
    DISPATCHER = 'DP'
    WAREHOUSE_PERSONNEL = 'WP'
    ADMIN = 'AD'
    ROLES = (
        (CLINIC_MANAGER, 'Clinic Manager'),
        (DISPATCHER, 'Dispatcher'),
        (WAREHOUSE_PERSONNEL, 'Warehouse Personnel'),
        (ADMIN, 'Admin')
    )

    username = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 254)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    role = models.CharField(
        max_length = 2,
        choices = ROLES,
        default = CLINIC_MANAGER
    )

    def __str__(self):
        return f"{self.username}: {self.role}"


class Item(models.Model):
    name = models.CharField(max_length = 200)
    supplying_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    category = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200)
    weight = models.PositiveIntegerField(default = 0)
    quantity = models.PositiveIntegerField(default = 0)

    def __str__(self):
        return f"{self.name}, {self.category}"


# distance is only stored on one side
class Distance(models.Model):
    distance = models.FloatField()
    host_a = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name = 'from_host')
    host_b = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name = 'to_host')

    def __str__(self):
        return f"{self.host_a} -> {self.host_b} : {self.distance}"

# no need to generate ref_no for it cuz it has its unique pk already
class Order(models.Model):
    QUEUED_FOR_PROCESSING = 'QFP'
    PROCESSING_BY_WAREHOUSE = 'PBW'
    QUEUED_FOR_DISPATCH = 'QFD'
    DISPATCHED = 'DSD'
    DELIVERED = 'DLD'

    STATUS = (
        (QUEUED_FOR_PROCESSING, 'Queued for Processing'),
        (PROCESSING_BY_WAREHOUSE, 'Processing by Warehouse'),
        (QUEUED_FOR_DISPATCH, 'Queued for Dispatched'),
        (DISPATCHED, 'Dispatched'),
        (DELIVERED, 'Delivered')
    )

    status = models.CharField(
        max_length = 3,
        choices = STATUS,
        default = QUEUED_FOR_PROCESSING
    )

    requester = models.ForeignKey(User, on_delete = models.CASCADE)
    time = models.DateTimeField()
    # 1 being LOW and 3 being HIGH
    priority = models.PositiveIntegerField(default = 1)
    def __str__(self):
        return f"{self.id}, {self.status}"


class Ordered_Item(models.Model):
    item = models.CharField(max_length = 200)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.item}, {self.quantity}"
