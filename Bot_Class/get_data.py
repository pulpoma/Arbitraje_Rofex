# from log_in import LogIn

class GetData():
    
    def __init__(self, LogIn, *args):  #Si no funciona, cambiar el "LogIn" por login
        self.LogIn = LogIn
        self.tickers = list(args)

        self.spot = "Run spot_df first \n"
        self.instruments = "Run instruments_load first \n"
        # self.instruments =['DLR/OCT22A', 'DLR/JUL22A', 'YPFD/FEB22', 'DLR/AGO22A', 'DLR/SEP22A', 'DLR/FEB22', 'DLR/NOV22', 'DLR/JUN22A', 'DLR/MAY22A', 'DLR/ABR22A', 'DLR/MAR22', 'DLR/AGO22', 'DLR/FEB22A', 'PAMP/FEB22', 'DLR/JUN22', 'DLR/ABR22', 'DLR/MAR22A', 'DLR/OCT22', 'DLR/SEP22', 'DLR/NOV22A', 'DLR/MAY22', 'GGAL/FEB22', 'DLR/JUL22']
        self.future_rest = "Run future_rest_df first \n"
        

    @property
    def instruments_load(self):
        import pyRofex as pyRofex

        self.LogIn.initialize  

        instruments_step = []
        instruments = []
        instrument_dict = pyRofex.get_all_instruments()['instruments']
        count=0

        for order in range(0, len(instrument_dict)):
            instruments_step.append(pyRofex.get_all_instruments()['instruments'][order]['instrumentId']['symbol'])
            # print(count) --> visualizar MAX=436
            count+=1

        for i in instruments_step:
            for j in self.tickers:
                if (j in i) and (i.count('/') == 1):
                    instruments.append(i)
                    # print(i) -->Visualizar

        self.instruments = instruments

        print("Instruments Loaded")
        return self.instruments


    @property
    def spot_df(self):
        import datetime as datetime
        import yfinance as yf
        import pandas as pd

        spot = pd.DataFrame()
        start = datetime.datetime(2022, 1, 1)
        end = datetime.datetime.today()

        for t in self.tickers:
            a = t
            if t in 'DLR':
                t = 'ARS=X'
            else:
                t += '.BA'

            print(t, "-->", a)  #---> Visualize ticker change
            spot[t] = yf.Ticker(t).history(start = start, end = end)['Close']

        spot.columns = self.tickers
        self.spot = spot.iloc[-1]
        
        return self.spot


    @property
    def future_rest_df(self):
        import pyRofex as pyRofex
        import numpy as np
        import pandas as pd

        self.LogIn.initialize

        mes_s = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
        mes_i = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        ano_s = ['22', '23', '24']
        ano_i = [2022, 2023, 2024]
        mes_s_i = dict(zip(mes_s, mes_i))
        ano_s_i = dict(zip(ano_s, ano_i))

        # Traigo datos de los instrumentos
        resp_dict = {}

        for activo in self.instruments:
            resp_dict[f"{activo}"] = pyRofex.get_market_data(ticker = activo)

        # BID
        bid = {}
        for activo in self.instruments:

            """Trato de traer los valores del precio"""
            """Si no trae valores de precio y necesito probar algo de las funciones que siguen, puedo tratar de importar
            los datos del cierre o del ultimo precio"""
            try:
                bid[activo] = resp_dict[activo]['marketData']['BI'][0]['price']            
            except:
                # print(f"{activo} has no BID")
                bid[activo] = np.nan

        # OFFER
        offer = {}
        for activo in self.instruments:
            # Trato de traer los valores del precio

            try:
                offer[activo] = resp_dict[activo]['marketData']['OF'][0]['price']

            except:
                #  print(f"{activo} has no OFFER")
                offer[activo] = np.nan

        self.future_rest = pd.DataFrame({"bid": bid, "offer": offer}).sort_index()

        for month in mes_s_i.keys():
            for activo in self.future_rest.index:
                if month in activo:
                    try:
                        self.future_rest.loc[activo, "month"] = mes_s_i[month]
                    except:
                        self.future_rest.loc[activo, "month"] = None

        for year in ano_s_i.keys():
            for activo in self.future_rest.index:
                if year in activo:
                    try:
                        self.future_rest.loc[activo, "year"] = ano_s_i[year]
                    except:
                        self.future_rest.loc[activo, "year"] = None

        self.future_rest = self.future_rest.sort_values('month')
        self.future_rest['month'] = self.future_rest['month'].apply(int)
        self.future_rest['year'] = self.future_rest['year'].apply(int)

        return self.future_rest
    
    
    @property
    def future_ws_df(self):
        pass