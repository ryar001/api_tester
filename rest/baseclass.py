from abc import ABC, abstractmethod


class RestBaseClass(ABC):
    @abstractmethod
    def __init__(self, spot_host="",perp_host="",api_key="", api_secret=""):
        '''
        Initialize the API client
        '''

    @abstractmethod
    def get_spot_config(self, symbol=None):
        '''
        Test spot read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''

    @abstractmethod
    def get_spot_balance(self):
        '''
        Test spot read - get account balances

        Returns:
            dict: Account balances
        '''

    @abstractmethod
    def get_fut_position(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''

    @abstractmethod
    def get_spot_price(self, symbol=None):
        '''
        Test spot read - get spot price

        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None.

        Returns:
            dict: Spot price
        '''

    @abstractmethod
    def test_buy_spot(self):
        '''
        Test spot write/trade - place a buy order

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def test_sell_spot(self):
        '''
        Test spot write/trade - place a sell order

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def get_perp_market_config(self, symbol=None):
        '''
        Test futures/swap read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''

    @abstractmethod
    def cancel_spot_open_orders(self):
        '''
        Test spot write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def cancel_fut_open_orders(self):
        '''
        Test futures/swap write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def get_fut_balance(self):
        '''
        Test futures/swap read - get futures account balance

        Returns:
            dict: Futures account balance
        '''

    @abstractmethod
    def test_open_long_fut(self):
        '''
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def test_close_long_fut(self):
        '''
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        '''

    @abstractmethod
    def get_spot_open_orders(self):
        '''
        Test spot read - get open orders

        Returns:
            dict: Open orders
        '''

    @abstractmethod
    def get_fut_open_orders(self):
        '''
        Test futures/swap read - get open orders

        Returns:
            dict: Open orders
        '''
    
    @abstractmethod
    def get_account_config(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''

    @abstractmethod
    def get_um_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: usd perp comms rates
        '''

    @abstractmethod
    def get_spot_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: comms rate info
        '''

    @abstractmethod
    def get_spot_trades(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: comms rate info
        '''

    @abstractmethod
    def get_um_trades(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: comms rate info
        '''
