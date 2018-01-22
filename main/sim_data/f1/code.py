import os, django, sys
sys.path.append('/var/www/stockAnalyzeWeb')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockAnalyzeWeb.settings")
django.setup()

from main.models import *
import random as rand
import time

def run(suite=0):
    try:
        sim = Simulation.objects.get(num=1)
        sim.delete()
        with open('/var/www/stockAnalyzeWeb/main/sim_data/f1/log.txt', 'w') as f:
            f.write('suite : ' + str(suite) + '\n')
    except Exception as e:
        pass

    sim = Simulation()
    sim.num = 1
    sim.name = 'Random walk for testing'
    sim.detail = 'Random walk with probabilitiy=50%'
    sim.progress = 0.0
    sim.save()

    chart = Chart(sim=sim, name='random walk')
    chart.save()

    y = 0

    for x in range(1000):
        if rand.random() < 0.5:
            y += 1
        else:
            y -= 1
        data = FfData(chart=chart, x=x, y=y)
        data.save()

        sim.progress = (x+1) / 1000 * 100
        sim.save()

        with open('/var/www/stockAnalyzeWeb/main/sim_data/f1/log.txt', 'a') as f:
            f.write(str(x) + ' : ' + str(y) + str('\n'))

        time.sleep(0.01)

run()
