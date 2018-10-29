from django.db import models

# Create your models here.

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

    role = models.CharField(
        max_length = 2,
        choices = ROLES,
        default = CLINIC_MANAGER
    )

    def __str__(self):
        return f"{self.username}: {self.role}"

class Item(models.Model):
    name = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200)
    weight = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name}"

class Ordered_Item(models.Model):
    item = models.OneToOneField(Item, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item}, {self.quantity}"

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
    priority = models.PositiveIntegerField(default = 1)
    ref_no = models.PositiveIntegerField(unique = True)
    items = models.ManyToManyField(Ordered_Item)

    def __str__(self):
        return f"{self.ref_no}, {self.status}"
                
