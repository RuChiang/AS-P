from django.db import models
from django.contrib.auth.models import User

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

class UserExt(models.Model):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    role = models.CharField(
        max_length = 2,
        choices = ROLES,
        default = CLINIC_MANAGER
    )

    def __str__(self):
        return f"{self.user.username}: {self.role}"

class Category(models.Model):
    name = models.CharField(max_length = 200)

    def __str__(self):
        return f"{self.name}"


class Item(models.Model):
    name = models.CharField(max_length = 200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length = 200)
    weight = models.FloatField(default = 0)
    # image = models.ImageField(null = True)

    def __str__(self):
        return f"Category: {self.category.name} | Name: {self.name}"

class Available_Item(models.Model):
    item_abstract = models.ForeignKey(Item, on_delete=models.CASCADE)
    supplying_hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default = 0)

    def __str__(self):
        return f"Name: {self.item_abstract.name} | Supplying_Hospital: {self.supplying_hospital.name} | Quantity: {self.quantity}"


# distance is only stored on one side
class Distance(models.Model):
    distance = models.FloatField()
    hospital_a = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name = 'from_host')
    hospital_b = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name = 'to_host')

    def __str__(self):
        return f"{self.hospital_a} <-> {self.hospital_b} : {self.distance}"

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
        (QUEUED_FOR_DISPATCH, 'Queued for Dispatch'),
        (DISPATCHED, 'Dispatched'),
        (DELIVERED, 'Delivered')
    )

    status = models.CharField(
        max_length = 3,
        choices = STATUS,
        default = QUEUED_FOR_PROCESSING
    )

    requester = models.ForeignKey(UserExt, on_delete = models.CASCADE)
    # 1 being LOW and 3 being HIGH
    priority = models.PositiveIntegerField(default = 1)
    # All important time stamps for Health Authority
    time_queued_processing = models.DateTimeField()
    time_processing = models.DateTimeField(null = True)
    time_queued_dispatch = models.DateTimeField(null = True)
    time_dispatched = models.DateTimeField(null = True)
    time_delivered = models.DateTimeField(null = True)
    def __str__(self):
        return f"Order_id:{self.id} | Requester: {self.requester.user.username} | Status: {self.status} | Order_placed_at: {self.time_queued_processing}"


class Ordered_Item(models.Model):
    item = models.CharField(max_length = 200)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, on_delete = models.CASCADE)

    def __str__(self):
        return f"Order: {self.order.id} | Name: {self.item} | Quantity: {self.quantity}"
