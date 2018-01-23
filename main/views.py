from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import * 
import pandas as pd
import math
from datetime import *
from . import stuff
import json
import os
import subprocess
import sys
import shutil

# Create your views here.

@login_required
def index(request):
    ctx = {}
    ctx['Companies'] = Company.objects.all()
    today = stuff.MyDate.fromfile('/var/www/stockAnalyzeWeb/main/data/today.txt')
    ctx['Today'] = today.__str__() 
    ctx['TodayShort'] = today.__str__()[2:]
    ctx['y_items'] = ['sales', 'biz_profit', 'net_profit', 'consol_net_profit', 'tot_asset', 'tot_debt', 'tot_capital']

    return render(request, 'main/index.html', ctx)

@login_required
def edit(request):
    ctx = {}
    return render(request, 'main/edit.html', ctx)

@login_required
def strategy(request):
    ctx = {}
    ctx['sims'] = Simulation.objects.all().order_by('-num')
    return render(request, 'main/strategy.html', ctx)

@login_required
def add_strategy(request):
    num = Simulation.objects.all().latest('num').num
    num += 1
    s = Simulation()
    s.num = num
    s.name = "New strategy"
    s.detail = "New strategy created"
    s.progress = 0.0
    s.save()
    pth = '/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num)
    os.mkdir(pth, 0o777)

    codepth = pth + '/code.py'
    with open('/var/www/stockAnalyzeWeb/main/sim_data/codeTemplate.py', 'r', encoding='utf-8') as codef:
        code = codef.read()
        code = code.replace('NUM', str(num))
        with open(codepth, 'w') as writecode:
            writecode.write(code)
        os.chmod(codepth, 0o777)
    return redirect('main:strategy')

@login_required
def delete_strategy(request, num):
    Simulation.objects.get(num=num).delete()
    shutil.rmtree('/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num))
    return redirect('main:strategy')


@login_required
def strategy_detail(request, num):
    ctx = {}
    ctx['sim'] = Simulation.objects.get(num=num)
    try:
        with open('/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num) + '/code.py', 'r') as f:
            ctx['code'] = f.read()
    except Exception as e:
        ctx['error'] = str(e)


    return render(request, 'main/strategy-detail.html', ctx)

@login_required
def get_file(request):
    if request.method == "POST" and request.is_ajax():
        try:
            path = request.POST['path']
            with open(os.path.join('/var/www/stockAnalyzeWeb', path), 'r', encoding='utf-8') as f:
                txt = f.read()
                ret = {}
                ret['value'] = txt
                return JsonResponse(ret)
        except Exception as e:
            ret = {}
            ret['value'] = str(e)
            return JsonResponse(ret)
    else:
        return HttpResponse("Bad")

@login_required
def set_file(request):
    if request.method == "POST" and request.is_ajax():
        try:
            txt = request.POST['txt']
            path = request.POST['path']
            with open(os.path.join('/var/www/stockAnalyzeWeb', path), 'w', encoding='utf-8') as f:
                f.write(txt)
            return HttpResponse("Success")
        except Exception as e:
            return HttpResponse(str(e))
    else:
        return HttpResponse("Bad")


@login_required
def save_code(request, num):
    if request.method == "POST" and request.is_ajax():
        txt = request.POST['txt']
        with open('/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num) + '/code.py', 'w') as f:
            f.write(txt)
        return HttpResponse("Success")
    else:
        return HttpResponse("Bad")

@login_required
def run_code(request, num):
    if request.method == "POST" and request.is_ajax():
        pth = '/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num) + '/code.py'
        errpth = '/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num) + '/error.txt'
        try:
            #exec(open(pth, encoding='utf-8').read(), globals())
            with open(errpth, 'w') as err:
                p = subprocess.Popen([sys.executable, pth], stderr=err)
            return HttpResponse("Exec started")
        except Exception as e:
            return HttpResponse(str(e))
    else:
        return HttpResponse("Bad")

@login_required
def get_log(request, num):
    s = ""
    try:
        with open('/var/www/stockAnalyzeWeb/main/sim_data/f' + str(num) + '/log.txt', 'r', encoding='utf-8') as f:
            s = f.read()
    except Exception as e:
        s = 'get_log_error : ' + str(e)
    return JsonResponse({'log':s})

@login_required
def get_progress(request, num):
    sim = Simulation.objects.get(num=num)
    ret = {}
    ret['value'] = sim.progress
    return JsonResponse(ret)

@login_required
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

@login_required
def logout_user(request):
    return render(request, 'main/index.html', {}) # temp

@login_required
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

@login_required
def detail(request, code):
    return render(request, 'main/detail.html', {'code':code})


@login_required
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

@login_required
def fund_info(request, code, date, freq, item):
    if code == 'all':
        codes = [c.code for c in Company.objects.all()]
    else:
        codes = [code]
    ret = {}
    for c in codes:
        ret[c] = stuff.fund_info(c, date, freq, item)
    return JsonResponse(ret)
