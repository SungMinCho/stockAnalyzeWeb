from django.shortcuts import render
from django.http import JsonResponse
from .models import Company
import pandas as pd
import math
from datetime import *
from . import stuff

# Create your views here.

def index(request):
    return render(request, 'main/index.html', {'Companies' : Company.objects.all(), 'Today' : date.today(), 'TodayShort' : date.today().strftime('%m-%d')})

def strategy(request):
    return render(request, 'main/index.html', {}) # temp

def logout_user(request):
    return render(request, 'main/index.html', {}) # temp

def get_prices(request, code, date):
    c = Company.objects.filter(code=code)[0]
    prices = pd.read_pickle(c.prices)
    ret = {}
    for index, row in prices.iterrows():
        ret[str(index).split(' ')[0]] = row['Adj Close']
    return JsonResponse(ret)

def detail(request, code):
    return render(request, 'main/detail.html', {'code':code})




