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

class Price(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    open = models.FloatField(default=0.0)
    close = models.FloatField(default=0.0)
    high = models.FloatField(default=0.0)
    low = models.FloatField(default=0.0)
    adjclose = models.FloatField(default=0.0)
    volume = models.FloatField(default=0.0)

class Fund_y(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.CharField(max_length=20)
    sales = models.FloatField(default=0.0)
    biz_profit = models.FloatField(default=0.0)
    net_profit = models.FloatField(default=0.0)
    consol_net_profit = models.FloatField(default=0.0)
    tot_asset = models.FloatField(default=0.0)
    tot_debt = models.FloatField(default=0.0)
    tot_capital = models.FloatField(default=0.0)

