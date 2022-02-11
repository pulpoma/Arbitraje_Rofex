import datetime
import time
import matplotlib.pyplot as plt
import pandas as pd

from account_details import user, password, account
from log_in import LogIn
from get_data import GetData
from get_tasa2 import GetTasa

import pyRofex as pyRofex


class StrategyArbitrage:

    # def __init__(self,login,  instrument, spot):
    def __init__(self, login, spot):
        import matplotlib.pyplot as plt
        from datetime import datetime

        """Defino General Variables"""
        self.instrument = ['DLR/FEB22', 'DLR/MAR22', 'DLR/ABR22', 'DLR/MAY22', 'DLR/JUN22', 'DLR/JUL22', 'DLR/AGO22',
                           'DLR/SEP22', 'DLR/OCT22', 'DLR/NOV22']
        # self.instrument = instrument
        self.future_ws_df = pd.DataFrame(columns=["activo", "bid", "offer", "last", "month", "year", "timestamp"])
        self.future_ws_df.set_index('activo', inplace=True)
        self.message_list = []
        self.tasas = pd.DataFrame()
        self.spot = spot
        self.arbitraje_df = pd.DataFrame()

        """Define Trading Variables"""
        self.commission = .005
        self.fire_power = 10
        self.size = 1
        self.order_history = pd.DataFrame(columns=["order id", "ticker", "side", "size"])
        self.order_history.set_index('order id', inplace=True)

        
        """API Connection"""
        # Initialize the environment
        # pyRofex.initialize(user="luciomassimi3968", password = "feulrX6%", account = "REM3968", environment=pyRofex.Environment.REMARKET)
        login.initialize
        # Initialize Websocket Connection with the handler
        pyRofex.init_websocket_connection(
            market_data_handler=self.market_data_handler
        )
        # Subscribes for Market Data
        pyRofex.market_data_subscription(
            tickers=self.instrument,
            entries=[
                pyRofex.MarketDataEntry.BIDS,
                pyRofex.MarketDataEntry.OFFERS,
                pyRofex.MarketDataEntry.LAST
            ]
        )
        # Subscribes to receive order report for the default account
        pyRofex.order_report_subscription()

        
        
    @staticmethod
    def plot_prices(dataframe):
        """Plotear como cambian las tasas y precios de los activos"""
        
        # plt.figure(figsize=(18, 10))
        x = dataframe.index
        y_bid = dataframe['bid'].loc[x]
        y_offer = dataframe['offer'].loc[x]
        y_last = dataframe['last'].loc[x]

        plt.plot(x, y_bid, color='red', marker='o', label='Bid - Colocadora')
        plt.plot(x, y_offer, color='green', marker='X', label='Offer - Tomadora')
        plt.plot(x, y_last, color='black', linestyle='dashed', alpha=0.5, label='last')

        plt.title('Futuros')
        plt.xlabel('Future Contract')
        plt.ylabel('Precio')

        plt.legend()
        plt.tight_layout()
        plt.show()

    @staticmethod
    def add_year(message_instrument):
        """Agrego el ano a cada row de los activos que se importan para calcular la tasa"""
        ano_s = ['22', '23', '24']
        ano_i = [2022, 2023, 2024]
        ano_s_i = dict(zip(ano_s, ano_i))

        for year in ano_s_i.keys():
            if year in message_instrument:
                return ano_s_i[year]

            
            
    @staticmethod
    def add_month(message_instrument):
        """Agrego el mes a cada row de los activos que se importan para calcular la tasa"""
        mes_s = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
        mes_i = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        mes_s_i = dict(zip(mes_s, mes_i))

        for month in mes_s_i.keys():
            if month in message_instrument:
                return mes_s_i[month]

            
            
    def arbitraje_tasas(self, dataframe_tasa_ws):  # TODO TERMINAR LAS ORDENES
        """ Crea un diccionario de todas las oportinidades de arbitraje que hay, y luego usa
        self.send_order() para mandar las operaciones de compra y venta"""
        
        arbitraje_dict = {}
        count = 0
        for offer in dataframe_tasa_ws['offer']:
            for bid in dataframe_tasa_ws['bid']:
                # print(f'arbitraje: {count}')
                # print(f'bid: {bid}')
                # print(f'offer: {offer}')

                if bid < offer and (self.fire_power > (self.size * 2)):  # TODO cambiar el signo >
                    print("\narbitraje_tasas ")
                    # print("BID", dataframe_tasa_ws[dataframe_tasa_ws['bid'] == bid].index[0])
                    # print("Price", self.future_ws_df[dataframe_tasa_ws['bid'] == bid]['bid'][0] * (1 - self.commission))
                    # print("")
                    # print("OFFER", dataframe_tasa_ws[dataframe_tasa_ws['offer'] == offer].index[0])
                    # print("Price", self.future_ws_df[dataframe_tasa_ws['offer'] == offer]['offer'] * (1 + self.commission))

                    # ticker_offer = dataframe_tasa_ws[dataframe_tasa_ws['offer'] == offer].index[0]
                    # price_offer = self.future_ws_df[dataframe_tasa_ws['offer'] == offer]['offer'][0] * (1 + self.commission)
                    # ticker_bid = dataframe_tasa_ws[dataframe_tasa_ws['bid'] == bid].index[0]
                    # price_bid = self.future_ws_df[dataframe_tasa_ws['bid'] == bid]['bid'][0] * (1 - self.commission)
                    #
                    # print(f"offer \n ticker: ({ticker_offer}), price: ({price_offer})")
                    # print(f"bid \n ticker: ({ticker_bid}), price: ({price_offer})")
                    # # print(ticker_bid, price_offer)
                    #
                    # self.send_order(str(ticker_offer), pyRofex.Side.BUY, price_offer)
                    # self.send_order(ticker_bid, pyRofex.Side.SELL, price_bid)
                    # #             #
                    # self.fire_power -= self.size * 2
                    # print("Firepower left: ", self.fire_power)

                    arbitraje_dict.update(
                        {f"{dataframe_tasa_ws[dataframe_tasa_ws['bid'] == bid].index[0]}-{count}" : bid, f"{dataframe_tasa_ws[dataframe_tasa_ws['offer'] == offer].index[0]}": offer})
                    count += 1
        #         else:
        #             pass

        arbitraje_df = pd.DataFrame(arbitraje_dict).T.sort_index()
        # arbitraje_df.columns = ['bid', 'offer']
        arbitraje_df.columns = ['bid ticker', 'bid tasa', 'offer ticker', 'offer tasa']
        # arbitraje_df.columns = ['bid ticker', 'bid price', 'bid tasa', 'offer ticker', 'offer price', 'offer tasa']
        self.arbitraje_df = arbitraje_df
        return self.arbitraje_df

    
    
    @property
    def send_order(self, ticker, side, price):  # TODO CHECKEAR QUE LAS ORDENES SE MANDEN
        print("\n SEND ORDER ")
        pyRofex.send_order(
            ticker=ticker,
            side=side,
            size=self.size,
            price=price,
            order_type=pyRofex.OrderType.LIMIT)

        self.order_history.loc[(order['order']['clientId'])] = [ticker, side, self.size]
        print(f"{side} order: {order['order']['clientId']}")

        
        
    @property
    def cancel_order(self):  # TODO AGREGAR UN CASE POR LAS DUDAS(?)
        pass
    
    
    
