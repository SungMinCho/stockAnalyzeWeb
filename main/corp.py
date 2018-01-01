import crawl as cw
import os
from datetime import *
import math
import pandas as pd


class Corp:
    slippage = 0.005
    tax = 0.003
    def __init__(self, _name, _code, start=date.fromordinal(date.today().toordinal()-365*5), end=date.today()):
        loadingMode = True
        try:
            #print('loading ' + _name + " " + _code)
            self.name = _name
            self.code = _code
            self.loading_success = False
            if loadingMode and os.path.isfile(os.path.join('data', _code + '_failed')):
                return
            if loadingMode and os.path.isfile(os.path.join('data', _code + '_prices')):
                self.prices = pd.read_pickle(os.path.join('data', _code+'_prices')) # only works because i fixed the start and end date
                self.loading_success = True
            else:
                for i in range(10):
                    try:
                        self.prices = cw.get_stock(_code, start, end)
                        self.prices.to_pickle(os.path.join('data', _code+'_prices'))
                        self.loading_success = True
                        break
                    except Exception as e:
                        #print('price loading error, trying again')
                        pass
            if not self.loading_success:
                f = open(os.path.join('data', _code + '_failed'), 'w')
                f.write('x')
                f.close()
                return
            else:
                self.loading_success = False

            if loadingMode and os.path.isfile(os.path.join('data', _code + '_fundByYear')):
                self.fundByYear = pd.read_pickle(os.path.join('data', _code + '_fundByYear'))
            else:
                self.fundByYear = cw.get_fund_byYear(_code.split('.')[0])
                self.fundByYear.to_pickle(os.path.join('data', _code+'_fundByYear'))


            if loadingMode and os.path.isfile(os.path.join('data', _code + '_fundByQuarter')):
                self.fundByQuarter = pd.read_pickle(os.path.join('data', _code + '_fundByYear'))
            else:
                self.fundByQuarter = cw.get_fund_byQuarter(_code.split('.')[0])
                self.fundByQuarter.to_pickle(os.path.join('data', _code+'_fundByQuarter'))
            self.loading_success = True
            #print('loading succesful')
        except Exception as e:
            f = open(os.path.join('data', _code + '_failed'), 'w')
            f.write('x')
            f.close()
            #print('loading failed')

    def get_recent_fund(self, t, index):
        try:
            # we'll use only fundByYear for now
            cols = self.fundByYear.columns
            for c in reversed(cols):
                year = c.split('(')[0].split('/')[0]
                month = c.split('(')[0].split('/')[1]
                dt = datetime(int(year), int(month), 1)
                if type(dt) != type(t):
                    dt = datetime.date(dt)
                if dt <= t:
                    return self.fundByYear.ix[index][c]
            return None
        except Exception as e:
            return None

    def get_price(self, t):
        return self.prices.ix[t]

    def get_adjc(self, t):
        try:
            ret = self.prices.ix[t]['Adj Close']
            if math.isnan(ret):
                return None
            return ret
        except Exception as e:
            return None

    def get_recent_adjc(self, t):
        for n in range(15): # look back at most 4 days
            p = self.get_adjc(t - timedelta(n))
            if p:
                return p
        return None

    def get_buy_price(self, t):
        p = self.get_adjc(t)
        if math.isnan(p):
            print('debug nan1')
        if p:
            if math.isnan(p*(1+Corp.slippage)):
                print('debug nan2', p, 1+Corp.slippage)
            return p*(1+Corp.slippage)
        else:
            return None

    def get_sell_price(self, t):
        p = self.get_adjc(t)
        if p:
            return p*(1-Corp.slippage-Corp.tax)
        else:
            return None

    def get_recent_sell_price(self, t):
        for n in range(15): # look back at most 14 days
            p = self.get_sell_price(t - timedelta(n))
            if p:
                return p
        return None
        

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code

    def can_trade(self, t):
        return (self.get_adjc(t) != None)

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return not(self == other)


def main():
    c = Corp('test','005930.KS') 
    print(c.get_recent_fund(datetime.today(), '매출액'))

if __name__ == "__main__":
    main()
