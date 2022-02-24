import matplotlib.pyplot as plt
import pandas as pd
import pyRofex as pyRofex

from account_details import user, password, account
from log_in import LogIn
from get_data import GetData
from get_tasa2 import GetTasa
from add_month_year import add_year, add_month

class StrategyArbitrage:

    # def __init__(self,login, spot, instrument):
    def __init__(self, login, spot):
        # import matplotlib.pyplot as plt

        """Define General Variables"""
        self.instrument = ['DLR/OCT22A', 'DLR/ENE23', 'DLR/JUL22A', 'YPFD/FEB22', 'DLR/AGO22A', 'GGAL/ABR22',
                           'DLR/SEP22A', 'DLR/FEB22', 'DLR/NOV22', 'DLR/JUN22A', 'DLR/MAY22A', 'DLR/ABR22A',
                           'DLR/ENE23A', 'DLR/MAR22', 'DLR/AGO22', 'DLR/FEB22A', 'PAMP/FEB22', 'DLR/JUN22', 'DLR/ABR22',
                           'DLR/MAR22A', 'DLR/DIC22A', 'DLR/OCT22', 'DLR/SEP22', 'DLR/DIC22', 'DLR/NOV22A', 'DLR/MAY22',
                           'GGAL/FEB22', 'DLR/JUL22']
        # self.instrument = instrument
        self.future_ws_df = pd.DataFrame(columns=["activo", "bid", "offer", "last", "month", "year", "timestamp"])
        self.future_ws_df.set_index('activo', inplace=True)
        self.message_list = []
        self.tasas = pd.DataFrame()
        self.spot = spot
        self.count_message = 0

        """Define Trading Variables"""
        self.commission = .005
        self.fire_power = 1000
        self.maxoperation = 1000
        self.size = 1
        pd.set_option('display.max_columns', None)
        self.order_history = pd.DataFrame(
            columns=['order_id', 'ticker', 'size', 'side', 'intern_id', 'tasa', "timestamp"])
        self.order_history.set_index('order_id', inplace=True)
        self.order_active = self.order_history.copy(deep=True)
        self.intern_id = 0

        """API Connection"""
        """Initialize the environment"""

        login.initialize
        """Initialize Websocket Connection with the handler"""
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

    @staticmethod
    def plot_prices(dataframe):
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



    def arbitraje_tasas(self, dataframe_tasa_ws):  # TODO TERMINAR LAS ORDENES
        print(
            "\nARBITRAJE TASAS -----------------------------------------------------------------------------------------------\n")
        for offer in dataframe_tasa_ws['offer']:
            for bid in dataframe_tasa_ws['bid']:

                if bid > offer and (self.fire_power > (self.size * 2)):

                    ticker_offer = dataframe_tasa_ws[dataframe_tasa_ws['offer'] == offer].index[0]
                    price_offer = self.future_ws_df[dataframe_tasa_ws['offer'] == offer]['offer'][0]
                    ticker_bid = dataframe_tasa_ws[dataframe_tasa_ws['bid'] == bid].index[0]
                    price_bid = self.future_ws_df[dataframe_tasa_ws['bid'] == bid]['bid'][0]

                    self.send_order(ticker_offer, pyRofex.Side.BUY, self.intern_id, price_offer, offer)
                    self.send_order(ticker_bid, pyRofex.Side.SELL, self.intern_id, price_bid, bid)
                    self.intern_id += 1
                    self.fire_power -= self.size * 2
                    print("Firepower left: ", self.fire_power)


    def send_order(self, ticker, side, intern_id, price_bid_offer, tasa_bid_offer):
        print(
            "\nORDER SENT")
        order = pyRofex.send_order(
            ticker=ticker,
            side=side,
            size=self.size,
            price=price_bid_offer,
            order_type=pyRofex.OrderType.LIMIT)
        # print(order)
        self.order_active.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                             pyRofex.get_order_status(order['order']['clientId'])[
                                                                 'order']['transactTime'][0:17]]
        self.order_history.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                              pyRofex.get_order_status(order['order']['clientId'])[
                                                                  'order']['transactTime'][0:17]]
        print(f"Order History: \n{self.order_history}\n")
        print(f"Order Active: \n{self.order_active}\n")

    def close(self, order_id, ticker, side, intern_id, price_bid_offer, tasa_bid_offer):
        print(
            "\nORDER CLOSED\n")

        if side == "Side.BUY":
            order = pyRofex.send_order(
                ticker=ticker,
                side=pyRofex.Side.SELL,  # ser lo contrario para cerrar operacion
                size=self.size,
                price=price_bid_offer,
                order_type=pyRofex.OrderType.LIMIT)

        elif side == "Side.SELL":
            order = pyRofex.send_order(
                ticker=ticker,
                side=pyRofex.Side.BUY,
                size=self.size,
                price=price_bid_offer,
                order_type=pyRofex.OrderType.LIMIT)
        else:
            print('\nERROR\n')

        print(f"ORDER TO DROP: {order_id}")

        self.order_active.drop(order_id, axis=0, inplace=True)
        side = pyRofex.get_order_status(order['order']['clientId'])['order']['side']
        self.order_history.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                              pyRofex.get_order_status(order['order']['clientId'])[
                                                                  'order']['transactTime'][0:17]]

        print(f"Order History: \n{self.order_history}\n")
        print(f"Order Active: \n{self.order_active}\n")


    def close_arb(self, df):
        """En df entra self.tasas para estimar si hay alguna de las operaciones de arbitraje que tienen que cerrarse"""
        print(
            "\nCLOSE ARB -----------------------------------------------------------------------------------------------")
        if self.fire_power <= (self.maxoperation - 2):
            for offer in df['offer']:
                for bid in df['bid']:
                    ticker_bid_new = df[df['bid'] == bid].index[0]
                    ticker_offer_new = df[df['offer'] == offer].index[0]

                    """El key lo uso para asegurarme que el order del bid y offer sea igual a la de la operacion
                    que ya se habia hecho antes. Si solo checkeo que ahora el bid sea menor al offer para cerrar
                    y que tengan el mismo ID, lo que puede pasar es que el offer del vendido sea mayor al bid del 
                    comprado y la operacion se cierre.
                    La idea del key es para asegurar que el offer"""

                    key1 = ticker_bid_new + ticker_offer_new

                    if bid >= offer and (ticker_bid_new != ticker_offer_new):
                        """BID TIENE QUE SER MAS GRANDE SIEMPRE, DE ESA MANERA SIEMPRE ESTOY HACIENDO TASA A LA TASA 
                        MAS GRANDE, Y 'TOMANDO' A LA TASA MAS CHICA"""

                        intern_id_bid_list = self.order_active[self.order_active['ticker'] == ticker_bid_new][
                            'intern_id']
                        intern_id_offer_list = self.order_active[self.order_active['ticker'] == ticker_offer_new][
                            'intern_id']

                        for id_bid in intern_id_bid_list:
                            for id_offer in intern_id_offer_list:

                                if id_bid == id_offer:
                                    print(f"id_bid: {id_bid}")
                                    print(f"id_offer: {id_offer}")

                                    """Es una lista porque dos operaciones van a tener el mismo id dado que 
                                    id_bid==id_offer. Por eso despues tengo que iterar para que se cierren las dos 
                                    operaciones. b_o simplemente es la iteracion para cerrar la operaciones de venta en
                                    bid y compra en offer"""


                                    arb_to_close_intern_id_list = self.order_active[
                                        self.order_active['intern_id'] == id_offer]
                                    print(f"\nEqual id offer:\n")
                                    print(arb_to_close_intern_id_list, "\n")

                                    bid_key = arb_to_close_intern_id_list.iloc[0]['ticker']
                                    offer_key = arb_to_close_intern_id_list.iloc[1]['ticker']
                                    key2 = bid_key + offer_key

                                    print(f"Close Key: {key2}")
                                    print(f"key: {key1}")

                                    if key1 == key2:
                                        """hace que la operacion antes abierta se cierre"""
                                        print(f"Match: {key1}={key2}")

                                        for b_o in range(0, 2):
                                            """id de operacion compra/venta original"""
                                            order_id = arb_to_close_intern_id_list.iloc[b_o].name

                                            print(f"id: {arb_to_close_intern_id_list.iloc[b_o]}, b_o: {b_o}")
                                            print(arb_to_close_intern_id_list)

                                            ticker = arb_to_close_intern_id_list.iloc[b_o]['ticker']
                                            side = str(arb_to_close_intern_id_list.iloc[b_o]['side'])
                                            size = arb_to_close_intern_id_list.iloc[b_o]['size']
                                            int_id = arb_to_close_intern_id_list.iloc[b_o]['intern_id']
                                            price_0 = self.future_ws_df[dataframe_tasa_ws['offer'] == offer]['offer'][0]
                                            price_1 = self.future_ws_df[dataframe_tasa_ws['bid'] == bid]['bid'][0]

                                            if b_o == 0:
                                                self.close(order_id, ticker, side, int_id, price_0, bid)
                                                self.fire_power += self.size
                                                print(f"Firepower left: \n{self.fire_power}\n")
                                            elif b_o == 1:
                                                self.close(order_id, ticker, side, int_id, price_1, offer)
                                                self.fire_power += self.size
                                                print(f"Firepower left: \n{self.fire_power}\n")
                                            else:
                                                print("Close error")
        else:
            print("Can't create $$$\n")

    def market_data_handler(self, message):
        from datetime import datetime
        import numpy as np

        self.message_list.append(message)
        print("Market Data Message Received: {0}".format(message))

        """Cambiar el bidx y offerx para agregar las comisiones cuando termine  de probar cosas
        tambien deberia de dejar de usar el last, porque se pueden mandar malas operaciones.
        """
        last = np.nan if not message["marketData"]["LA"] else message["marketData"]["LA"]["price"]
        bidx = last if not message["marketData"]["BI"][0]["price"] else message["marketData"]["BI"][0]["price"]
        offerx = last if not message["marketData"]["OF"][0]["price"] else message["marketData"]["OF"][0]["price"]
        monthx = add_month(message["instrumentId"]['symbol'])
        yearx = add_year(message["instrumentId"]['symbol'])
        datex = datetime.fromtimestamp(message["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')

        self.future_ws_df.loc[message["instrumentId"]['symbol']] = [
            bidx,
            offerx,
            last,
            monthx,
            yearx,
            datex
        ]
        self.future_ws_df['month'] = self.future_ws_df['month'].apply(int)
        self.future_ws_df['year'] = self.future_ws_df['year'].apply(int)

        self.future_ws_df = self.future_ws_df.sort_values(by=['year', 'month'], ascending=[True, True])
        print("\nFutures:\n")
        print(self.future_ws_df)

        self.tasas = GetTasa.tasas_futuros(self.spot, self.future_ws_df)
        print("\nTasas:\n")
        print(self.tasas)

        self.arbitraje_tasas(self.tasas)
        self.close_arb(self.tasas)

        """Save data"""

        print('pre csv')
        time = datetime.now().strftime('%Y_%b_%d_%H')
        pd.concat([self.future_ws_df, self.tasas], axis=1).to_csv(f'run_data_{time}.csv')
        with open(f'run_data_{time}.csv', 'a') as f:
            pd.concat([self.order_history, self.order_active], axis=1).to_csv(f)
        print("csv")


"""TEST """
log_in_1 = LogIn(user, password, account)
get_data_1 = GetData(log_in_1, 'GGAL', 'YPFD', 'PAMP', 'DLR')
get_data_1.spot_df
# get_data_1.instruments_load #sacar

if __name__ == "__main__":
    StrategyArbitrage(log_in_1, get_data_1.spot)
    # StrategyArbitrage(log_in_1, get_data_1.spot, get_data_1.instruments)
