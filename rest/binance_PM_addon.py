import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode
import websocket
from api_tester.rest.baseclass import RestBaseClass
from api_tester.rest.binance_api import binanceApi
# from binance.spot import Spot


class BinancePMClient:
    def __init__(self,api_key,api_secret,base_url):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def hashing(self,query_string):
        query_string = query_string
        return hmac.new(
            self.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def get_timestamp(self) -> int:
        """
        Get the current timestamp in milliseconds.

        Returns:
            int: The current timestamp in milliseconds.
        """
        return int(time.time() * 1000)

    def dispatch_request(self,apply_method):
        session = requests.Session()
        session.headers.update(
            {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": self.api_key}
        )
        methods = {
            "GET": session.get,
            "DELETE": session.delete,
            "PUT": session.put,
            "POST": session.post,
        }
        if apply_method == list(methods.keys())[0]:
            return methods.get('GET')
        elif apply_method == list(methods.keys())[1]:
            return methods.get('DELETE')
        elif apply_method == list(methods.keys())[2]:
            return methods.get('PUT')
        elif apply_method == list(methods.keys())[3]:
            return methods.get('POST')

    def send_signed_request(self, apply_method,url_path, payload={}):

        query_string = urlencode(payload)
        # replace single quote to double quote
        query_string = query_string.replace("%27", "%22")
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.get_timestamp())
        else:
            query_string = "timestamp={}".format(self.get_timestamp())

        url = (
            self.base_url +url_path+"?" + query_string + "&signature=" + self.hashing(query_string)
        )
        print("{} {}".format(apply_method, url))
        params = {"url": url, "params": {}}
        response = self.dispatch_request(apply_method)(**params)
        return response.json()

    def send_sined_request_variableParams(self,apply_method,url_path,payload={}):
        query_string = urlencode({k:v for k,v in payload.items() if v is not None})
        query_string = query_string.replace("%27", "%22")
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.get_timestamp())
        else:
            query_string = "timestamp={}".format(self.get_timestamp())

        url = (
            self.base_url +url_path+"?" + query_string + "&signature=" + self.hashing(query_string)
        )
        print("{} {}".format(apply_method, url))
        params = {"url": url, "params": {}}
        response = self.dispatch_request(apply_method)(**params)
        return response.json()

    def send_public_request(self,url_path,payload={}):
        query_string = urlencode(payload, True)
        url = self.base_url + url_path
        if query_string:
            url = url + "?" + query_string
        print("{}".format(url))
        response = self.dispatch_request("GET")(url=url)
        return response.json()
    def get_spot_trades(self,symbol,orderId=None,startTime=None,endTime=None,fromId=None,limit=None,recvWindow=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        params = {
            "symbol": symbol,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "fromId": fromId,
            "limit": limit,
            "recvWindow": recvWindow
        }
        return self.send_sined_request_variableParams("GET", "/papi/v1/margin/myTrades", params)
    
    def get_um_trades(self,symbol,orderId=None,startTime=None,endTime=None,fromId=None,limit=None,recvWindow=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        params = {
            "symbol": symbol,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "fromId": fromId,
            "limit": limit,
            "recvWindow": recvWindow
        }
        return self.send_sined_request_variableParams("GET", "/papi/v1/um/userTrades", params)
    
    def get_cm_trades(self,symbol,orderId=None,startTime=None,endTime=None,fromId=None,limit=None,recvWindow=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        params = {
            "symbol": symbol,
            "orderId": orderId,
            "startTime": startTime,
            "endTime": endTime,
            "fromId": fromId,
            "limit": limit,
            "recvWindow": recvWindow
        }
        return self.send_sined_request_variableParams("GET", "/papi/v1/cm/userTrades", params)

    def account_balance(self):
        account_balance = self.send_signed_request("GET","/papi/v1/balance")
        return account_balance

    def account_information(self):
        account_information = self.send_signed_request("GET","/papi/v1/account")
        return account_information

    def margin_max_borrow(self,params):
        """
        pass parameter asset
        """
        margin_max_borrow = self.send_signed_request('GET',"/papi/v1/margin/maxBorrowable",params)
        return margin_max_borrow

    def query_margin_max_withdraw(self,asset=None):
        """
        pass parameter asset
        """
        endpoint = "/papi/v1/margin/maxWithdraw"
        params = {'asset':asset}
        query_margin_max_withdraw = self.send_signed_request('GET',endpoint,params)
        return query_margin_max_withdraw

    def query_um_position_information(self,symbol=None):
        """
        pass symbol
        """
        if symbol !=None:
            params = {'symbol':symbol}
            query_um_position_information = self.send_signed_request('GET',"/papi/v1/um/positionRisk",params)
            return query_um_position_information
        else:
            query_um_position_information = self.send_signed_request('GET',"/papi/v1/um/positionRisk")
            return query_um_position_information

    def query_cm_position_information(self,marginAsset=None,pair=None):
        endpoint = "/papi/v1/cm/positionRisk"
        params = {'marginAsset':marginAsset,
                  "pair":pair}
        query_cm_position_information = self.send_sined_request_variableParams('GET',endpoint,params)
        return query_cm_position_information

    def change_um_initial_leverage(self,symbol,leverage=int):
        params = {'symbol':symbol,
                  'leverage':leverage}
        change_um_initial_leverage = self.send_signed_request("POST",'/papi/v1/um/leverage',params)
        return change_um_initial_leverage

    def change_cm_initial_leverage(self,symbol,leverage=int):
        params = {'symbol':symbol,
                  'leverage':leverage}
        change_cm_initial_leverage = self.send_signed_request("POST",'/papi/v1/um/leverage',params)
        return change_cm_initial_leverage

    def change_um_position_mode(self,dualSidePosition):
        '''
        dualSidePosition
        true: Hedge Mode
        false: One-way Mode
        '''
        params = {'dualSidePosition':dualSidePosition}
        change_um_position_mode = self.send_signed_request("POST","/papi/v1/um/positionSide/dual",params)
        return change_um_position_mode

    def get_um_current_position_mode(self):
        get_um_current_position_mode = self.send_signed_request("GET",'/papi/v1/um/positionSide/dual')
        return get_um_current_position_mode

    def get_cm_current_position_mode(self):
        get_cm_current_position_mode = self.send_signed_request("GET",'/papi/v1/cm/positionSide/dual')
        return get_cm_current_position_mode

    def um_account_trade_list(self,symbol,starTime=None, endTime=None,fromId=None,limit=None):
        endpoint = "/papi/v1/um/userTrades"
        params = {
            "symbol": symbol,
            "startTime": starTime,
            "endTime": endTime,
            "fromId": fromId,
            "limit": limit,
        }
        um_account_trade_list = self.send_sined_request_variableParams("GET",endpoint,params)
        return um_account_trade_list

    def cm_account_trade_list(self,symbol,starTime=None, endTime=None,fromId=None,recvWindow=None,limit=None):
        endpoint = "/papi/v1/cm/userTrades"
        params = {
            "symbol": symbol,
            "startTime": starTime,
            "endTime": endTime,
            "fromId": fromId,
            "recvWindow":recvWindow,
            "limit": limit
        }
        cm_account_trade_list = self.send_sined_request_variableParams("GET",endpoint,params)
        return cm_account_trade_list

    def um_notional_and_leverage_brackets(self,symbol=None,recvWindow=None):
        endpoint = "/papi/v1/um/leverageBracket"
        params = {
            'symbol':symbol,
            'recvWindow':recvWindow
        }
        um_notional_and_leverage_brackets = self.send_sined_request_variableParams('GET',endpoint,params)
        return um_notional_and_leverage_brackets

    def cm_notional_and_leverage_brackets(self,symbol=None,recvWindow=None):
        endpoint = "/papi/v1/cm/leverageBracket"
        params = {
            'symbol':symbol,
            'recvWindow':recvWindow
        }
        cm_notional_and_leverage_brackets = self.send_sined_request_variableParams('GET',endpoint,params)
        return cm_notional_and_leverage_brackets

    def query_user_margin_force_orders(self,starTime=None,endTime=None,current=None,size=None,recvWindow=None):
        endpoint = "/papi/v1/margin/forceOrders"
        params = {
            'startTime':starTime,
            'endTime':endTime,
            'current':current,
            'size':size,
            "recvWindow":recvWindow
        }
        query_user_margin_force_orders = self.send_sined_request_variableParams("GET",endpoint,params)
        return query_user_margin_force_orders

    def query_user_um_force_orders(self,symbol=None,autoCloseType=None,starTime=None,endTime=None,limit=None,recvWindow=None):
        """
        autoCloseType (ENUM): LIQUIDATION / ADL,
        if starTime not sent, data within 7 days before endTime can be queried.
        """
        endpoint = "/papi/v1/um/forceOrders"
        params = {
            "symbol":symbol,
            "autoCloseType":autoCloseType,
            'startTime':starTime,
            'endTime':endTime,
            'limit':limit,
            "recvWindow":recvWindow
        }
        query_user_um_force_orders = self.send_sined_request_variableParams("GET",endpoint,params)
        return query_user_um_force_orders

    def query_user_cm_force_orders(self,symbol=None,autoCloseType=None,starTime=None,endTime=None,limit=None,recvWindow=None):
        """
        autoCloseType (ENUM): LIQUIDATION / ADL,
        if starTime not sent, data within 7 days before endTime can be queried.
        """
        endpoint = "/papi/v1/cm/forceOrders"
        params = {
            "symbol":symbol,
            "autoCloseType":autoCloseType,
            'startTime':starTime,
            'endTime':endTime,
            'limit':limit,
            "recvWindow":recvWindow
        }
        query_user_cm_force_orders = self.send_sined_request_variableParams("GET",endpoint,params)
        return query_user_cm_force_orders

    def PM_um_trading_quantitative_rules_indicators(self,symbol=None,recvWindow=None):
        endpoint = "/papi/v1/um/apiTradingStatus"
        params = {
            'symbol':symbol,
            "recvWindow":recvWindow
        }
        PM_um_trading_quantitative_rules_indicators = self.send_sined_request_variableParams("GET",endpoint,params)
        return PM_um_trading_quantitative_rules_indicators

    def get_user_commission_rate_for_um(self,symbol):
        endpoint = "/papi/v1/um/commissionRate"
        params = {'symbol':symbol}
        get_user_commission_rate_for_um = self.send_sined_request_variableParams('GET',endpoint,params)
        return get_user_commission_rate_for_um

    def get_user_commission_rate_for_cm(self,symbol):
        endpoint = "/papi/v1/cm/commissionRate"
        params = {'symbol':symbol}
        get_user_commission_rate_for_cm = self.send_sined_request_variableParams('GET',endpoint,params)
        return get_user_commission_rate_for_cm

    def query_margin_loan_record(self,asset,txId=None,starTime=None,endTime=None,current=1,size=None,archived="false",recvWindow=None):
        """
        txId: tranId in POST /papi/v1/marginLoan,
        current: querying page, start from 1, default 1,
        archived: Default: false. Set to true for archived data from 6 months ago
        https://binance-docs.github.io/apidocs/pm/en/#query-margin-loan-record-user_data
        """
        endpoint = "/papi/v1/margin/marginLoan"
        params = {
            "asset":asset,
            "txId":txId,
            "starTime":starTime,
            "endTime":endTime,
            "current":current,
            "size":size,
            "archived":archived,
            "recvWindow":recvWindow
        }
        query_margin_loan_record = self.send_sined_request_variableParams('GET',endpoint,params)
        return query_margin_loan_record

    def query_margin_repay_record(self,asset,txId=None,starTime=None,endTime=None,current=1,size=None,archived="false",recvWindow=None):
        """
        txId: tranId in POST /papi/v1/marginLoan,
        current: querying page, start from 1, default 1,
        archived: Default: false. Set to true for archived data from 6 months ago
        https://binance-docs.github.io/apidocs/pm/en/#query-margin-repay-record-user_data
        """
        endpoint = "/papi/v1/margin/repayLoan"
        params = {
            "asset":asset,
            "txId":txId,
            "starTime":starTime,
            "endTime":endTime,
            "current":current,
            "size":size,
            "archived":archived,
            "recvWindow":recvWindow
        }
        query_margin_repay_record = self.send_sined_request_variableParams('GET',endpoint,params)
        return query_margin_repay_record

    def get_margin_borrow_loan_interest_history(self,asset,txId=None,starTime=None,endTime=None,current=1,size=None,archived="false",recvWindow=None):
        """
        txId: tranId in POST /papi/v1/marginLoan,
        current: querying page, start from 1, default 1,
        archived: Default: false. Set to true for archived data from 6 months ago
        https://binance-docs.github.io/apidocs/pm/en/#get-margin-borrow-loan-interest-history-user_data
        """
        endpoint = "/papi/v1/margin/marginInterestHistory"
        params = {
            "asset":asset,
            "txId":txId,
            "starTime":starTime,
            "endTime":endTime,
            "current":current,
            "size":size,
            "archived":archived,
            "recvWindow":recvWindow
        }
        query_margin_repay_record = self.send_sined_request_variableParams('GET',endpoint,params)
        return query_margin_repay_record

    def query_PM_interest_history(self,asset=None,starTime=None,endTime=None,size=10,recvWindow=None):
        '''
        query user's portfolio margin interest history.
        '''
        endpoint = "/papi/v1/portfolio/interest-history"
        params = {
            'asset':asset,
            'starTime':starTime,
            'endTime':endTime,
            'size':size,
            'recvWindow':recvWindow
        }
        query_PM_interest_history = self.send_sined_request_variableParams("GET",endpoint,params)
        return query_PM_interest_history

    def fund_auto_collection(self,asset=None,recvWindow=None):
        """
        Fund collection for Portfolio Margin
        """
        endpoint = "/papi/v1/auto-collection"
        params = {'asset':asset,"recvWindow":recvWindow}
        fund_auto_collection  = self.send_sined_request_variableParams("POST",endpoint,params)
        return fund_auto_collection

    def bnb_transfer(self,amount,transferSide,recvWindow=None):
        """
        transferSide (ENUM): "TO_UM" or "FROM_UM"
        """
        endpoint = "/papi/v1/bnb-transfer"
        params = {
            'amount':amount,
            'transferSide':transferSide,
            "recvWindow":recvWindow
        }
        bnb_transfer = self.send_sined_request_variableParams("POST",endpoint,params)
        return bnb_transfer

    def create_listenKey(self):
        headers = {'X-MBX-APIKEY': self.api_key}
        print(headers)
        listenKey = requests.post("https://papi.binance.com/papi/v1/listenKey",headers=headers)
        return listenKey.json()

    def update_listenKey(self):
        headers = {'X-MBX-APIKEY': self.api_key}
        listenKey = requests.put("https://papi.binance.com/papi/v1/listenKey",headers=headers)
        return listenKey.json()

    def delete_listenKey(self):
        headers = {'X-MBX-APIKEY': self.api_key}
        listenKey = requests.delete("https://papi.binance.com/papi/v1/listenKey",headers=headers)
        return listenKey.json()

    def user_stream(self,listenKey):
        stream_url = f"wss://fstream.binance.com/pm/stream/ws/{listenKey}"
        def on_message(_,message):
            print(message)
        ws = websocket.WebSocketApp(stream_url,on_message=on_message)
        ws.run_forever()

    def asset_collection(self,asset,recvWindow=None):
        '''transfer from portfolio margin account to margin account, need to do before sending back to spot account

        From support chat:
        Transfers in and out of Portfolio Margin Account can only be done through Cross Margin Wallets. 
        For POST /sapi/v1/asset/transfer,
        only below parameters can be supported for the Portfolio Margin Pro Program and the new Portfolio Margin Program: MAIN_PORTFOLIO_MARGIN and PORTFOLIO_MARGIN_MAIN

        So you will need to first transfers specific asset from Futures Account to Margin account with POST /papi/v1/asset-collection (https://binance-docs.github.io/apidocs/pm/en/#fund-collection-by-asset-trade) and then use POST /sapi/v1/asset/transfer to transfer that amount from your PM Cross Margin wallet to your Spot wallet.

        '''
        params = {"asset":asset,"recvWindow":recvWindow}
        asset_collection = self.send_signed_request("POST","/papi/v1/asset-collection",params)
        return asset_collection

class BinancePmTestWrapper(RestBaseClass):
    def __init__(self, spot_host="", perp_host="",pm_host="", api_key="", api_secret="", default_symbol="BTCUSDT", default_quantity=0.001):
        """
        Initialize the API client for Binance Portfolio Margin

        Args:
            spot_host (str): The host URL for spot API
            perp_host (str): The host URL for perpetual futures API (not used in PM as it uses a single endpoint)
            api_key (str): API key
            api_secret (str): API secret
            default_symbol (str): Default trading symbol
            default_quantity (float): Default trading quantity
        """

        # For Portfolio Margin, we use the same base URL for both spot and futures
        self.pm_host = pm_host if pm_host else "https://papi.binance.com"
        self.perp_host = perp_host if perp_host else "https://fapi.binance.com"
        self.spot_host = spot_host if spot_host else "https://api.binance.com"
        
        # perp_host is not used for Portfolio Margin as it uses a single endpoint

        self.client = BinancePMClient(api_key, api_secret, self.pm_host)
        self.api_key = api_key
        self.api_secret = api_secret
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity

        self.spot_api = binanceApi(api_key=api_key, api_secret=api_secret, spot_host=self.spot_host, perp_host=self.perp_host)
        print(f"Binance Portfolio Margin API client initialized\nspot_host: {spot_host}, perp_host: {perp_host}")

    def transfer_to_spot(self,asset:str,amount:float,**_):
        '''transfer to spot'''
        print(f"Transfer to Margin account: {self.client.asset_collection(asset,amount)}")
        self.spot_api.spot_user_universal_transfer_("PORTFOLIO_MARGIN_MAIN",asset,amount)
    
    def send_usdt_from_spot_to_pm(self,amount:float):
        '''send usdt from spot to pm'''
        self.spot_api.spot_user_universal_transfer_("MAIN_PORTFOLIO_MARGIN","USDT",amount)

    def get_spot_config(self, symbol=None):
        """
        Test spot read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        """
        try:
            if symbol is None:
                symbol = self.default_symbol
            # For PM, we need to use the exchange info endpoint
            exchange_info = self.spot_api.get_spot_config(symbol=symbol)
            return exchange_info
        except Exception as e:
            print(f"Error getting spot config: {e}")
            return {"error": str(e)}

    def get_spot_balance(self):
        """
        Test spot read - get account balances

        Returns:
            dict: Account balances
        """
        print("Getting spot account balance")
        try:
            # Use the account balance endpoint for PM
            account_balance = self.spot_api.get_spot_balance()
            # filter for non zero
            account_balance = [i for i in account_balance if float(i['free']) or float(i['locked'])]
            return account_balance
        except Exception as e:
            print(f"Error getting spot account balance: {e}")
            return {"error": str(e)}

    def get_pm_balance(self):
        """
        Test spot read - get account balances

        Returns:
            dict: Account balances
        """
        print("Getting PM balance")
        try:
            # Use the account balance endpoint for PM
            account_balance = self.client.account_balance()
            return account_balance
        except Exception as e:
            print(f"Error getting spot balance: {e}")
            return {"error": str(e)}
        
    def get_um_price(self, symbol=None):
        """
        Test futures/swap read - get futures mark price

        Returns:
            dict: Futures mark price
        """
        if symbol is None:
            symbol = self.default_symbol
        try:
            # Use the UM mark price endpoint for PM
            mark_price = self.spot_api
            return mark_price
        except Exception as e:
            print(f"Error getting futures mark price: {e}")
            return {"error": str(e)}

    def get_fut_position(self):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        print("Getting futures positions")
        try:
            # Use the UM position information endpoint for PM
            positions = self.client.query_um_position_information()
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}

    def get_spot_price(self, symbol=None):
        """
        Test spot read - get spot price

        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None.

        Returns:
            dict: Spot price
        """
        try:
            if symbol is None:
                symbol = self.default_symbol
            # Use the public request to get ticker price
            ticker = self.spot_api.get_spot_price(symbol=symbol)
            return ticker
        except Exception as e:
            print(f"Error getting spot price: {e}")
            return {"error": str(e)}

    def _get_spot_params(self, symbol, price, quantity, order_type, time_in_force):
        if order_type == "MARKET":
            price = None
            if time_in_force:
                time_in_force = None
        else:
            if not price:
                return {"error": "Price is required for LIMIT order"}
            if not time_in_force:
                time_in_force = "GTC"

        params = {"symbol": symbol, "price": price, "quantity": quantity, "timeInForce": time_in_force,"type": order_type}

        return {i:j for i, j in params.items() if j is not None}

    def buy_spot(self, symbol=None, price=None, quantity=None, order_type='LIMIT', time_in_force='GTC'):
        """
        Place a spot buy order

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Defaults to None (calculated based on current price).
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        """
        params = self._get_spot_params(symbol, price, quantity, order_type, time_in_force)
        params.update({"side": "BUY"})
        try:

            print(f"Buying spot: {params}")
            # Use the margin order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/margin/order", params)
            print(f"Spot buy order placed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error placing spot buy order: {e}")
            return {"error": str(e)}
        
    def sell_spot(self, symbol=None, price=None, quantity=None, order_type='LIMIT', time_in_force='GTC'):
        """
        Place a spot sell order

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Defaults to None (calculated based on current price).
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).   
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        """
        params = self._get_spot_params(symbol, price, quantity, order_type, time_in_force)
        params.update({"side": "SELL"})
        try:
            print(f"Selling spot: {params}")
            # Use the margin order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/margin/order", params)
            print(f"Spot sell order placed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error placing spot sell order: {e}")
            return {"error": str(e)}

    def test_buy_spot(self):
        """
        Test spot write/trade - place a buy order

        Returns:
            dict: Order response
        """
        print(f"Buying spot: {self.default_symbol}")
        try:
            # Get current price to calculate a price below market
            ticker = self.get_spot_price(self.default_symbol)
            if "error" in ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit buy order at 90% of current price to avoid execution
            current_price = float(ticker['price'])
            buy_price = round(current_price * 0.9, 2)  # Simplified precision
            params = {
                'symbol': self.default_symbol,
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': self.default_quantity,
                'price': buy_price
            }

            # Use the margin order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/margin/order", params)
            print(f"Spot buy order placed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error placing spot buy order: {e}")
            return {"error": str(e)}

    def test_sell_spot(self):
        """
        Test spot write/trade - place a sell order

        Returns:
            dict: Order response
        """
        print(f"Selling spot: {self.default_symbol}")
        try:
            # Get current price to calculate a price above market
            ticker = self.get_spot_price(self.default_symbol)
            if "error" in ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit sell order at 110% of current price to avoid execution
            current_price = float(ticker['price'])
            sell_price = round(current_price * 1.1, 2)  # Simplified precision

            params = {
                'symbol': self.default_symbol,
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': self.default_quantity,
                'price': sell_price
            }

            # Use the margin order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/margin/order", params)
            print(f"Spot sell order placed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error placing spot sell order: {e}")
            return {"error": str(e)}

    def get_perp_market_config(self, symbol=None):
        """
        Test futures/swap read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None.

        Returns:
            dict: Market config
        """
        try:
            if symbol is None:
                symbol = self.default_symbol
            # For PM, we use the exchange info endpoint
            exchange_info = self.spot_api.get_perp_market_config(symbol=symbol)
            return exchange_info
        except Exception as e:
            print(f"Error getting perp market config: {e}")
            return {"error": str(e)}

    def cancel_spot_open_orders(self,symbol=None):
        """
        Test spot write/trade - cancel all open orders

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol
        print(f"Cancelling all spot open orders for {symbol}")
        try:
            # Use the margin cancel all open orders endpoint for PM
            result = self.client.send_signed_request("DELETE", "/papi/v1/margin/openOrders", {"symbol": symbol})
            print(f"Cancelled all spot open orders: {result}")
            return result
        except Exception as e:
            print(f"Error cancelling spot open orders: {e}")
            return {"error": str(e)}

    def cancel_fut_open_orders(self,symbol=None):
        """
        Test futures/swap write/trade - cancel all open orders

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol
        print(f"Cancelling all futures open orders for {symbol}")
        try:
            # Use the UM cancel all open orders endpoint for PM
            result = self.client.send_signed_request("DELETE", "/papi/v1/um/allOpenOrders", {"symbol": symbol})
            print(f"Cancelled all futures open orders: {result}")
            return result
        except Exception as e:
            print(f"Error cancelling futures open orders: {e}")
            return {"error": str(e)}

    def get_fut_balance(self):
        """
        Test futures/swap read - get futures account balance

        Returns:
            dict: Futures account balance
        """
        print("Getting futures account balance")

        try:
            # Use the account balance endpoint for PM
            account_balance = self.client.account_balance()
            # Filter for UM wallet balance
            for asset in account_balance:
                if "umWalletBalance" in asset:
                    return asset
            return account_balance
        except Exception as e:
            print(f"Error getting futures account balance: {e}")
            return {"error": str(e)}
        
    def _get_fut_params(self, symbol, price, qty, order_type, time_in_force):
        if order_type == "MARKET":
            price = None
            if time_in_force:
                time_in_force = None
        else:
            if not price:
                return {"error": "Price is required for LIMIT order"}
            if not time_in_force:
                time_in_force = "GTC"


        params = {"symbol": symbol, "price": price, "quantity": qty, "timeInForce": time_in_force,"type": order_type}

        return {i:j for i, j in params.items() if j is not None}

    def open_long_fut(self,symbol,qty,price=None,order_type="LIMIT",time_in_force=""):
        """
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        """
        params = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        params.update({"side": "BUY", "positionSide": "LONG"})
        try:
            params.update({"side": "BUY", "positionSide": "LONG"})
            print(f"Opening long futures position: {params}")
            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures long position opened: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error opening long futures position: {e}")
            return {"error": str(e)}
        
    def close_long_fut(self,symbol,qty,price=None,order_type="LIMIT",time_in_force=""):
        """
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        """
        params = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        params.update({"side": "SELL", "positionSide": "LONG"})

        try:
            print(f"Closing long futures position: {params}")
            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures long position closed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error closing long futures position: {e}")
            return {"error": str(e)}
    
    def open_short_fut(self,symbol,qty,price=None,order_type="LIMIT",time_in_force=""):
        """
        Test futures/swap write/trade - open a short position

        Returns:
            dict: Order response
        """
        params = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        params.update({"side": "SELL", "positionSide": "SHORT"})

        try:
            print(f"Opening short futures position: {params}")
            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures short position opened: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error opening short futures position: {e}")
            return {"error": str(e)}
        
    def close_short_fut(self,symbol,qty,price=None,order_type="LIMIT",time_in_force=""):
        """
        Test futures/swap write/trade - close a short position

        Returns:
            dict: Order response
        """
        params = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        params.update({"side": "BUY", "positionSide": "SHORT"})
        try:
            
            print(f"Closing short futures position: {params}")
            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures short position closed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error closing short futures position: {e}")
            return {"error": str(e)}

    def test_open_long_fut(self):
        """
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        """
        print(f"Opening long futures position: {self.default_symbol}")
        try:
            # Get current price to calculate a price below market
            ticker = self.get_spot_price(self.default_symbol)
            if "error" in ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit buy order at 90% of current price to avoid execution
            current_price = float(ticker['price'])
            buy_price = round(current_price * 0.9, 2)  # Simplified precision

            params = {
                'symbol': self.default_symbol,
                'side': 'BUY',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': self.default_quantity,
                'price': buy_price,
                'positionSide': 'LONG'  # For hedge mode
            }

            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures long position opened: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error opening long futures position: {e}")
            return {"error": str(e)}

    def test_close_long_fut(self):
        """
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        """
        print(f"Closing long futures position: {self.default_symbol}")
        try:
            # Get current position to determine quantity to close
            positions = self.get_fut_position()
            position_qty = 0

            # Find the long position for the default symbol
            if isinstance(positions, list):
                for position in positions:
                    if position.get('symbol') == self.default_symbol and position.get('positionSide') == 'LONG':
                        position_qty = float(position.get('positionAmt', 0))
                        break

            if position_qty <= 0:
                return {"error": "No long position to close"}

            # Get current price
            ticker = self.get_spot_price(self.default_symbol)
            if "error" in ticker:
                return {"error": "Failed to get ticker data"}

            # Place a limit sell order at 110% of current price to avoid execution
            current_price = float(ticker['price'])
            sell_price = round(current_price * 1.1, 2)  # Simplified precision

            params = {
                'symbol': self.default_symbol,
                'side': 'SELL',
                'type': 'LIMIT',
                'timeInForce': 'GTC',
                'quantity': abs(position_qty),
                'price': sell_price,
                'positionSide': 'LONG',  # For hedge mode
                'reduceOnly': 'true'
            }

            # Use the UM order endpoint for PM
            order_result = self.client.send_signed_request("POST", "/papi/v1/um/order", params)
            print(f"Futures long position closed: {order_result}")
            return order_result
        except Exception as e:
            print(f"Error closing long futures position: {e}")
            return {"error": str(e)}

    def get_spot_open_orders(self,symbol=None):
        """
        Test spot read - get open orders

        Returns:
            dict: Open orders
        """
        if symbol is None:
            symbol = self.default_symbol
        print(f"Getting spot open orders for {symbol}")
        try:
            # Use the margin open orders endpoint for PM
            open_orders = self.client.send_signed_request("GET", "/papi/v1/margin/openOrders", {"symbol": symbol})
            return open_orders
        except Exception as e:
            print(f"Error getting spot open orders: {e}")
            return {"error": str(e)}

    def get_fut_open_orders(self,symbol=None):
        """
        Test futures/swap read - get open orders

        Returns:
            dict: Open orders
        """
        if symbol is None:
            symbol = self.default_symbol
        print(f"Getting futures open orders for {symbol}")
        try:
            # Use the UM open orders endpoint for PM
            open_orders = self.client.send_signed_request("GET", "/papi/v1/um/openOrders", {"symbol": symbol})
            return open_orders
        except Exception as e:
            print(f"Error getting futures open orders: {e}")
            return {"error": str(e)}

    def get_account_config(self):
        """
        Test futures/swap read - get account configuration

        Returns:
            dict: Account configuration
        """
        print("Getting account configuration")
        try:
            # Use the account information endpoint for PM
            account_info = self.client.account_information()
            return account_info
        except Exception as e:
            print(f"Error getting account configuration: {e}")
            return {"error": str(e)}
        
    def get_um_comms_rate(self,symbol=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions

        {
            "symbol": "BTCUSDT",
            "makerCommissionRate": "0.0002",  // 0.02%
            "takerCommissionRate": "0.0004"   // 0.04%
        }
        """
        try:
            # Use the UM position information endpoint for PM
            positions = self.client.get_user_commission_rate_for_um(symbol=symbol)
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}

    def get_spot_comms_rate(self,symbol=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions

        {
            "symbol": "BTCUSDT",
            "makerCommissionRate": "0.0002",  // 0.02%
            "takerCommissionRate": "0.0004"   // 0.04%
        }
        """
        try:
            # Use the UM position information endpoint for PM
            positions = self.spot_api.get_spot_comms_rate(symbol=symbol)
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}
    
    def get_spot_trades(self,symbol=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        try:
            # Use the UM position information endpoint for PM
            positions = self.client.get_spot_trades(symbol=symbol)
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}
        
    def get_um_trades(self,symbol=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        try:
            # Use the UM position information endpoint for PM
            positions = self.client.get_um_trades(symbol=symbol)
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}
        
    def get_cm_trades(self,symbol=None):
        """
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        """
        try:
            # Use the UM position information endpoint for PM
            positions = self.client.get_cm_trades(symbol=symbol)
            return positions
        except Exception as e:
            print(f"Error getting futures positions: {e}")
            return {"error": str(e)}
    
    
# Add a test function to verify the implementation
if __name__ == "__main__":
    import yaml
    from pathlib import Path

    def test_binance_pm_wrapper():
        """Test the BinancePmTestWrapper implementation"""
        print("Testing BinancePmTestWrapper...")

        # Try to load API keys from .keys.yaml
        keys_path = Path(__file__).parent.parent / '.keys.yaml'
        api_key = ""
        api_secret = ""

        try:
            if keys_path.exists():
                with open(keys_path, 'r') as f:
                    keys = yaml.safe_load(f)

                if 'binance' in keys:
                    binance_keys = keys['binance']
                    # Get the first key
                    for _, key_data in binance_keys.items():
                        api_key = key_data.get('api_key', '')
                        api_secret = key_data.get('api_secret', '')
                        break
        except Exception as e:
            print(f"Error loading API keys: {e}")

        # Initialize the wrapper
        wrapper = BinancePmTestWrapper(
            api_key=api_key,
            api_secret=api_secret,
            default_symbol="BTCUSDT",
            default_quantity=0.001
        )

        # Test basic read operations that don't require authentication
        print("\n--- Testing Public Endpoints ---")

        # Test get_spot_config
        print("\nTesting get_spot_config...")
        spot_config = wrapper.get_spot_config()
        print(f"Spot config: {spot_config.keys() if isinstance(spot_config, dict) else 'Error'}")

        # Test get_spot_price
        print("\nTesting get_spot_price...")
        spot_price = wrapper.get_spot_price()
        print(f"Spot price: {spot_price}")

        # If API keys are provided, test authenticated endpoints
        if api_key and api_secret:
            print("\n--- Testing Authenticated Endpoints ---")

            # Test get_spot_balance
            print("\nTesting get_spot_balance...")
            spot_balance = wrapper.get_spot_balance()
            print(f"Spot balance: {spot_balance}")

            # Test get_fut_position
            print("\nTesting get_fut_position...")
            fut_position = wrapper.get_fut_position()
            print(f"Futures positions: {fut_position}")

            # Test get_account_config
            print("\nTesting get_account_config...")
            account_config = wrapper.get_account_config()
            print(f"Account config: {account_config.keys() if isinstance(account_config, dict) else 'Error'}")
        else:
            print("\nSkipping authenticated endpoint tests - no API keys provided")

        print("\nBinancePmTestWrapper test completed")

    # Run the test
    test_binance_pm_wrapper()
