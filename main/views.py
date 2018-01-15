from django.shortcuts import render
from django.http import JsonResponse
from .models import * 
import pandas as pd
import math
from datetime import *
from . import stuff
import json
import os

# Create your views here.

def index(request):
    ctx = {}
    ctx['Companies'] = Company.objects.all()
    today = stuff.MyDate.fromfile('/var/www/stockAnalyzeWeb/main/data/today.txt')
    ctx['Today'] = today.__str__() 
    ctx['TodayShort'] = today.__str__()[2:]
    ctx['y_items'] = ['sales', 'biz_profit', 'net_profit', 'consol_net_profit', 'tot_asset', 'tot_debt', 'tot_capital']

    return render(request, 'main/index.html', ctx)

def strategy(request):
    ctx = {}
    ctx['sims'] = Simulation.objects.all().order_by('-num')
    return render(request, 'main/strategy.html', ctx)

def strategy_detail(request, num):
    ctx = {}
    ctx['sim'] = Simulation.objects.get(num=num)

    return render(request, 'main/strategy-detail.html', ctx)

def get_charts(request, num):
    ret = {}
    sim = Simulation.objects.get(num=num)
    charts = sim.chart_set.all()
    i = -1
    for c in charts:
        i += 1
        ret[i] = {}
        if c.ffdata_set.all().count() > 0:
            data = c.ffdata_set.all().order_by('x')
            ret[i]['xs'] = []
            ret[i]['ys'] = []
            for d in data:
                ret[i]['xs'].append(d.x)
                ret[i]['ys'].append(d.y)
        elif c.sfdata_set.all().count() > 0:
            data = c.sfdata_set.all().order_by('x')
            ret[i]['xs'] = []
            ret[i]['ys'] = []
            for d in data:
                ret[i]['xs'].append(d.x)
                ret[i]['ys'].append(d.y)

        elif c.sffdata_set.all().count() > 0:
            data = c.sffdata_set.all().order_by('x')
            ret[i]['xs'] = []
            ret[i]['ys'] = []
            ret[i]['y2s'] = []
            for d in data:
                ret[i]['xs'].append(d.x)
                ret[i]['ys'].append(d.y)
                ret[i]['y2s'].append(d.y2)

        ret[i]['name'] = c.name
    return JsonResponse(ret)


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
