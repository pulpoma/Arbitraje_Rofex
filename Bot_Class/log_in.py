class LogIn():

    def __init__(self, user=str, password=str, account=str):
        self.user = user
        self.password = password
        self.account = account

    @property
    def initialize(self):
        """Crea un Log in por cuenta, lo pense asi para que sea mas comoda la organizacion de las cuentas en las que se van a correr los bot"""
        import pyRofex as pyRofex

        pyRofex.initialize(user = self.user, password = self.password, account = self.account, environment = pyRofex.Environment.REMARKET)
        print("Initialized")
        # return pyRofex.initialize(user = self.user, password = self.password, account = self.account, environment = pyRofex.Environment.REMARKET)
        
    def __str__(self):
        return f"{self.user}, {self.password}, {self.account}"

    def __repr__(self):
        return f"LogIn({self.user}, {self.password}, {self.account})"
