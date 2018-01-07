from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as bs
import pandas as pd

def get_html(ticker, freq='a'):
    if freq=="a":
        fs_url = "http://www.sejongdata.com/business_include_fr/table_main0_bus_01.html?no="+ ticker + "&gubun=2"
    elif freq=='q':
        fs_url = "http://www.sejongdata.com/business_include_fr/table_main0_bus_02.html?no=" + ticker
    else:
        return None

    req = Request(fs_url,headers={'User-Agent': 'Mozilla/5.0'})
    html_text = urlopen(req).read()
    return html_text

def ext_fin(ticker, item, n, freq):
    html_text = get_html_sejong_fs(ticker, freq)
    soup = bs(html_text, 'lxml')
    d = soup.find(text=item)
    d_ = d.find_all_next(class_="bus_board_txt1")

    ndata = 12 if freq == "q" else 10
    
    data = d_[(ndata-n):ndata]
    v = [v.text for v in data]
    return v

def get_fin_table(ticker, freq="a"):
    try:
        if freq == "a":
            fs_url = "http://www.sejongdata.com/business_include_fr/table_main0_bus_01.html?no="+ ticker + "&gubun=2" 
            df = pd.read_html(fs_url, encoding='utf-8')[1] 
            df = df.T
        elif freq == "q":
            fs_url = "http://www.sejongdata.com/business_include_fr/table_main0_bus_02.html?no=" + ticker 
            df = pd.read_html(fs_url, encoding='utf-8')
        else:
            fs_url = None
            df = None
    except AttributeError as e:
        return None

    return df
