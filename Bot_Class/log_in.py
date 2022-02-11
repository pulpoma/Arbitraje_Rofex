class LogIn():

    def __init__(self, user=str, password=str, account=str):
        self.user = user
        self.password = password
        self.account = account

        # self.instruments = []
        # self.tickers = ['GGAL', 'YPFD', 'PAMP', 'DLR']
        # self.environment = environment

    @property
    def initialize(self):
        import pyRofex as pyRofex

        pyRofex.initialize(user = self.user, password = self.password, account = self.account, environment = pyRofex.Environment.REMARKET)
        print("Initialized")
        # return pyRofex.initialize(user = self.user, password = self.password, account = self.account, environment = pyRofex.Environment.REMARKET)
        
    def __str__(self):
        return f"{self.user}, {self.password}, {self.account}"

    def __repr__(self):
        return f"LogIn({self.user}, {self.password}, {self.account})"

#     @property
#     def instruments_load(self):
#
#         instruments_step = []
#         instruments =[]
#         instrument_dict = pyRofex.get_all_instruments()['instruments']
#
#         for order in range(0, len(instrument_dict)):
#             instruments_step.append(pyRofex.get_all_instruments()['instruments'][order]['instrumentId']['symbol'])
#
#         for i in instruments_step:
#             for j in self.tickers:
#                 if (j in i) and (i.count('/') == 1):
#                     instruments.append(i)
#
#         self.instruments = instruments
#
#         print("Instruments Loaded")
#         return self.instruments
#
#
# log_in_1 = LogIn("luciomassimi3968", "feulrX6%", "REM3968")
# log_in_1.initialize

# import pyRofex as pyRofex
# pyRofex.initialize(user = "luciomassimi3968", password ="feulrX6%", account = "REM3968", environment = pyRofex.Environment.REMARKET)
