import matplotlib.pyplot as plt
import pandas as pd
import pyRofex as pyRofex

from account_details import user, password, account
from log_in import LogIn
from get_data import GetData
from get_tasa2 import GetTasa
from add_month_year import add_year, add_month
from plot_future import plot_prices


class StrategyArbitrage:

    # def __init__(self,login, spot, instrument):
    def __init__(self, login, spot):
        # import matplotlib.pyplot as plt

        """Define General Variables"""
        self.instrument = ['DLR/ENE23', 'YPFD/FEB22', 'GGAL/ABR22', 'DLR/FEB22', 'DLR/NOV22', 'DLR/MAR22',
                           'DLR/AGO22', 'DLR/FEB22A', 'PAMP/FEB22', 'DLR/JUN22',
                           'DLR/ABR22', 'DLR/OCT22', 'DLR/SEP22', 'DLR/DIC22', 'DLR/MAY22', 'GGAL/FEB22', 'DLR/JUL22']
        # self.instrument = instrument
        self.future_ws_df = pd.DataFrame(columns=["activo", "bid", "offer", "last", "month", "year", "timestamp"])
        self.future_ws_df.set_index('activo', inplace=True)
        # self.future_ws_df_comission = pd.DataFrame(columns=["activo", "bid", "offer", "last", "month", "year", "timestamp"])
        # self.future_ws_df_comission.set_index('activo', inplace=True)


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
        self.count = 0
        self.keys = []

        """API DATA"""
        self.message_list = []
        self.order_report = []

        """API Connection"""
        """Initialize the environment"""
        # pyRofex.initialize(user="luciomassimi3968", password = "feulrX6%", account = "REM3968", environment=pyRofex.Environment.REMARKET)
        self.login = login
        login.initialize
        self.saldo = 0

        """Initialize Websocket Connection with the handler"""
        pyRofex.init_websocket_connection(
            market_data_handler=self.market_data_handler,
            order_report_handler=self.order_report_handler,
            error_handler=self.error_handler
            # ,
            # exception_error = self.exception_error,
        )
        """Subscribes for Market Data"""
        pyRofex.market_data_subscription(
            tickers=self.instrument,
            entries=[
                pyRofex.MarketDataEntry.BIDS,
                pyRofex.MarketDataEntry.OFFERS,
                pyRofex.MarketDataEntry.LAST
            ]
        )
        pyRofex.order_report_subscription(snapshot=True)

    @property
    def saldo_left(self):
        account_details = pyRofex.get_account_report(login.account)
        self.saldo = account_details["accountData"]["availableToCollateral"]
        return self.saldo

    def arbitraje_tasas(self, dataframe_tasa_ws):
        print("\nARBITRAJE TASAS\n")

        for bid in dataframe_tasa_ws['bid']:
            for offer in dataframe_tasa_ws['offer']:

                if bid > offer and (self.fire_power > (self.size * 2)):
                    """Se entra en arbitraje si alguna tasa BID es mayor que una tasa OFFER, esto significa que 
                    podemos "hacer tasa" a tasa mayor de la que "nos financiamos"."""

                    ticker_offer = dataframe_tasa_ws[dataframe_tasa_ws['offer'] == offer].index[0]
                    price_offer = self.future_ws_df[dataframe_tasa_ws['offer'] == offer]['offer'][0]  # + 0.01
                    ticker_bid = dataframe_tasa_ws[dataframe_tasa_ws['bid'] == bid].index[0]
                    price_bid = self.future_ws_df[dataframe_tasa_ws['bid'] == bid]['bid'][0]  # - 0.01

                    """Creo 'Keys' o 'Flags' para poder comparar las posibles nuevas operaciones con las que ya estan
                    activas. En este caso trato de que no se repitan las operaciones y haya una sola para cada arbitraje
                    al mismo tiempo. Se podria luego agregar una opcion que tambien mande una nueva operacion si el 
                    arbitraje es mas beneficioso para hacer DCA y promediar"""
                    key1 = ticker_bid + ticker_offer

                    if key1 in self.keys:
                        print("Don't Repeat!")

                    else:
                        self.send_order(ticker_offer, pyRofex.Side.BUY, self.intern_id, price_offer,
                                        offer)
                        self.send_order(ticker_bid, pyRofex.Side.SELL, self.intern_id, price_bid, bid)
                        self.intern_id += 1
                        self.fire_power -= self.size * 2
                        print("Firepower Left: ", self.fire_power)
                        self.count += 1

                        self.keys.append(key1)
                        print("\nTotal Keys\n")
                        print(self.keys)

    def send_order(self, ticker, side, intern_id, price_bid_offer, tasa_bid_offer):
        """Toma los output de otras funciones, manda operaciones y las guarda con su #order en un df de
        operaciones historicas: order_history, y otro de operaciones activas: order_active. Con el #order se puede
        consultar el estado de las operaciones"""
        # print("\n--\n")
        order = pyRofex.send_order(
            ticker=ticker,
            side=side,
            size=self.size,
            price=price_bid_offer,
            order_type=pyRofex.OrderType.LIMIT)
        print(f"\nOPEN ORDER SENT: {order}\n")
        self.order_active.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                             pyRofex.get_order_status(order['order']['clientId'])[
                                                                 'order']['transactTime'][0:17]]
        self.order_history.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                              pyRofex.get_order_status(order['order']['clientId'])[
                                                                  'order']['transactTime'][0:17]]
        print(f"Order History: \n{self.order_history}\n")
        print(f"Order Active: \n{self.order_active}\n")

    def close(self, order_id, ticker, side, intern_id, price_bid_offer, tasa_bid_offer):
        """Toma el output de "close_arb", cierra las operaciones de arbitraje mandando la operacion contraria. Guarda
         la operacion en order_history, y borra la operacion de order_active"""
        # print("\n--\n")
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

        print(f"ORDER TO CLOSE: {order_id}")

        self.order_active.drop(order_id, axis=0, inplace=True)
        side = pyRofex.get_order_status(order['order']['clientId'])['order']['side']
        self.order_history.loc[order['order']['clientId']] = [ticker, self.size, side, intern_id, tasa_bid_offer,
                                                              pyRofex.get_order_status(order['order']['clientId'])[
                                                                  'order']['transactTime'][0:17]]
        print(f"Order History: \n{self.order_history}\n")
        print(f"Order Active: \n{self.order_active}\n")

    def close_arb(self, df):
        """En df entra self.tasas para estimar si hay alguna de las operaciones de arbitraje que tienen que cerrarse al
        cumplirse la condicion de que el BID del que antes fue el OFFER se "de vuelta" y ahora sea igual o mayor.
        De esta manera se igualan las tasas y se cierra, o se deberia invertir la posicion."""
        print("\nCLOSE ARB\n")

        if self.fire_power <= (self.maxoperation - 2):
            """Un check extra, no se podria "cerrar" una operacion si no hay ninguna abierta"""

            for bid in df['bid']:
                for offer in df['offer']:

                    if bid > offer:
                        """El key lo uso para asegurarme que el order del bid y offer sea igual a la de la operacion
                        que ya se habia hecho antes. Si solo checkeo que ahora el bid sea menor al offer para cerrar
                        y que tengan el mismo ID, lo que puede pasar es que el offer del vendido sea mayor al bid del 
                        comprado y la operacion se cierre.
                        La idea del key es para asegurar que se este cerrando la operacion correcta"""

                        ticker_offer = df[df['offer'] == offer].index[0]
                        ticker_bid = df[df['bid'] == bid].index[0]

                        key1 = ticker_bid + ticker_offer
                        key_inverse =  ticker_offer + ticker_bid
                        print(f"key: {key1}")
                        print(f"key_inverse: {key_inverse}")

                        if key_inverse in self.keys:
                            """Key inverse me deja ver si el arbitraje que se esta procesando es el contrario de un 
                            abitraje anterior. Si es el caso, excluyo de la lista de keys el arbitraje que se esta
                            cerrando para que se pueda volver a abrir si la situacion cambia y tambien el arbitraje
                            que se esta operando en este momento para que se vuelva a ejecutar. La primera ejecucion
                            seria el cierre del arbitraje anterior, y la segunda operacion seria el comienzo del nuevo
                            arbitraje."""
                            self.keys.remove(key_inverse)
                            self.keys.remove(key1)

                            self.fire_power += self.size
                            print(f"Firepower left: \n{self.fire_power}\n")

        else:
            print("\nSin Operaciones\n")

    """API MESSAGE HANDLERS"""

    def order_report_handler(self, message):
        print(f"Order Routing Message Received: {message}")
        self.order_report.append(message)

    def error_handler(message):
        print(f"Error Message Received: {message}")

    def exception_error(message):
        print(f"Exception Message Received: {message}")

    def market_data_handler(self, message):
        """Cambiar el bidx y offerx para agregar las comisiones cuando termine  de probar cosas"""

        from datetime import datetime
        import numpy as np

        self.message_list.append(message)
        print("Market Data Message Received: {0}".format(message))

        symbol = message["instrumentId"]['symbol']
        last = np.nan if not message["marketData"]["LA"] else message["marketData"]["LA"]["price"]

        """Deberia calcular las tasas con la comision incluida para saber el resultado verdadero> incluirlas directo
        en la tasa, o modificar la """
        # bidx = last if not message["marketData"]["BI"][0]["price"] else message["marketData"]["BI"][0]["price"] * (1 - self.commission)
        # offerx = last if not message["marketData"]["OF"][0]["price"] else message["marketData"]["OF"][0]["price"] * (1 + self.commission)

        """En este caso uso el last en bidx y offerx para el bien de la practicidad del caso o para testear el bot,
        muchas veces me paso que no hay puntas y el bot no le pega a nada"""
        bidx = last if not message["marketData"]["BI"][0]["price"] else message["marketData"]["BI"][0]["price"]
        offerx = last if not message["marketData"]["OF"][0]["price"] else message["marketData"]["OF"][0]["price"]
        monthx = add_month(message["instrumentId"]['symbol'])
        yearx = add_year(message["instrumentId"]['symbol'])
        datex = datetime.fromtimestamp(message["timestamp"] / 1000).strftime('%Y-%m-%d %H:%M:%S')

        """Dataframe de futuros"""
        self.future_ws_df.loc[symbol] = [bidx, offerx, last, monthx, yearx, datex]

        self.future_ws_df['month'] = self.future_ws_df['month'].apply(int)
        self.future_ws_df['year'] = self.future_ws_df['year'].apply(int)
        self.future_ws_df = self.future_ws_df.sort_values(by=['year', 'month'], ascending=[True, True])
        print("\nFutures:\n")
        print(self.future_ws_df)

        """Dataframe de tasas> Como mejoras puedo sacar las tasas con las comisiones incluidas en el df de futuros"""
        # self.future_ws_df_comission.loc[symbol] = [bidx,offerx,last,monthx,yearx,datex]
        self.tasas = GetTasa.tasas_futuros(self.spot, self.future_ws_df)
        print("\nTasas:\n")
        print(self.tasas)

        """Ejecuta el arbitraje y el cierre del arbitraje de tasas"""
        self.arbitraje_tasas(self.tasas)
        self.close_arb(self.tasas)

        """Save data > creo un CSV con la informacion capturada del bot por si es necesaria compartirla u analizarla
        con otra herramienta"""
        # print('pre csv')
        time = datetime.now().strftime('%Y_%b_%d_%H_%M_%S')
        time = datetime.now().strftime('%Y_%b_%d_%H')
        pd.concat([self.future_ws_df, self.tasas], axis=1).to_csv(f'run_data_{time}.csv')
        with open(f'run_data_{time}.csv', 'a') as f:
            pd.concat([self.order_history, self.order_active], axis=1).to_csv(f)
        # print("csv")

        """Plot de los futuros y las tasas a medida que se ingesta data > Correr en Jupyter."""
        # plot_prices(self.tasas)
        # plot_prices(self.future_ws_df)

        # print(f'saldo: {saldo_left()}')



    def cancel_all(df):
        for open_order in df['order_id']:
            order_canceled = pyRofex.cancel_order(open_order)
            print(order_canceled)


"""TEST """
log_in_1 = LogIn(user, password, account)
get_data_1 = GetData(log_in_1, 'GGAL', 'YPFD', 'PAMP', 'DLR')
get_data_1.spot_df
# get_data_1.instruments_load

if __name__ == "__main__":
    StrategyArbitrage(log_in_1, get_data_1.spot)
    # StrategyArbitrage(log_in_1, get_data_1.spot, get_data_1.instruments)
