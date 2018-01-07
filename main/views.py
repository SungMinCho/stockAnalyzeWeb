from django.shortcuts import render
from django.http import JsonResponse
from .models import * 
import pandas as pd
import math
from datetime import *
from . import stuff

# Create your views here.

def index(request):
    ctx = {}
    ctx['Companies'] = Company.objects.all()
    today = stuff.MyDate.fromfile('/var/www/stockAnalyzeWeb/main/data/today.txt')
    ctx['Today'] = today.__str__() 
    ctx['TodayShort'] = today.__str__()[2:]

    return render(request, 'main/index.html', ctx)

def strategy(request):
    return render(request, 'main/index.html', {}) # temp

def logout_user(request):
    return render(request, 'main/index.html', {}) # temp

def get_prices(request, code, date):
    c = Company.objects.get(code=code)
    #prices = pd.read_pickle(c.prices)
    prices = c.price_set.all()
    ret = {}
    for price in prices:
        ret[price.date] = price.adjclose
    #for index, row in prices.iterrows():
    #    ret[str(index).split(' ')[0]] = row['Adj Close']

    return JsonResponse(ret)

def detail(request, code):
    return render(request, 'main/detail.html', {'code':code})


def price_change(request, code, date):
    if code == 'all':
        codes = [c.code for c in Company.objects.all()]
    else:
        codes = [code]
    ret = {}
    d = stuff.MyDate(date)
    for c in codes:
        ret[c] = stuff.price_change(c, d)
    return JsonResponse(ret)


def fund_info(request, code, date, freq, item):
    if code == 'all':
        codes = [c.code for c in Company.objects.all()]
    else:
        codes = [code]
    ret = {}
    for c in codes:
        ret[c] = stuff.fund_info(c, date, freq, item)
    return JsonResponse(ret)
