from datetime import *
from pandas import *
from .models import *
from .crawl import *
from pandas_datareader import data as pdr

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
    def __eq__(self, other):
        return self.s == other.s
    def __ne__(self, other):
        return not (self == other)
    def __lt__(self, other):
        return self.date < other.date
    def __le__(self, other):
        return (self == other) or self < other
    def __gt__(self, other):
        return other < self
    def __ge__(self, other):
        return other <= self
    def __hash__(self):
        return hash(self.s)

    def today():
        return MyDate(datetime.today().__str__().split(' ')[0])
    def fromfile(f='/var/www/stockAnalyzeWeb/main/data/today.txt'):
        f = open(f, 'r')
        s = f.readline().strip()
        f.close()
        return MyDate(s)
    def tofile(self, f='/var/www/stockAnalyzeWeb/main/data/today.txt'):
        f = open(f, 'w')
        f.write(self.__str__())
        f.close()

def price_change(code, date):
    c = Company.objects.get(code=code)
    p = c.price_set
    newprice = None
    for n in range(15):
        try:
            newprice = p.get(date=date-n).adjclose
            break
        except Exception as e:
            pass
    if newprice == None:
        return 'X'

    oldprice = None
    for m in range(n+1, 20):
        olddate = date-m
        try:
            oldprice = p.get(date=olddate).adjclose
            break
        except Exception as e:
            pass
    if oldprice == None:
        return 'X'
    diff = (newprice - oldprice) / oldprice * 100
    ret = '+{:.2f}%'.format(diff)
    if diff < 0:
        ret = ret[1:]
    return ret

def update_prices(todate=MyDate.today()):
    i = 0
    origin = MyDate('2012-12-03')
    for c in Company.objects.all():
        i += 1
        print('\r                                                                   ', end='')
        print('\r' + ' '*100, end='')
        print('\r'+str(i), end='')
        try:
            try:
                fromdate = MyDate(c.price_set.latest('date').date)
                fromdate = fromdate + 1
                if MyDate(c.price_set.earliest('date').date) > origin:
                    fromdate = origin
            except Exception as e:
                fromdate = origin
            if fromdate >= todate:
                continue
            print('date ', fromdate, todate)
            for getn in range(5):
                try:
                    p = get_kospi(c.code, fromdate.date, todate.date)
                    break
                except Exception as e:
                    pass
            for index, row in p.iterrows():
                try:
                    pt = Price(company=c,
                            date=str(index).split(' ')[0],
                            open = row['Open'],
                            close = row['Close'],
                            high = row['High'],
                            low = row['Low'],
                            adjclose = row['Adj Close'],
                            volume = row['Volume'])
                    pt.save()
                except Exception as e:
                    pass
        except Exception as e:
            print('\r'+str(e), end='')
    todate.tofile()

def fund_info(code, date_, freq, item):
    if freq == 'a':
        table = Company.objects.get(code=code).fund_y_set
    else:
        table = Company.objects.get(code=code).fund_q_set
    try:
        row = table.filter(date__lt=date_).latest('date')
        ret = getattr(row, item)
        return ret
    except Exception as e:
        return 'X'
