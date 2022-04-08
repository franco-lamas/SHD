"""
When this code was created only God and I knew how it works, now only God knows.

GoodLuck and may the force be with you.
"""
from os import path
import re
import json
import requests
import pandas as pd
import numpy as np
from setuptools import setup, find_packages

from common import brokers, BrokerNotSupportedException,convert_to_numeric_columns



class SHD:
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
          print("login status", status)  
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

        response = self.__s.post(url = f"https://{self.__host}/Login/IngresarModal", headers=headers, data = data, allow_redirects=False)
        status = response.status_code

        if status != 302:
            print("login status", status)  
            exit()
        print("Connected!")

    def get_bluechips(self,settlement):
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





    def __get_broker_data(self, broker_id):

        broker_data = [broker for broker in brokers if broker['broker_id'] == broker_id]

        if not broker_data:
            supported_brokers = ''.join([str(broker['broker_id']) + ', ' for broker in brokers])[0:-2]
            raise BrokerNotSupportedException('Broker not supported.  Brokers supported: {}.'.format(supported_brokers))

        return broker_data[0]


