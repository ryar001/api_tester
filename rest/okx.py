from abc import ABC, abstractmethod
from api_tester.rest.baseclass import RestBaseClass
from okx.Account import AccountAPI
from okx.Trade import TradeAPI
from okx.MarketData import MarketAPI
from okx.PublicData import PublicAPI
# You might need other APIs depending on specific needs, e.g., PublicAPI, FundingAPI


# Concrete implementation of RestBaseClass using python-okx
class OkxApi(RestBaseClass):
    PRICE_REQ=["limit","post_only","fok","ioc","mmp","mmp_and_post_only"]
    def __init__(self, spot_host="", perp_host="", api_key="", api_secret="", passphrase="", spot_symbol="", perp_symbol="", quantity=0.001, use_simulated=True):
        '''
        Initialize the OKX API client.
        Note: The python-okx library typically uses a single host and a passphrase
        for authentication, not separate spot_host and perp_host.
        We will use the provided api_key, api_secret, and passphrase.
        The host is usually derived from the library's internal configuration
        or can be specified during client initialization if needed, but the
        abstract method signature doesn't allow for passphrase.
        For simplicity and to match the abstract signature, we'll use the
        api_key and api_secret, and assume the library handles the host.
        A real implementation would likely require the passphrase.
        We'll add a 'passphrase' parameter to the concrete class's init
        for a more realistic implementation with the okx library.
        'use_simulated' is added to switch between live and demo trading.
        '''
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

        self.use_simulated = use_simulated
        self.spot_symbol = spot_symbol if spot_symbol else "BTC-USDT"
        self.perp_symbol = perp_symbol if perp_symbol else "BTC-USDT-SWAP"
        self.quantity = quantity
        self.flag = "1" if use_simulated else "0"

        # Initialize the OKX API clients
        # The python-okx library separates concerns into different API classes
        # We will initialize the necessary ones here.
        # Note: The host parameters in the abstract method are not directly
        # used by the python-okx client initialization in this way.
        # The library handles the endpoint URLs internally.
        self.account_api = AccountAPI(api_key, api_secret, passphrase,flag=self.flag)
        self.market_api = MarketAPI(api_key, api_secret, passphrase,flag=self.flag)
        self.trade_api = TradeAPI(api_key, api_secret, passphrase,flag=self.flag)
        self.public_api = PublicAPI(flag=self.flag)
        # Add other APIs if needed, e.g., self.public_api = PublicAPI.PublicAPI(...)

        print(f"OKX API client initialized, simulated: {self.use_simulated}")

    def get_spot_config(self, symbol=None):
        '''
        Test spot read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''
        inst_type = "SPOT"
        inst_id = symbol if symbol else self.spot_symbol

        # The get_instruments method is used to get instrument details
        result = self.public_api.get_instruments(instType=inst_type, instId=inst_id)
        return result

    def get_spot_balance(self):
        '''
        Test spot read - get account balances

        Returns:
            dict: Account balances
        '''
        # The get_balance method fetches account balance details
        result = self.account_api.get_account_balance()
        return result

    def get_fut_position(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_positions(instType="SWAP", instId=self.perp_symbol)
        return result

    def get_spot_price(self, symbol=None):
        '''
        Test spot read - get spot price

        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None.

        Returns:
            dict: Spot price
        '''
        inst_id = symbol if symbol else self.spot_symbol

        # The get_ticker method is used to get ticker information, including the last price
        result = float(self.market_api.get_ticker( instId=inst_id).get('data',[0])[0].get("last",0))
        return result
    
    def get_spot_open_orders(self):
        '''
        Test spot read - get open orders

        Returns:
            dict: Open orders
        '''
        # Fetch open spot orders
        result = self.trade_api.get_order_list(instType='SPOT', state='live')
        return result
    
    def get_fut_open_orders(self):
        '''
        Test futures/swap read - get open orders

        Returns:
            dict: Open orders
        '''
        # Fetch open futures/swap orders
        result = self.trade_api.get_order_list(instType='SWAP', state='live')
        return result
    
    def get_account_config(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        # Fetch account configuration
        result = self.account_api.get_account_config()
        return result
    
    def get_um_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        
        '''
        if symbol is None:
            symbol = self.perp_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_fee_rates(instType="SWAP", instId=symbol)
        return result
    
    def get_spot_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        
        '''
        if symbol is None:
            symbol = self.spot_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_fee_rates(instType="SPOT", instId=symbol)
        return result
    
    def get_spot_trades(self, instId='',uly='', ordId='', after='', before='', limit='', instFamily='',begin='',end=''):
        '''
        Test spot read - get spot trades

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None.
            order_id (str, optional): Order ID to get trades for. Defaults to None.
            start_time (int, optional): Start time to get trades for. Defaults to None.
            end_time (int, optional): End time to get trades for. Defaults to None.
            from_id (int, optional): Trade ID to get trades from. Defaults to None.
            limit (int, optional): Limit of trades to get. Defaults to None.

        Returns:
            dict: Spot trades
        '''
        # Fetch spot trades
        result = self.trade_api.get_fills(instType="SPOT", uly=uly, instId=instId, ordId=ordId, after=after, before=before, limit=limit, instFamily=instFamily,begin=begin,end=end)
        return result
    
    def get_um_trades(self, instId='',uly='', ordId='', after='', before='', limit='', instFamily='',begin='',end=''):
        '''
        Test futures/swap read - get futures trades

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None.
            order_id (str, optional): Order ID to get trades for. Defaults to None.
            start_time (int, optional): Start time to get trades for. Defaults to None.
            end_time (int, optional): End time to get trades for. Defaults to None.
            from_id (int, optional): Trade ID to get trades from. Defaults to None.
            limit (int, optional): Limit of trades to get. Defaults to None.

        Returns:
            dict: Futures trades
        '''
        # Fetch futures trades
        result = self.trade_api.get_fills(instType="SWAP", uly=uly, instId=instId, ordId=ordId, after=after, before=before, limit=limit, instFamily=instFamily,begin=begin,end=end)
        return result
    
    def _get_order_params(self, symbol, price, quantity, order_type,td_mode="cross",is_fut=False):
        if order_type not in self.PRICE_REQ:
            price = None
        else:
            if not price:
                return {"error": "Price is required for LIMIT order"}

        # for market orders, sz is in quote ccy
        if order_type == "market" and not is_fut:
            _price = self.get_spot_price(symbol)
            quantity = quantity * _price

        params = {"instId": symbol, "px": price, "sz": quantity, "ordType": order_type, "tdMode": td_mode}

        return {i:j for i, j in params.items() if j is not None}
    
    def buy_spot(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test spot write/trade - place a buy order

        Args:
            symbol (str): Symbol to buy
            price (float): Price to buy at
            quantity (float): Quantity to buy
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode)
        print(f"buy spot params: {params}")
        # Place a spot buy order
        result = self.trade_api.place_order(**params,side='buy')
        return result
    
    def sell_spot(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test spot write/trade - place a sell order

        Args:
            symbol (str): Symbol to sell
            price (float): Price to sell at
            quantity (float): Quantity to sell
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode)
        print(f"sell spot params: {params}")
        # Place a spot sell order
        result = self.trade_api.place_order(**params,side='sell')
        return result
    
    def open_long_fut(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test futures/swap write/trade - open a long position

        Args:
            symbol (str): Symbol to open long position
            price (float): Price to open at
            quantity (float): Quantity to open
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode,is_fut=True)
        print(f"open long fut params: {params}")
        # Place a futures buy order to open a long position

        result = self.trade_api.place_order(
            **params,
            side='buy',            # Order side (buy to open long)
            posSide='long'         # Position side (long, short)
        )
        return result
    
    def close_long_fut(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test futures/swap write/trade - close a long position

        Args:
            symbol (str): Symbol to close long position
            price (float): Price to close at
            quantity (float): Quantity to close
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode)
        print(f"close long fut params: {params}")
        # Place a futures sell order to close a long position
        result = self.trade_api.place_order(
            **params,
            side='sell',           # Order side (sell to close long)
            posSide='long'         # Position side (long, short)
        )
        return result
    
    def open_short_fut(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test futures/swap write/trade - open a short position

        Args:
            symbol (str): Symbol to open short position
            price (float): Price to open at
            quantity (float): Quantity to open
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode,is_fut=True)
        print(f"open short fut params: {params}")
        # Place a futures sell order to open a short position
        result = self.trade_api.place_order(
            **params,
            side='sell',           # Order side (sell to open short)
            posSide='short'        # Position side (long, short)
        )
        return result
    
    def close_short_fut(self, symbol, price, quantity, order_type='limit',td_mode="cross", **kwargs):
        '''
        Test futures/swap write/trade - close a short position

        Args:
            symbol (str): Symbol to close short position
            price (float): Price to close at
            quantity (float): Quantity to close
            order_type (str, optional): Order type. Defaults to 'limit'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        '''
        params = self._get_order_params(symbol, price, quantity, order_type,td_mode)
        print(f"close short fut params: {params}")
        # Place a futures buy order to close a short position
        result = self.trade_api.place_order(
            **params,
            side='buy',            # Order side (buy to close short)
            posSide='short'         # Position side (long, short)
        )
        return result

    def test_buy_spot(self):
        '''
        Test spot write/trade - place a buy order

        Returns:
            dict: Order response
        '''
        # Place a market buy order using the configured spot symbol and quantity
        result = self.trade_api.place_order(
            instId=self.spot_symbol,
            tdMode='cash',    # Trade mode (cash for spot)
            side='buy',       # Order side (buy)
            ordType='market', # Order type (market order)
            sz=str(self.quantity)  # Quantity
        )
        return result

    def test_sell_spot(self):
        '''
        Test spot write/trade - place a sell order

        Returns:
            dict: Order response
        '''
        # Place a market sell order using the configured spot symbol and quantity
        result = self.trade_api.place_order(
            instId=self.spot_symbol,
            tdMode='cash',     # Trade mode (cash for spot)
            side='sell',       # Order side (sell)
            ordType='market',  # Order type (market order)
            sz=str(self.quantity)   # Quantity
        )
        return result

    def get_perp_market_config(self, symbol=None):
        '''
        Test futures/swap read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        '''
        inst_type = "SWAP"
        inst_id = symbol if symbol else self.perp_symbol
        # The get_instruments method is used to get instrument details
        result = self.public_api.get_instruments(instType=inst_type, instId=inst_id)
        return result

    def cancel_spot_open_orders(self):
        '''
        Test spot write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''
        # Get all open spot orders
        open_orders = self.trade_api.get_order_list(instType='SPOT', state='live')

        # Check if there are any open orders
        if 'data' in open_orders and open_orders['data']:
            # Prepare a list to store cancellation results
            cancel_results = []

            # Cancel each open order
            for order in open_orders['data']:
                if 'instId' in order and 'ordId' in order:
                    cancel_result = self.trade_api.cancel_order(
                        instId=order['instId'],
                        ordId=order['ordId']
                    )
                    cancel_results.append(cancel_result)

            return {"message": "Cancelled spot open orders", "results": cancel_results}
        else:
            return {"message": "No open spot orders to cancel"}

    def cancel_fut_open_orders(self):
        '''
        Test futures/swap write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''
        # Get all open swap orders
        open_orders = self.trade_api.get_order_list(instType='SWAP', state='live')

        # Check if there are any open orders
        if 'data' in open_orders and open_orders['data']:
            # Prepare a list to store cancellation results
            cancel_results = []

            # Cancel each open order
            for order in open_orders['data']:
                if 'instId' in order and 'ordId' in order:
                    cancel_result = self.trade_api.cancel_order(
                        instId=order['instId'],
                        ordId=order['ordId']
                    )
                    cancel_results.append(cancel_result)

            return {"message": "Cancelled futures/swap open orders", "results": cancel_results}
        else:
            return {"message": "No open futures/swap orders to cancel"}
        
    def cancel_algo_open_orders(self):
        '''
        Test futures/swap write/trade - cancel all open algo orders

        Returns:
            dict: Order response
        '''
        # Get all open algo orders
        open_orders = self.trade_api.order_algos_list(ordType='conditional')

        # Check if there are any open orders
        if 'data' in open_orders and open_orders['data']:
            # Prepare a list to store cancellation results
            cancel_results = []

            # Cancel each open order
            cancel_result = self.trade_api.cancel_algo_order(
                [{'instId': order['instId'], 'algoId': order['algoId']} for order in open_orders['data']]
            )
            cancel_results.append(cancel_result)

            return {"message": "Cancelled futures/swap algo open orders", "results": cancel_results}
        else:
            return {"message": "No open futures/swap algo orders to cancel"}

    def get_fut_balance(self):
        '''
        Test futures/swap read - get futures account balance

        Returns:
            dict: Futures account balance
        '''
        # The get_balance method provides details including margin info relevant to futures/swaps
        result = self.account_api.get_account_balance()
        return result

    def test_open_long_fut(self,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        '''
        # Set leverage for the instrument (optional, can be done separately)
        self.account_api.set_leverage(
            instId=self.perp_symbol,
            lever='10',  # 10x leverage
            mgnMode='cross'  # Margin mode: cross or isolated
        )

        if qty_prec == 0:
            _qty = int(self.quantity / cont_size)
        else:
            _qty = round(self.quantity / cont_size, qty_prec)


        # Place a market order to open a long position
        result = self.trade_api.place_order(
            instId=self.perp_symbol,
            tdMode='cross',        # Trade mode (cross, isolated)
            side='buy',            # Order side (buy to open long)
            ordType='limit',      # Order type
            sz=str(_qty), # Quantity (contract size)
            posSide='long'         # Position side (long, short)
        )
        return result

    def test_close_long_fut(self,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        '''
        # Get current position to determine the size to close
        # positions = self.account_api.get_positions(instType="SWAP", instId=self.perp_symbol)

        if qty_prec == 0:
            _qty = int(self.quantity / cont_size)
        else:
            _qty = round(self.quantity / cont_size, qty_prec)
        # Check if there's an open long position
        # if 'data' in positions and positions['data']:
        #     for position in positions['data']:
        #         if position.get('posSide') == 'long' and float(position.get('pos', '0')) > 0:
        #             # Place a market order to close the long position
        result = self.trade_api.place_order(
            instId=self.perp_symbol,
            tdMode='cross',           # Trade mode
            side='sell',              # Order side (sell to close long)
            ordType='market',         # Order type
            sz=str(_qty),
            posSide='long'            # Position side being closed
        )
        return result

        # If no position found or position size is 0
        return {"message": "No long position to close"}

    def get_spot_open_orders(self):
        '''
        Test spot read - get open orders

        Returns:
            dict: Open orders
        '''
        # Get all open spot orders
        result = self.trade_api.get_order_list(instType='SPOT', state='live')
        return result

    def get_fut_open_orders(self):
        '''
        Test futures/swap read - get open orders

        Returns:
            dict: Open orders
        '''
        # Get all open swap orders
        result = self.trade_api.get_order_list(instType='SWAP', state='live')
        return result
    
    def get_account_config(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_account_config()
        return result
    
    def get_um_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        
        '''
        if symbol is None:
            symbol = self.perp_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_fee_rates(instType="SWAP", instId=symbol)
        return result
    
    def get_spot_comms_rate(self,symbol=None):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        
        '''
        if symbol is None:
            symbol = self.spot_symbol
        # Fetch SWAP positions for the specified symbol
        result = self.account_api.get_fee_rates(instType="SPOT", instId=symbol)
        return result
    
    def set_account_level(self,acct_lv):
        '''
        level:
            1: Spot
            2: Spot and futures mode.
            3: Multi-currency margin code.
            4: Portfolio margin mode.

        Returns:
            dict: Futures positions
        
        '''
        result = self.account_api.set_account_level(acctLv=acct_lv)
        return result
    
    def set_position_mode(self,pos_mode):
        '''
        pos_mode:
            long_short_mode
            net_mode

        Returns:
            dict: Futures positions
        
        '''
        result = self.account_api.set_position_mode(posMode=pos_mode)
        return result

    def funds_transfer(self, ccy: str, amt: str, from_account: str, to_account: str, type: str = "0", subAcct: str = "", instId: str = "", toInstId: str = "", loanTrans: bool = False, omitPosRisk: bool = False):
        '''
        Transfers funds between accounts.

        Args:
            ccy (str): Currency, e.g., "USDT".
            amt (str): Amount to transfer.
            from_account (str): Account to transfer from (e.g., "6" for Funding, "18" for Trading).
            to_account (str): Account to transfer to (e.g., "6" for Funding, "18" for Trading).
            type (str, optional): Transfer type. Defaults to "0" (internal).
            subAcct (str, optional): Sub-account name. Required if type is "1", "2", or "3".
            instId (str, optional): Instrument ID. Required for cross-currency transfers.
            toInstId (str, optional): To Instrument ID. Required for cross-currency transfers.
            loanTrans (bool, optional): Loan transfer. Defaults to False.
            omitPosRisk (bool, optional): Omit position risk. Defaults to False.

        Returns:
            dict: Transfer response.
        '''
        params = {
            "ccy": ccy,
            "amt": amt,
            "from": from_account,
            "to": to_account,
            "type": type,
            "subAcct": subAcct,
            "instId": instId,
            "toInstId": toInstId,
            "loanTrans": str(loanTrans).lower(), # Convert boolean to string "true" or "false"
            "omitPosRisk": str(omitPosRisk).lower() # Convert boolean to string "true" or "false"
        }
        # Filter out empty parameters
        params = {k: v for k, v in params.items() if v not in ["", False]}

        result = self.account_api.asset_transfer(**params)
        return result

# Example Usage (requires you to fill in your API details)
# api_key = "YOUR_API_KEY"
# api_secret = "YOUR_API_SECRET"
# passphrase = "YOUR_PASSPHRASE" # Essential for authentication with okx library
# use_simulated = True # Set to False for live trading

# try:
#     okx_client = OkxApi(api_key=api_key, api_secret=api_secret, passphrase=passphrase, use_simulated=use_simulated)

#     # Example calls (uncomment to test after filling in API details)
#     # print("Spot Config:", okx_client.get_spot_config(symbol='BTC-USDT'))
#     # print("Spot Balance:", okx_client.get_spot_balance())
#     # print("Futures Positions:", okx_client.get_fut_position())
#     # print("Spot Price (BTC-USDT):", okx_client.get_spot_price(symbol='BTC-USDT'))
#     # print("Spot Open Orders:", okx_client.get_spot_open_orders())

#     # Trade methods require parameters and caution! Use simulated trading first.
#     # print("Attempting to buy spot (placeholder):", okx_client.buy_spot())
#     # print("Attempting to cancel spot orders (placeholder):", okx_client.cancel_spot_open_orders())

# except Exception as e:
#     print(f"An error occurred: {e}")
