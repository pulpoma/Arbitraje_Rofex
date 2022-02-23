import unittest
from unittest.mock import patch

import pandas as pd
from account_details import user, password, account
from log_in import LogIn
from get_data import GetData
from get_tasa2 import GetTasa
from S

class TestBot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')

    @classmethod
    def tearDownClass(cls):
        print('teardownClass')

    def setUp(self):
        # print('setUp')
        self.user = LogIn(user,password,account)
        self.data1 = GetData(self.user,'GGAL','YPFD','PAMP','DLR')
        self.tasa1 = GetTasa()
        self.bot1 = StrategyArbitrage(log_in_1, get_data_1.spot)


    """Class get_data2"""


    def test_get_data_instruments_load(self):
        print('\ntest_get_data_instruments_load')
        self.data1.instruments_load
        self.assertListEqual(self.data1.instruments, ['DLR/OCT22A', 'DLR/ENE23', 'DLR/JUL22A', 'YPFD/FEB22', 'DLR/AGO22A', 'GGAL/ABR22', 'DLR/SEP22A', 'DLR/FEB22', 'DLR/NOV22', 'DLR/JUN22A', 'DLR/MAY22A', 'DLR/ABR22A', 'DLR/ENE23A', 'DLR/MAR22', 'DLR/AGO22', 'DLR/FEB22A', 'PAMP/FEB22', 'DLR/JUN22', 'DLR/ABR22', 'DLR/MAR22A', 'DLR/DIC22A', 'DLR/OCT22', 'DLR/SEP22', 'DLR/DIC22', 'DLR/NOV22A', 'DLR/MAY22', 'GGAL/FEB22', 'DLR/JUL22'])

    # def test_get_data_spot_df(self):
    #     print('\ntest_get_data_spot_df')
    #     self.data1.spot_df
    #     self.assertListEqual(self.data1.spot.index.to_list(), ['GGAL','YPFD','PAMP','DLR'])
    #

    # def test_get_data_future_rest_df(self):
    #     print('\ntest_get_data_future_rest_df')
    #     self.data1.spot_df
    #     self.data1.instruments_load
    #     self.assertListEqual(self.data1.future_rest_df.columns.to_list(), ['bid', 'offer', 'month', 'year'])

    """Class get_tasa2"""  #TODO tal vez agregar el resto de las funciones de tasa

    # def test_get_tasa_delta_days(self):
    #     print('\ntest_get_tasa_delta_days')
    #     self.assertEquals(self.tasa1.delta_days(2022,2), 7)
    #
    # def test_get_tasa_tasa(self):
    #     print('\ntest_get_tasa_tasa')
    #     self.assertEqual(round(self.tasa1.tasa(100,130,365),2), 0.26 )
    #
    #
    # def test_tasas_futuros(self):
    #     print('\ntest_get_data_future_rest_df')
    #     spot = pd.Series([100, 100], index=['DLR', 'YPF'])
    #     future_df = pd.DataFrame(index=['DLR/FEB22', 'YPF/FEB23'],
    #                              columns=['bid', 'offer', 'last', 'month', 'year', 'timestamp'],
    #                              data=[[101, 101.5, 101.25, 2, 2022, 'tiempo'], [160, 165, 163, 2, 2023, 'tiempo']])
    #     self.assertListEqual(self.tasa1.tasas_futuros(spot,future_df)['bid'].to_list(),[0.5188386802009076, 0.4611594749319718] )

    # """Class StrategyArbitrage"""
    #
    # def test_market_data_handler(self):
    #
    #     self.bot1
    #     message1 = {'type': 'Md', 'timestamp': 1645414957458, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/ABR22'}, 'marketData': {'BI': [{'price': 128.05, 'size': 6}], 'LA': {'price': 128.05, 'size': 1, 'date': 1645390644137}, 'OF': [{'price': 128.16, 'size': 1}]}}
    #     message2 = {'type': 'Md', 'timestamp': 1645414957459, 'instrumentId': {'marketId': 'ROFX', 'symbol': 'DLR/FEB22'}, 'marketData': {'BI': [{'price': 107.05, 'size': 4}], 'LA': {'price': 108.9, 'size': 1.0, 'date': 1645316114985}, 'OF': [{'price': 108.1, 'size': 3}]}}







# log_in_1 = LogIn(user, password, account)
# get_data_1 = GetData(log_in_1, 'GGAL','YPFD','PAMP','DLR')
#
#
# print(get_data_1.spot)
# get_data_1.spot_df
# print(get_data_1.spot)
#
# print(get_data_1.instruments)
# get_data_1.instruments_load
# print(get_data_1.instruments)
#
# print(get_data_1.future_rest)
# get_data_1.future_rest_df
# print(get_data_1.future_rest)
#
# print(get_data_1.spot)
# print(get_data_1.future_rest)
#
# spot = get_data_1.spot
# future = get_data_1.future_rest
#
# get_tasa_1 = GetTasa(spot, future)
# get_tasa_1.tasas_futuros
# print(get_tasa_1.tasas)

if __name__ == "__main__":
    unittest.main()