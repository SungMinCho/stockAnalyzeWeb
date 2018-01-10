from stockAnalyzeWeb.wsgi import *
from pandas import *
from main.models import * 
from main.sejong import *

def saver(ks):
    for index, r in ks.iterrows():

        code = r['종목코드']

        pwd = '/var/www/stockAnalyzeWeb/main/data'

        c = Company(market='kospi', name=r['회사명'], code=r['종목코드'], category=r['업종'], products=r['주요제품'], listedDate=r['상장일'], settlementMonth=r['결산월'], representative=r['대표자명'], homepage=r['홈페이지'], area=r['지역'], prices=os.path.join(pwd, code+'.KS_prices'), fundY=os.path.join(pwd, code+'.KS_fundByYear'), fundQ=os.path.join(pwd, code+'.KS_fundByQuarter'))
        c.save()


def pricestablesaver():
    counter = 0
    for c in Company.objects.all():
        counter += 1
        print('\r       ', end='')
        print(counter, end='')
        try:
            p = read_pickle('/var/www/stockAnalyzeWeb/main/data/' + c.code + '.KS_prices')
            for index, row in p.iterrows():
                d = str(index).split(' ')[0],
                if Price.objects.filter(company=c).filter(date=d).count() > 0:
                    continue
                pt = Price(company=c,
                        date=d,
                        open = row['Open'],
                        close = row['Close'],
                        high = row['High'],
                        low = row['Low'],
                        adjclose = row['Adj Close'],
                        volume = row['Volume'])
                pt.save()
        except Exception as e:
            print(e, end='')

def fund_y_saver():
    counter = 0
    for c in Company.objects.all():
        counter += 1
        if c.code == '^KS11':
            continue
        print('\r                                             ', end='')
        print('\r'+str(counter), end='')
        try:
            p = get_fin_table(c.code)
            for index, r in p.iterrows():
                if index == 0:
                    continue
                try:
                    d = r[0].split(' ')[0].replace('.', '-') + '-01'
                    if Fund_y.objects.filter(company=c).filter(date=d).count() > 0:
                        continue
                    fundy = Fund_y(company=c,
                            date=d,
                            sales=r[1],
                            biz_profit=r[2],
                            net_profit=r[3],
                            consol_net_profit=r[4],
                            tot_asset=r[5],
                            tot_debt=r[6],
                            tot_capital=r[7])
                    fundy.save()
                except Exception as e:
                    pass
        except Exception as e:
            print(e, end='')

def fund_q_saver():
    counter = 0
    for c in Company.objects.all():
        counter += 1
        if c.code == '^KS11':
            continue
        print('\r                                             ', end='')
        print('\r'+str(counter), end='')
        try:
            p = get_fin_table(c.code, 'q')
            p = p[0].T
            for index, r in p.iterrows():
                if index == 0:
                    continue
                try:
                    d = r[0].split(' ')[0].replace('.', '-') + '-01'
                    if Fund_q.objects.filter(company=c).filter(date=d).count() > 0:
                        continue
                    fundq = Fund_q(company=c,
                            date=d,
                            sales=r[1],
                            biz_profit=r[2],
                            net_profit=r[3],
                            consol_net_profit=r[4])
                    fundq.save()
                except Exception as e:
                    pass
        except Exception as e:
            print(e, end='')

def main():
    fund_y_saver()
    fund_q_saver()

