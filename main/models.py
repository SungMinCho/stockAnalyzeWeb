from django.db import models

# Create your models here.
class Company(models.Model):
    market = models.CharField(max_length=10)
    name = models.CharField(max_length=40)
    code = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    products = models.CharField(max_length=300)
    listedDate = models.CharField(max_length=30)
    settlementMonth = models.CharField(max_length=10)
    representative = models.CharField(max_length=30)
    homepage = models.CharField(max_length=30)
    area = models.CharField(max_length=30)
    prices = models.CharField(max_length=30)
    fundY = models.CharField(max_length=30)
    fundQ = models.CharField(max_length=30)

    def __str__(self):
        return self.name + self.code
