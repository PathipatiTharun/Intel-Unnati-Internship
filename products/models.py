# products/models.py
from django.db import models

class Product(models.Model):
    device_id = models.CharField(max_length=100)
    batch_id = models.CharField(max_length=100)
    manufacturing_date = models.DateField()
    rohs_compliance = models.BooleanField(default=False)
    serial_number = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.device_id} - {self.serial_number}"
