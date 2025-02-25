import datetime
import numpy as np
import pandas as pd

class Portfolio:
    """
    Clase Portfolio que interactúa con una API para obtener y procesar información de activos de un comitente
    en una fecha específica y en una moneda determinada.
    
    Atributos:
        headers (dict): Encabezados HTTP que se utilizan en las solicitudes a la API.
        host (str): Host o dominio donde se realiza la consulta.
        session (requests.Session): Sesión de solicitud HTTP que mantiene la persistencia entre las solicitudes.
    """

    def __init__(self, headers, host, session):
        """
        Constructor de la clase Portfolio.

        Parámetros:
            headers (dict): Encabezados HTTP que se utilizan en las solicitudes a la API.
            host (str): Host o dominio donde se realiza la consulta.
            session (requests.Session): Sesión de solicitud HTTP.
        """
        self.__headers = headers
        self.__host = host
        self.__s = session
        
    def by_date(self, comitente, date, moneda):
        """
        Obtiene los activos de un comitente en una fecha específica y en una moneda determinada, 
        procesando la respuesta de la API para devolverla en formato DataFrame.

        Parámetros:
            comitente (str): ID del comitente.
            date (str): Fecha en formato "YYYY-MM-DD" para la consulta.
            moneda (str): Moneda en la que se requiere obtener los activos ("ARS" o "USD").

        Retorna:
            pd.DataFrame: DataFrame con los datos procesados de los activos.

        Lanza:
            ValueError: Si la moneda no es válida o si la fecha no tiene el formato esperado.
        """
        
        # Convertir la fecha en un objeto datetime
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"La fecha '{date}' no tiene el formato correcto (YYYY-MM-DD).")

        # Formatear la fecha al formato "DD/MM/YYYY"
        date = date.strftime("%d/%m/%Y")

        # Mapa de monedas para determinar el proceso
        proceso_map = {"ARS": 10, "USD": 91}

        # Validar que la moneda sea válida
        if moneda not in proceso_map:
            raise ValueError(f"Moneda '{moneda}' no válida.")

        # Cargar los datos a consultar en un diccionario
        payload = {
            "comitente": str(comitente),
            "consolida": "0",
            "proceso": str(proceso_map.get(moneda)),
            "fechaDesde": str(date),
            "tipo": "00"
        }

        # Realizar la solicitud a la API
        response = self.__s.post(f"https://{self.__host}/Consultas/GetConsulta", json=payload)
        
        # Verificar si la respuesta fue exitosa
        if response.status_code != 200:
            raise ValueError(f"Error al realizar la solicitud: {response.status_code}")
        
        # Convertir la respuesta JSON en un objeto Python
        portfolio = response.json()

        # Inicializar una lista para almacenar los activos procesados
        activos = []

        # Iterar sobre los activos obtenidos de la respuesta
        for activo in portfolio['Result']['Activos']:
            for subtotal in activo['Subtotal']:
                # Crear un diccionario con los datos relevantes del activo y su subtotal
                activo_data = {
                    'symbol': subtotal['TICK'],
                    'description': subtotal['AMPL'],
                    'position_size': subtotal['CANT'],
                    'position_price': subtotal['CAN0'],
                    'date_close': subtotal['PCIO'],
                    'position': subtotal['IMPO'],                    
                    'PNL': subtotal['GTOS'],
                    'group': activo['ESPE'],                    
                }
                # Agregar los datos procesados del activo a la lista
                activos.append(activo_data)

        # Convertir la lista de activos en un DataFrame de pandas
        activos_df=pd.DataFrame(activos)

        tenencia_disponible = next(
                (item["IMPO"] for item in portfolio["Result"]["Activos"] if item["ESPE"] == "Cuenta Corriente"),
                None
            )

        activos_df.loc[activos_df['group'] == 'Cuenta Corriente', 'position'] = tenencia_disponible
        activos_df.loc[activos_df['group'] == 'Cuenta Corriente', 'description'] = "Liquidez"
        # Retornar el DataFrame con los datos procesados
        return activos_df