# por que no funciona @property?  #TODO leer
    def market_data_handler(self, message):
        from datetime import datetime

        self.message_list.append(message)
        print("Market Data Message Received: {0}".format(message))

        last = None if not message["marketData"]["LA"] else message["marketData"]["LA"]["price"]
        self.future_ws_df.loc[message["instrumentId"]['symbol']] = [
            message["marketData"]["BI"][0]["price"] * (1 - self.commission),
            message["marketData"]["OF"][0]["price"] * (1 + self.commission),
            last,
            StrategyArbitrage.add_month(message["instrumentId"]['symbol']),
            StrategyArbitrage.add_year(message["instrumentId"]['symbol']),
            datetime.fromtimestamp(message["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        ]
        self.future_ws_df['month'] = self.future_ws_df['month'].apply(int)
        self.future_ws_df['year'] = self.future_ws_df['year'].apply(int)

        self.future_ws_df = self.future_ws_df.sort_values(by=['year', 'month'], ascending=[True, True])
        self.tasas = GetTasa.tasas_futuros(self.spot, self.future_ws_df)

        self.arbitraje_tasas(self.tasas) #

        print(self.arbitraje_df)
        print(self.future_ws_df)
        print(self.tasas)
        # return self.future_ws_df ,self.tasas

"""TEST """
log_in_1 = LogIn(user, password, account)
get_data_1 = GetData(log_in_1, 'GGAL', 'YPFD', 'PAMP', 'DLR')
get_data_1.spot_df

if __name__ == "__main__":
    StrategyArbitrage(log_in_1, get_data_1.spot)
