
from binance_sdk_spot.spot import SpotRestAPI
from binance_sdk_wallet.wallet import WalletRestAPI
from binance_sdk_derivatives_trading_usds_futures.derivatives_trading_usds_futures import DerivativesTradingUsdsFuturesRestAPI as UMFutures
from binance_common.configuration import ConfigurationRestAPI
from rest.baseclass import RestBaseClass
import math
import json


class binanceApi(RestBaseClass):

    @staticmethod
    def _extract_response_data(response):
        """
        Helper function to extract data from Binance SDK ApiResponse objects.

        Args:
            response: The response object from Binance SDK

        Returns:
            dict or list: The extracted data
        """
        if response is None:
            return None

        # If it's already a dict or list, return as is
        if isinstance(response, (dict, list, str, int, float)):
            return response

        # Try to get data attribute
        if hasattr(response, 'data'):
            return response.data

        # Try to convert to dict
        if hasattr(response, 'to_dict'):
            return response.to_dict()

        # Try to get the actual_instance attribute (common in OpenAPI generated clients)
        if hasattr(response, 'actual_instance'):
            return response.actual_instance

        # Try to serialize to JSON and back (last resort)
        try:
            if hasattr(response, '__dict__'):
                return response.__dict__
        except:
            pass

        # If all else fails, return string representation
        return str(response)

    def __init__(self, spot_host="",perp_host="",api_key="", api_secret="",default_symbol="BTCUSDT",default_quantity=0.001):
        '''
        Initialize the API client
        '''
        self.spot_host = spot_host if spot_host else "https://api.binance.com"
        self.perp_host = perp_host if perp_host else "https://fapi.binance.com"
        self.api_key = api_key
        self.api_secret = api_secret
        # Placeholder initialization
        self.spot_client:SpotRestAPI = SpotRestAPI(configuration=ConfigurationRestAPI(api_key=api_key, api_secret=api_secret, base_path=self.spot_host))
        self.futures_client:UMFutures = UMFutures(configuration=ConfigurationRestAPI(api_key=api_key, api_secret=api_secret, base_path=self.perp_host))
        self.wallet_client:WalletRestAPI = WalletRestAPI(configuration=ConfigurationRestAPI(api_key=api_key, api_secret=api_secret, base_path=self.spot_host))
        # Set default trading parameters
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity
        print("Binance API client initialized")

    def get_um_trades(self,**kwargs):
        ''''''

    def spot_user_universal_transfer_(self, type: str, asset: str, amount: str, **kwargs):
        """User Universal Transfer (USER_DATA)

        POST /sapi/v1/asset/transfer

        https://binance-docs.github.io/apidocs/spot/en/#user-universal-transfer-user_data

        Args:
            type (str)
            asset (str)
            amount (str)
        Keyword Args:
            fromSymbol (str, optional): Must be sent when type are ISOLATEDMARGIN_MARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            toSymbol (str, optional): Must be sent when type are MARGIN_ISOLATEDMARGIN and ISOLATEDMARGIN_ISOLATEDMARGIN
            recvWindow (int, optional): The value cannot be greater than 60000
        """
        result = self.wallet_client.user_universal_transfer(type=type,asset=asset,amount=amount,**kwargs)
        return self._extract_response_data(result)

    def send_usdt_from_spot_to_pm(self,amount:float):
        '''send usdt from spot to pm'''
        self.spot_user_universal_transfer_(type="MAIN_PORTFOLIO_MARGIN",asset="USDT",amount=amount)

    def get_spot_config(self, symbol=None):
        '''
        Test spot read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''
        try:
            if symbol is None:
                symbol = self.default_symbol
            exchange_info = self.spot_client.exchange_info(symbol=symbol)
            return self._extract_response_data(exchange_info)
        except Exception as e:
            print(f"Error getting spot config: {e}")
            return None
        
    def get_spot_trades(self, symbol=None, **kwargs):
        '''
        Test spot read - get account trades

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None.

        Returns:
            dict: Account trades
        '''
        try:
            if symbol is None:
                symbol = self.default_symbol
            trades = self.spot_client.my_trades(symbol=symbol, **kwargs)
            return self._extract_response_data(trades)
        except Exception as e:
            print(f"Error getting spot trades: {e}")
            return {"error": str(e)}
        
    def get_um_price(self, symbol=None):
        '''
        Test futures/swap read - get futures mark price

        Returns:
            dict: Futures mark price
        '''
        if symbol is None:
            symbol = self.default_symbol
        try:
            # Use the UM mark price endpoint for PM
            mark_price_response = self.futures_client.mark_price(symbol=symbol)
            mark_price_data = self._extract_response_data(mark_price_response)
            if isinstance(mark_price_data, dict) and "markPrice" in mark_price_data:
                return float(mark_price_data["markPrice"])
            elif isinstance(mark_price_data, list) and len(mark_price_data) > 0 and "markPrice" in mark_price_data[0]:
                return float(mark_price_data[0]["markPrice"])
            else:
                return {"error": f"Unexpected mark price response format: {mark_price_data}"}
        except Exception as e:
            print(f"Error getting futures mark price: {e}")
            return {"error": str(e)}

    def get_spot_balance(self):
        '''
        Test spot read - get account balances

        Returns:
            dict: Account balances
        '''
        print("Getting spot balance")
        # Implement using binance-connector-python
        try:
            account_info = self.spot_client.get_account()
            account_data = self._extract_response_data(account_info)
            if isinstance(account_data, dict) and 'balances' in account_data:
                return account_data.get('balances', [])
            else:
                return account_data
        except Exception as e:
            print(f"Error getting spot balance: {e}")
            return {"error": str(e)}

    def get_fut_position(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        print("Getting futures position")
        # Implement using binance-futures-connector-python
        try:
            # This endpoint gets all positions, filter as needed
            positions = self.futures_client.position_information_v2()
            return self._extract_response_data(positions)
        except Exception as e:
            print(f"Error getting futures position: {e}")
            return {"error": str(e)}

    def get_spot_price(self, symbol=None):
        '''
        Test spot read - get spot price

        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None.

        Returns:
            dict: Spot price
        '''
        try:
            if symbol is None:
                symbol = self.default_symbol
            ticker = self.spot_client.ticker_price(symbol=symbol)
            return self._extract_response_data(ticker)
        except Exception as e:
            print(f"Error getting spot price: {e}")
            return None

    def test_buy_spot(self,spot_config=None):
        '''
        Test spot write/trade - place a buy order

        Returns:
            dict: Order response
        '''
        print(f"Buying spot: {self.default_symbol}")
        # Implement using binance-connector-python
        if not spot_config:
            spot_config = self.get_spot_config(self.default_symbol)
            spot_config = spot_config['symbols'][0]
        price_precision = float([i for i in spot_config['filters'] if i['filterType'] == 'PRICE_FILTER'][0]['tickSize'])
        quantity_precision = float([i for i in spot_config['filters'] if i['filterType'] == 'LOT_SIZE'][0]['stepSize'])
        # convert to int precision from float 0.01 or 1e-05 -> 2 using exponential
        price_precision = abs(int(math.log10(price_precision)))
        quantity_precision = abs(int(math.log10(quantity_precision)))
        try:
            # Get current price to calculate a price below market
            ticker = self.get_spot_price(self.default_symbol)
            if not ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit buy order at 90% of current price to avoid execution
            current_price = float(ticker['price'])
            buy_price = round(current_price * 0.9, price_precision)

            params = {
                'symbol': self.default_symbol,
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': round(self.default_quantity, quantity_precision),
                'price': buy_price
            }

            order_result = self.spot_client.new_order(**params)
            order_data = self._extract_response_data(order_result)
            print(f"Spot buy order placed: {order_data}")
            return order_data
        except Exception as e:
            print(f"Error placing spot buy order: {e}")
            return {"error": str(e)}

    def test_sell_spot(self,spot_config=None):
        '''
        Test spot write/trade - place a sell order

        Returns:
            dict: Order response
        '''
        print(f"Selling spot: {self.default_symbol}")
        if not spot_config:
            spot_config = self.get_spot_config(self.default_symbol)
            spot_config = spot_config['symbols'][0]
        price_precision = float([i for i in spot_config['filters'] if i['filterType'] == 'PRICE_FILTER'][0]['tickSize'])
        quantity_precision = float([i for i in spot_config['filters'] if i['filterType'] == 'LOT_SIZE'][0]['stepSize'])
        # convert to int precision from float 0.01 or 1e-05 -> 2 using exponential
        price_precision = abs(int(math.log10(price_precision)))
        quantity_precision = abs(int(math.log10(quantity_precision)))
        try:
            # Get current price to calculate a price above market
            ticker = self.get_spot_price(self.default_symbol)
            if not ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit sell order at 110% of current price to avoid execution
            current_price = float(ticker['price'])
            sell_price = round(current_price * 1.1, price_precision)

            params = {
                'symbol': self.default_symbol,
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': round(self.default_quantity, quantity_precision),
                'price': sell_price
            }

            order_result = self.spot_client.new_order(**params)
            order_data = self._extract_response_data(order_result)
            print(f"Spot sell order placed: {self.default_symbol}")
            return order_data
        except Exception as e:
            print(f"Error placing spot sell order: {e}")
            return {"error": str(e)}

    def get_perp_market_config(self, symbol=None):
        '''
        Test futures/swap read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''
        try:
            if symbol is None:
                symbol = self.default_symbol
            exchange_info = self.futures_client.exchange_information()
            exchange_data = self._extract_response_data(exchange_info)
            if symbol and isinstance(exchange_data, dict) and 'symbols' in exchange_data:
                # Filter for the specific symbol
                symbols_info = [s for s in exchange_data.get('symbols', []) if s.get('symbol') == symbol]
                return symbols_info
            return exchange_data
        except Exception as e:
            print(f"Error getting futures market config: {e}")
            return None

    def cancel_spot_open_orders(self):
        '''
        Test spot write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''
        try:
            response = self.spot_client.delete_open_orders(symbol=self.default_symbol)
            return self._extract_response_data(response)
        except Exception as e:
            print(f"Error canceling open spot orders: {e}")
            return {"error": str(e)}

    def cancel_fut_open_orders(self):
        '''
        Test futures/swap write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''
        try:
            response = self.futures_client.cancel_all_open_orders(symbol=self.default_symbol)
            return self._extract_response_data(response)
        except Exception as e:
            print(f"Error canceling open futures orders: {e}")
            return {"error": str(e)}

    def get_fut_balance(self):
        '''
        Test futures/swap read - get futures account balance

        Returns:
            dict: Futures account balance
        '''
        try:
            response = self.futures_client.futures_account_balance_v2()
            return self._extract_response_data(response)
        except Exception as e:
            print(f"Error getting futures account balance: {e}")
            return {"error": str(e)}

    def test_open_long_fut(self,price_prec,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        '''
        print(f"Opening long futures position: {self.default_symbol}")
        # Implement using binance-futures-connector-python
        try:
            # Get current price to calculate a price below market
            ticker = self.futures_client.mark_price(symbol=self.default_symbol)
            ticker_data = self._extract_response_data(ticker)
            if not ticker_data:
                return {"error": "Failed to get mark price data"}

            # Extract mark price from response
            if isinstance(ticker_data, dict) and "markPrice" in ticker_data:
                current_price = float(ticker_data["markPrice"])
            elif isinstance(ticker_data, list) and len(ticker_data) > 0 and "markPrice" in ticker_data[0]:
                current_price = float(ticker_data[0]["markPrice"])
            else:
                return {"error": f"Unexpected mark price response format: {ticker_data}"}

            buy_price = round(current_price * 0.9, price_prec)

            # convert size to contract
            if qty_prec == 0:
                _qty = int(self.default_quantity / cont_size)
            else:
                _qty = round(self.default_quantity / cont_size, qty_prec)

            params = {
                'symbol': self.default_symbol,
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': _qty,
                'price': buy_price
            }

            order_result = self.futures_client.new_order(**params)
            order_data = self._extract_response_data(order_result)
            print(f"Futures long order placed: {order_data}")
            return order_data
        except Exception as e:
            print(f"Error opening long futures position: {e}")
            return {"error": str(e)}

    def test_close_long_fut(self,price_prec,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        '''
        print(f"Closing long futures position: {self.default_symbol}")
        # Implement using binance-futures-connector-python
        try:
            # Get current price to calculate a price above market
            ticker = self.futures_client.mark_price(symbol=self.default_symbol)
            ticker_data = self._extract_response_data(ticker)
            if not ticker_data:
                return {"error": "Failed to get mark price data"}

            # Extract mark price from response
            if isinstance(ticker_data, dict) and "markPrice" in ticker_data:
                current_price = float(ticker_data["markPrice"])
            elif isinstance(ticker_data, list) and len(ticker_data) > 0 and "markPrice" in ticker_data[0]:
                current_price = float(ticker_data[0]["markPrice"])
            else:
                return {"error": f"Unexpected mark price response format: {ticker_data}"}

            sell_price = round(current_price * 1.1, price_prec)

            # convert size to contract
            if qty_prec == 0:
                _qty = int(self.default_quantity / cont_size)
            else:
                _qty = round(self.default_quantity / cont_size, qty_prec)

            params = {
                'symbol': self.default_symbol,
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': _qty,
                'price': sell_price
            }

            order_result = self.futures_client.new_order(**params)
            order_data = self._extract_response_data(order_result)
            print(f"Futures close long order placed: {order_data}")
            return order_data
        except Exception as e:
            print(f"Error closing long futures position: {e}")
            return {"error": str(e)}

    def get_spot_open_orders(self):
        '''
        Test spot read - get open orders

        Returns:
            dict: Open orders
        '''
        try:
            response = self.spot_client.get_open_orders(symbol=self.default_symbol)
            return self._extract_response_data(response)
        except Exception as e:
            print(f"Error getting open spot orders: {e}")
            return {"error": str(e)}
        
    def get_fut_open_orders(self):
        '''
        Test futures/swap read - get open orders

        Returns:
            dict: Open orders
        '''
        try:
            response = self.futures_client.query_current_open_order(symbol=self.default_symbol)
            return self._extract_response_data(response)
        except Exception as e:
            print(f"Error getting open futures orders: {e}")
            return {"error": str(e)}
        
    def get_account_config(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        # Fetch SWAP positions for the specified symbol
        result = self.spot_client.get_account()
        return self._extract_response_data(result)
    
    def get_spot_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        if symbol is None:
            symbol = self.default_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.spot_client.account_commission(symbol=symbol)
        return self._extract_response_data(result)
    
    def get_um_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        if symbol is None:
            symbol = self.default_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.futures_client.user_commission_rate(symbol=symbol)
        return self._extract_response_data(result)

if __name__== "__main__":
    import yaml
    from pathlib import Path
    keys_path = Path(__file__).parent.parent / '.keys.yaml'
    with open(keys_path, 'r') as f:
        keys = yaml.safe_load(f)

    acct_dict = {}
    for name, key_data in keys['binance'].items():
        try:
            api_key = key_data['api_key']
            api_secret = key_data['api_secret']
            # Initialize the Binance PM Utils
            binance = binanceApi(api_key=api_key,api_secret= api_secret)
            acct_dict[name] = binance
        except KeyError:
            raise ValueError("No API keys found in .keys.yaml")
        
    breakpoint()
