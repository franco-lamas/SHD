"""
When this code was created only God and I knew how it works, now only God knows.

GoodLuck and may the force be with you.
"""
from os import path
import re
import json
import datetime
import requests
import numpy as np
import pandas as pd
from pyquery import PyQuery as pq
from .common import brokers, BrokerNotSupportedException,convert_to_numeric_columns, SessionException



class SHDA:
    __settlements_int_map = {
        '1': 'spot',
        '2': '24hs',
        '3': '48hs'}

    __personal_portfolio_index = ['symbol', 'settlement']
    __personal_portfolio_columns = ['symbol', 'settlement', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'expiration', 'strike', 'kind', 'underlying_asset', 'close']
    __empty_personal_portfolio = pd.DataFrame(columns=__personal_portfolio_columns).set_index(__personal_portfolio_index)

    __repos_index = ['symbol', 'settlement']
    __repos_columns = ['symbol', 'days', 'settlement', 'bid_amount', 'bid_rate', 'ask_rate', 'ask_amount', 'last', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'close']
    __empty_repos = pd.DataFrame(columns=__repos_columns).set_index(__repos_index)


    __call_put_map = {
            0: '',
            1: 'CALL',
            2: 'PUT'}
    __boards = {
            0:"",
            'accionesLideres':'bluechips',
            'panelGeneral':'general_board',
            'cedears': 'cedears',
            'rentaFija':'government_bonds',
            'letes':'short_term_government_bonds',
            'obligaciones':'corporate_bonds'}

    __settlements_map = {'':0,'spot': 1,'24hs': 2,'48hs': 3}
    __securities_columns = ['symbol', 'settlement', 'bid_size', 'bid', 'ask', 'ask_size', 'last', 'change', 'open', 'high', 'low', 'previous_close', 'turnover', 'volume', 'operations', 'datetime', 'group']
    __filter_columns = ['Symbol', 'Term', 'BuyQuantity', 'BuyPrice', 'SellPrice', 'SellQuantity', 'LastPrice', 'VariationRate', 'StartPrice', 'MaxPrice', 'MinPrice', 'PreviousClose', 'TotalAmountTraded', 'TotalQuantityTraded', 'Trades', 'TradeDate', 'Panel']
    __numeric_columns = ['last', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_size', 'bid', 'ask_size', 'ask', 'previous_close']
    __numeric_columns_sp = ['last', 'high', 'low','change']
    __filter_columns_sp = ['Symbol', 'LastPrice', 'VariationRate', 'MaxPrice', 'MinPrice', 'Panel']
    __sp_columns=['symbol','last','change','high','low','group']
    
    def __init__(self,broker,dni,user,password):
        self.__s = requests.session()
        self.__host = self.__get_broker_data(broker)['page']
        self.__is_user_logged_in = False

        headers = {
            "Host" : f"{self.__host}",
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


        response = self.__s.get(url = f"https://{self.__host}", headers=headers)
        status = response.status_code
        if status != 200:
          print("Server Down", status)  
          exit()

        headers = {
            "Host" : f"{self.__host}",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language" : "en-US,en;q=0.5",
            "Accept-Encoding" : "gzip, deflate",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Origin" : f"https://{self.__host}/",
            "DNT" : "1",    
            "Connection" : "keep-alive",
            "Referer" : f"https://{self.__host}/",
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

        try:
            response = self.__s.post(url = f"https://{self.__host}/Login/Ingresar", headers=headers, data = data, allow_redirects=True)

            response.raise_for_status()

            doc = pq(response.text)
            if not doc('#usuarioLogueado'):
                print("Check login credentials")
                errormsg = doc('.callout-danger')
                if errormsg:
                    raise SessionException(errormsg.text())

                raise SessionException('Session cannot be created.  Check the entered information and try again.')

            print("Connected!")
            self.__is_user_logged_in = True
        except Exception as ex:
            self.__is_user_logged_in = False
            exit()

    def get_bluechips(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"accionesLideres","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def get_galpones(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"panelGeneral","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def get_cedear(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"cedears","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def get_bonds(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"rentaFija","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def get_short_term_bonds(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"letes","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def get_corporate_bonds(self,settlement):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"obligaciones","term":"'+str(self.__settlements_map[settlement])+'"}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()
        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = pd.DataFrame(data['Result']['Stocks']) if data['Result'] and data['Result']['Stocks'] else pd.DataFrame()
        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df = df[self.__filter_columns].copy()
        df.columns = self.__securities_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns)
        df.group = df.group.apply(lambda x: self.__boards[x] if x in self.__boards else self.__boards[0])
        df.settlement=settlement 
        return df

    def account(self,comitente):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()

        payload = {'comitente': str(comitente),
            'consolida': '0',
            'proceso': '22',
            'fechaDesde': None,
            'fechaHasta': None,
            'tipo': None,
            'especie': None,
            'comitenteMana': None}

        portfolio = self.__s.post(f"https://{self.__host}/Consultas/GetConsulta",json=payload).json()
        portfolio = portfolio["Result"]["Activos"]
        detailColumns=["IMPO",	"ESPE",	"TESP",	"NERE",	"GTOS",	"DETA",	"TIPO"	,"Hora"	,"AMPL"	,"DIVI"	,"TICK"	,"CANT"	,"PCIO"	,"CAN3"	,"CAN2","CAN0"]
        RowOne=["IMPO",	"ESPE",	"TESP",	"NERE",	"GTOS",	"DETA",	"TIPO"	,"Hora"	,"AMPL"	,"DIVI"	,"TICK"	,"CANT"	,"PCIO"	,"CAN3"	,"CAN2","CAN0"]

        df=pd.DataFrame(portfolio)
        df2=pd.DataFrame(columns=detailColumns)
        df2.at[0,"IMPO"]=df.at[0,"IMPO"]
        df2.at[0,"ESPE"]="Cash"
        if len(df)>0:
            for i in range(1,len(df)):
                df2=pd.concat([df2, pd.DataFrame(df.at[i,"Subtotal"])])
        return df2

    def get_options(self):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
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

        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
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
            df.PutOrCall = df.PutOrCall.apply(lambda x: self.__call_put_map[x] if x in self.__call_put_map else self.__call_put_map[0])

            df = df[_filter_columns].copy()
            df.columns = _options_columns

            df = convert_to_numeric_columns(df, _numeric_columns)
            df = df[df.strike > 0].copy() # Remove non options rows

        else:
            df = pd.DataFrame(columns=_options_columns).set_index(['symbol'])

        return df

    def get_MERVAL(self):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"indices","term":""}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel", headers=headers, data = data)
        status = response.status_code
        if status != 200:
            print("GetByPanel", status)  
            exit()

        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])
        df = df[self.__filter_columns_sp].copy()
        df.columns = self.__sp_columns
        df = convert_to_numeric_columns(df, self.__numeric_columns_sp)
        return df

    def get_personal_portfolio(self):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"indices","term":""}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetFavoritos", headers=headers)
        status = response.status_code

        data = response.json()
        data = pd.DataFrame(data['Result'])

        if status != 200:
            print("GetByPanel", status)  
            exit()

        df = pd.DataFrame(data)
        if df.empty:
            return self.__empty_personal_portfolio.copy()

        filter_columns = ['Symbol', 'Term', 'BuyQuantity', 'BuyPrice', 'SellPrice', 'SellQuantity', 'LastPrice', 'VariationRate', 'StartPrice', 'MaxPrice', 'MinPrice', 'PreviousClose', 'TotalAmountTraded', 'TotalQuantityTraded', 'Trades', 'TradeDate', 'MaturityDate', 'StrikePrice', 'PutOrCall', 'Issuer', 'ClosePrice']
        numeric_columns = ['last', 'close', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_size', 'bid', 'ask_size', 'ask', 'previous_close', 'strike']
        numeric_options_columns = ['MaturityDate', 'StrikePrice']
        alpha_option_columns = ['PutOrCall', 'Issuer']

        df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')
        df.loc[df.StrikePrice == 0, alpha_option_columns] = ''
        df.loc[df.StrikePrice == 0, numeric_options_columns] = np.nan
        df.MaturityDate = pd.to_datetime(df.MaturityDate, format='%Y%m%d', errors='coerce')
        df.PutOrCall = df.PutOrCall.apply(lambda x: self.__call_put_map[x] if x in self.__call_put_map else self.__call_put_map[0])
        df.Term = df.Term.apply(lambda x: self.__settlements_int_map[x] if x in self.__settlements_int_map else '')
        df = df[filter_columns].copy()
        df.columns = self.__personal_portfolio_columns
        df = convert_to_numeric_columns(df, numeric_columns)
        return df
    
    def get_repos(self):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()
        headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "en-US,en;q=0.5",
            "Connection" : "keep-alive",    
            "Content-Type" : "application/json; charset=utf-8",
            "DNT" : "1",    
            "Host" : f"{self.__host}",
            "Origin" : f"https://{self.__host}",
            "Referer" : f"https://{self.__host}/Prices/Stocks",
            "Sec-Fetch-Dest" : "empty",
            "Sec-Fetch-Mode" : "cors",
            "Sec-Fetch-Site" : "same-origin",
            "TE" : "trailers",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "X-Requested-With" : "XMLHttpRequest"
        }

        data = '{"panel":"cauciones","term":""}'
        response = self.__s.post(url = f"https://{self.__host}/Prices/GetByPanel",data=data ,headers=headers)
        status = response.status_code


        data = response.json()
        df = pd.DataFrame(data['Result']['Stocks'])

        if status != 200:
            print("GetByPanel", status)  
            exit()

        filter_columns = ['Symbol', 'CantDias', 'Term', 'BuyQuantity', 'BuyPrice', 'SellPrice', 'SellQuantity', 'LastPrice', 'VariationRate', 'StartPrice', 'MaxPrice', 'MinPrice', 'PreviousClose', 'TotalAmountTraded', 'TotalQuantityTraded', 'Trades', 'TradeDate', 'ClosePrice']
        numeric_columns = ['last', 'open', 'high', 'low', 'volume', 'turnover', 'operations', 'change', 'bid_amount', 'bid_rate', 'ask_rate', 'ask_amount', 'previous_close', 'close']

        if not df.empty:
            df.TradeDate = pd.to_datetime(df.TradeDate, format='%Y%m%d', errors='coerce') + pd.to_timedelta(df.Hour, errors='coerce')

            df = df[filter_columns].copy()
            df.columns = self.__repos_columns

            df = convert_to_numeric_columns(df, numeric_columns)
            df = df.set_index(self.__repos_index)
        else:
            df = self.__empty_repos.copy()

        return df
    
    def get_daily_history(self, symbol, from_date, to_date):
        if not self.__is_user_logged_in:
            print('You must be logged first')
            exit()

        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        url = 'https://{}/HistoricoPrecios/history?symbol={}&resolution=D&from={}&to={}'.format(
            self.__host,
            symbol.upper(),
            self.__convert_datetime_to_epoch(from_date),
            self.__convert_datetime_to_epoch(to_date))

        resp = self.__s.get(url = url ,headers=headers)
        resp.raise_for_status()
        resp = resp.json()
        df = pd.DataFrame({'date': resp['t'], 'open': resp['o'], 'high': resp['h'], 'low': resp['l'], 'close': resp['c'], 'volume': resp['v']})
        df.date = pd.to_datetime(df.date, unit='s').dt.date
        df.volume = df.volume.astype(int)

        return df
    

    #########################
    #### PRIVATE METHODS ####
    #########################
    def __convert_datetime_to_epoch(self, dt):

        if isinstance(dt, str):
            dt = datetime.datetime.strptime(dt, '%Y-%m-%d')

        dt_zero = datetime.date(1970, 1, 1)
        time_delta = dt - dt_zero
        return int(time_delta.total_seconds())
    
    def __get_broker_data(self, broker_id):

        broker_data = [broker for broker in brokers if broker['broker_id'] == broker_id]

        if not broker_data:
            supported_brokers = ''.join([str(broker['broker_id']) + ', ' for broker in brokers])[0:-2]
            raise BrokerNotSupportedException('Broker not supported.  Brokers supported: {}.'.format(supported_brokers))

        return broker_data[0]


