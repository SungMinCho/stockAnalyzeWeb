from datetime import *
from pandas import *

def human_readable_float(f):
    save_f = f
    if f < 0:
        f = -f
    s = ""
    q = f // 100000000
    if q > 0:
        s += str(int(q)) + '억'

    f = f % 100000000
    q = f // 10000
    if q > 0:
        s += str(int(q)) + '만'

    f = f % 10000
    f = int(f)
    s += str(f) + '원'
    if save_f < 0:
        s = '-' + s
    return s

class MyDate:
    def __init__(self,s):
        self.s = s
        self.date = datetime.strptime(s, '%Y-%m-%d').date()
    def __str__(self):
        return self.s
    def __repr__(self):
        return self.__str__()
    def __add__(self, n):
        return MyDate((self.date + timedelta(days=n)).__str__())
    def __radd__(self, n):
        return self + n
    def __sub__(self, n):
        return self + (-n)
