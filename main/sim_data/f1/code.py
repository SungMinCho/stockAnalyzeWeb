from main.models import *
import random as rand

sim = Simulation.objects.get(num=1)

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
