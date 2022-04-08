"""
When this code was created only God and I knew how it works, now only God knows.

GoodLuck and may the force be with you.
"""
import os
import re
import json
import requests
import pandas as pd
import numpy as np

settlements_map = {
        '':0,
        'spot': 1,
        '24hs': 2,
        '48hs': 3}

call_put_map = {
        0: '',
        1: 'CALL',
        2: 'PUT'}

s = requests.Session()
host="tt"
securities_columns = ['symbol', 'settlement', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'group']
filter_columns = ['Symbol', 'Term', 'BuyQuantity', 'BuyPrice', 'SellPrice', 'SellQuantity', 'LastPrice', 'VariationRate', 'StartPrice', 'MaxPrice', 'MinPrice', 'PreviousClose', 'TotalAmountTraded', 'TotalQuantityTraded', 'Trades', 'TradeDate', 'Panel']
numeric_columns = ['last', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_size', 'bid', 'ask_size', 'ask', 'previous_close']
numeric_columns_sp = ['last', 'high', 'low','change']
filter_columns_sp = ['Symbol', 'LastPrice', 'VariationRate', 'MaxPrice', 'MinPrice', 'Panel']
sp_columns=['symbol','last','change','high','low','group']

def convert_to_numeric_columns(df, columns):
    for col in columns:
        df[col] = df[col].apply(lambda x: x.replace('.', '').replace(',','.') if isinstance(x, str) else x)
        df[col] = pd.to_numeric(df[col].apply(lambda x: np.nan if x == '-' else x))
    return df

class SHD:

    def catcher_connect(site,dni,user,password):
        global host
        host=site
        headers = {
            "Host" : f"{host}",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language" : "en-US,en;q=0.5",
            "Accept-Encoding" : "gzip, deflate",
            "DNT" : "1",    
            "Connection" : "keep-alive",    
            "Upgrade-Insecure-Requests" : "1",
            "Sec-Fetch-Dest" : "document",
            "Sec-Fetch-Mode" : "navigate",
            "Sec-Fetch-Site" : "none",
            "Sec-Fetch-User" : "?1"   
        }


        response = s.get(url = f"https://{host}", headers=headers)
        status = response.status_code
        if status != 200:
          print("login status", status)  
          exit()
        headers = {
            "Host" : f"{host}",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language" : "en-US,en;q=0.5",
            "Accept-Encoding" : "gzip, deflate",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Origin" : f"https://{host}/",
            "DNT" : "1",    
            "Connection" : "keep-alive",
            "Referer" : f"https://{host}/",
            "Upgrade-Insecure-Requests" : "1",
            "Sec-Fetch-Dest" : "document",
            "Sec-Fetch-Mode" : "navigate",
            "Sec-Fetch-Site" : "same-origin",
            "Sec-Fetch-User" : "?1",
            "TE" : "trailers"
        }

        data = {
            "IpAddress": "",
            "Dni": dni,
            "Usuario": user,
            "Password": password
        }  

        response = s.post(url = f"https://{host}/Login/Ingresar", headers=headers, data = data, allow_redirects=False)
        status = response.status_code
        if status != 302:
            print("login status", status)  
            exit()
        print("Connected!")

    def get_bluchips(settlement):
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }
        if settlement=="48hs":
            data = '{"panel":"accionesLideres","term":"3"}'
        if settlement=="24hs":
            data = '{"panel":"accionesLideres","term":"2"}'
        if settlement=="spot":
            data = '{"panel":"accionesLideres","term":"1"}'

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[filter_columns].copy()
        df.columns = securities_columns
        df = convert_to_numeric_columns(df, numeric_columns)
        df.settlement=settlement
        return df

    def get_bonds(settlement):
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        if settlement=="48hs":
            data = '{"panel":"rentaFija","term":"3"}'
        if settlement=="24hs":
            data = '{"panel":"rentaFija","term":"2"}'
        if settlement=="spot":
            data = '{"panel":"rentaFija","term":"1"}'

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[filter_columns].copy()
        df.columns = securities_columns
        df = convert_to_numeric_columns(df, numeric_columns)
        df.settlement=settlement
        return df

    def get_galpones(settlement):
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        if settlement=="48hs":
            data = '{"panel":"panelGeneral","term":"3"}'
        if settlement=="24hs":
            data = '{"panel":"panelGeneral","term":"2"}'
        if settlement=="spot":
            data = '{"panel":"panelGeneral","term":"1"}'

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[filter_columns].copy()
        df.columns = securities_columns
        df = convert_to_numeric_columns(df, numeric_columns)
        df.settlement=settlement
        return df

    def get_MERV():
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"indices","term":""}'

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        #df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        #df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[filter_columns_sp].copy()
        df.columns = sp_columns
        df = convert_to_numeric_columns(df, numeric_columns_sp)
        return df

    def get_cedear(settlement):
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        if settlement=="48hs":
            data = '{"panel":"cedears","term":"3"}'
        if settlement=="24hs":
            data = '{"panel":"accionesLideres","term":"2"}'
        if settlement=="spot":
            data = '{"panel":"accionesLideres","term":"1"}'

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[filter_columns].copy()
        df.columns = securities_columns
        df = convert_to_numeric_columns(df, numeric_columns)
        df.settlement=settlement
        return df

    def get_options():
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{host}",
            "Origin" : f"https://{host}",
            "Referer" : f"https://{host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"opciones","term":"''"}'

        _filter_columns = ['Symbol', 'BuyQuantity', 'BuyPrice', 'SellPrice', 'SellQuantity', 'LastPrice', 'VariationRate', 'StartPrice', 'MaxPrice', 'MinPrice', 'PreviousClose', 'TotalAmountTraded', 'TotalQuantityTraded', 'Trades', 'TradeDate', 'MaturityDate', 'StrikePrice', 'PutOrCall', 'Issuer']
        _numeric_columns = ['last', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_size', 'bid', 'ask_size', 'ask', 'previous_close', 'strike']
        _options_columns = ['symbol', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'expiration', 'strike', 'kind', 'underlying_asset']

        response = s.post(url = f"https://{host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')

        if not df.empty:
            df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
            df.MaturityDate = pd.to_datetime(df.MaturityDate, format='%Y%m%d', errors='coerce')
            df.PutOrCall = df.PutOrCall.apply(lambda x: call_put_map[x] if x in call_put_map else call_put_map[0])

            df = df[_filter_columns].copy()
            df.columns = _options_columns

            df = convert_to_numeric_columns(df, _numeric_columns)
            df = df[df.strike > 0].copy() # Remove non options rows

        else:
            df = pd.DataFrame(columns=_options_columns).set_index(['symbol'])

        return df
    

class foreign_data:
    def get(tickers):
        url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
        #url += str(Tickers)
        headers = {
                "Accept"  :  "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding"  :  "gzip, deflate, br",
                "Accept-Language"  :  "en-US,en;q=0.5",
                "Cache-Control"  :  "no-cache",
                "Connection"  :  "keep-alive",
                "DNT"  :  "1",
                "Host"  :  "query1.finance.Yahoo.com",
                "Pragma"  :  "no-cache",
                "Upgrade-Insecure-Requests"  :  "1",
                "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0"  }


        response = requests.get(url = url+tickers, headers = headers)
        status = response.status_code
        if status != 200:
            print ("Yahoo no retorno status=200:", status)

        result = json.loads(response.text)
        df = pd.DataFrame(result["quoteResponse"]["result"])
        columns=['description','symbol','Exchange' , 'bid', 'ask', 'last', 'high', 'low', 'change', 'volume', 'previousclose']


        filter_columns=['shortName',"symbol",'fullExchangeName', 'bid', 'ask', "regularMarketPrice", "regularMarketDayHigh", "regularMarketDayLow", "regularMarketChangePercent", "regularMarketVolume", "regularMarketPreviousClose"]
        df = df[filter_columns].copy()
        #df['regularMarketTime'] = pd.to_datetime(df['regularMarketTime'], unit='s')
        df.columns = columns
        df.change=df.change/100
        return df
