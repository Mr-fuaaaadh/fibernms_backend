import uuid

from django.db import models


class Company(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('suspended', 'Suspended'),
    ]
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    region = models.CharField(max_length=100)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='trial')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'saas_companies'

    def __str__(self):
        return self.name