from pyxt.spot import Spot
from pyxt.perp import Perp
from pathlib import Path
import sys
from api_tester.rest.baseclass import RestBaseClass
import yaml
import os
import time

class XtApi(RestBaseClass):
    def __init__(self, spot_host="https://sapi.xt.com",um_host="https://fapi.xt.com",cm_host="https://dapi.xt.com",user_api_host="https://api.xt.com",api_key="", api_secret="",default_symbol="BTC_USDT",default_quantity=0.001,**kwargs):
        """
        Initialize the XT API client

        Args:
            host (str): API host URL
            key_type (str): Type of API key to use from the keys.yaml file
        """

        self.api_key = api_key
        self.api_secret = api_secret
        self.spot_host = spot_host
        self.um_host = um_host
        self.cm_host = cm_host
        self.user_api_host = user_api_host

        # Initialize the spot and perp clients
        self.spot = Spot(self.spot_host,user_id=None, access_key=api_key,secret_key= api_secret)
        self.um_perp = Perp(self.um_host,user_id=None, access_key=api_key,secret_key= api_secret)
        self.cm_perp = Perp(self.cm_host,user_id=None, access_key=api_key,secret_key= api_secret)
        self.user_api = Spot(self.user_api_host,user_id=None, access_key=api_key,secret_key= api_secret)
        self._p_user_api = Perp(self.user_api_host,user_id=None, access_key=self.api_key,secret_key=self.api_secret)

        # Set default trading parameters
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity
        self.default_price_multiplier = kwargs.get('default_price_multiplier',0.9)
        print("XT API client initialized")

    def get_spot_config(self, symbol=None):
        '''
        Test spot read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None (uses default symbol).

        Returns:
            dict: Market config containing information about the trading pair
        '''
        if symbol is None:
            symbol = self.default_symbol

        try:
            # Call the spot API to get market config for the symbol
            response = self.spot.get_symbol_config(symbol)
            return response
        except Exception as e:
            print(f"Error getting spot market config: {e}")
            return None

    def get_spot_balance(self):
        '''
        Test spot read - get account balances

        Returns:
            dict: Account balances
        '''
        try:
            # Call the spot API to get balances
            response = self.spot.balances()
            return response
        except Exception as e:
            print(f"Error getting spot balance: {e}")
            return {"error": str(e)}

    def _get_position(self,api:Perp, symbol=None):
        """
        get_position
        :return:
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/user" + '/v1/position/list'
        url = api.host + path
        params = None
        if symbol:
            params = {
                "symbol": symbol,
            }

        header = api._create_sign(self.api_key, self.api_secret, path=path, bodymod=bodymod,
                                   params=params)
        header["Content-Type"] = "application/x-www-form-urlencoded"
        code, success, error = api._fetch(method="GET", url=url, headers=header, params=params, timeout=api.timeout)
        return code, success, error

    def get_fut_position(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        try:
            # Call the perp API to get positions for the default symbol
            _, success, error = self._get_position(self.um_perp)
            _, cm_success, error = self._get_position(self.cm_perp,None)
            if error:
                return {"error": error}
            return {
                "um": success,
                "cm": cm_success
            }
        except Exception as e:
            print(f"Error getting futures position: {e}")
            return {"error": str(e)}

    def get_spot_price(self, symbol=None):
        '''
        Test spot read - get spot price

        Returns:
            dict: Spot price
        '''
        if symbol is None:
            symbol = self.default_symbol
        try:
            # Call the spot API to get the ticker for the default symbol
            response = self.spot.get_tickers(symbol)
            if symbol:
                response = [float(ticker['p']) for ticker in response if ticker['s'] == symbol][0]
            return response
        except Exception as e:
            print(f"Error getting spot price: {e}")
            return

    def convert_float_to_int(self,number:float|str)->int|float:
        if isinstance(number, str):
            number = float(number)
        if number == int(number):
            return int(number)
        else:
            return number

    def order(self,symbol,side, order_type, biz_type='SPOT', time_in_force='GTC', client_order_id=None, price=None,
              quantity=None, quote_qty=None):
        # convert to int if float is integer value
        if price:
            price = self.convert_float_to_int(price)
        if quantity:
            quantity = self.convert_float_to_int(quantity)
        if quote_qty:
            quote_qty = self.convert_float_to_int(quote_qty)
        return self.spot.order(symbol, side, order_type, biz_type, time_in_force, client_order_id, price, quantity, quote_qty)

    def buy_spot(self,symbol,price,quantity,order_type='LIMIT',time_in_force='GTC'):
        quote_qty = None
        if order_type == 'MARKET':
            quote_qty = str(round(quantity * price,2))
            quantity = None
            price = None
        if quantity:
            quantity = str(quantity)
        if price:
            price = str(price)

        return self.order(symbol=symbol,side='BUY',order_type=order_type,time_in_force=time_in_force,price=price,quantity=quantity,quote_qty=quote_qty)

    def sell_spot(self,symbol,price,quantity,order_type='LIMIT',time_in_force='GTC'):
        quote_qty = None
        if order_type == 'MARKET':
            price = None
            assert time_in_force in ['IOC','FOK'], "Time in force must be IOC or FOK for market orders"
        if quantity:
            quantity = str(quantity)
        if price:
            price = str(price)

        return self.order(symbol=symbol,side='SELL',order_type=order_type,time_in_force=time_in_force,price=price,quantity=quantity,quote_qty=quote_qty)

    def test_buy_spot(self):
        '''
        Test spot write/trade - place a buy order

        Returns:
            dict: Order response
        '''
        try:
            current_price = self.get_spot_price(self.default_symbol)  # Use our own ticker method
            # Get current ticker to determine price
            if not current_price:
                return {"error": "Failed to get ticker data"}

            # get_ config
            config = self.get_spot_config(self.default_symbol)
            if config is None:
                return {"error": "Failed to get market config"}
            config = config[0]
            price_precision = int(config["pricePrecision"])
            print(f"price_precision: {price_precision}")
            quantity_precision = int(config["quantityPrecision"])
            print(f"price_precision: {price_precision}, quantity_precision: {quantity_precision}")

            # Calculate a price 10% below current price to avoid execution
            buy_price = round(current_price * self.default_price_multiplier, price_precision)

            # Since the Spot class doesn't have a create_order method, we'll create a mock response
            # Place a limit buy order
            result = self.spot.order(
                symbol=self.default_symbol,
                side="BUY",
                type="LIMIT",
                price=str(buy_price),
                quantity=str(round(self.default_quantity, quantity_precision)),
                time_in_force="GTC",
                biz_type="SPOT"
            )

            # For read-only keys, this should fail with a permission error
            if "read_only" in self.api_key:
                return {"error": "Permission denied: This API key does not have trading permissions"}
            return result
        except Exception as e:
            print(f"Error buying spot: {e}")
            return {"error": str(e)}

    def test_sell_spot(self):
        '''
        Test spot write/trade - place a sell order

        Returns:
            dict: Order response
        '''
        try:
            current_price = self.get_spot_price(self.default_symbol)  # Use our own ticker method
            # Get current ticker to determine price
            if not current_price:
                return {"error": "Failed to get ticker data"}

            # get_ config
            config = self.get_spot_config(self.default_symbol)
            if config is None:
                return {"error": "Failed to get market config"}
            config = config[0]
            price_precision = int(config["pricePrecision"])
            print(f"price_precision: {price_precision}")
            quantity_precision = int(config["quantityPrecision"])
            print(f"price_precision: {price_precision}, quantity_precision: {quantity_precision}")

            sell_price = round(current_price * (1 + (1 - self.default_price_multiplier)), price_precision)

            # Place a limit sell order
            response = self.spot.order(
                symbol=self.default_symbol,
                side="SELL",
                type="LIMIT",
                price=str(sell_price),
                quantity=str(round(self.default_quantity, quantity_precision)),
                time_in_force="GTC",
                biz_type="SPOT"
            )
            return response
        except Exception as e:
            print(f"Error selling spot: {e}")
            return {"error": str(e)}

    def get_perp_market_config(self, symbol=None):
        '''
        Test futures/swap read - get market config

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None (uses default symbol).

        Returns:
            dict: Market config
        '''
        if symbol is None:
            symbol = self.default_symbol

        try:
            # Call the perp API to get market config for the symbol
            _, success, error = self.um_perp.get_market_config(symbol)
            _, cm_success, error = self.cm_perp.get_market_config(symbol)
            if error:
                print(f"Error getting perp market config: {error}")
                return None
            return {
                "um": success,
                "cm": cm_success
            }
        except Exception as e:
            print(f"Error getting perp market config: {e}")
            return None

    def cancel_spot_open_orders(self,symbol=None):
        '''
        Test spot write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''

        try:
            # Cancel all open orders
            response = self.spot.cancel_open_orders(symbol)
            return response
        except Exception as e:
            print(f"Error canceling open spot orders: {e}")
            return {"error": str(e)}

    def cancel_fut_open_orders(self,symbol:str=None):
        '''
        Test futures/swap write/trade - cancel all open orders

        Returns:
            dict: Order response
        '''
        res = {}
        try:
            if symbol:
                # Cancel all open orders
                if symbol.endswith("usdt"):
                    _, response, error = self.um_perp.cancel_all_order(symbol)
                    res["um"] = response
                elif symbol.endswith("usd"):
                    _, cm_response, error = self.cm_perp.cancel_all_order(symbol)
                    res["cm"] = cm_response
            else:
                _, um_response, error = self.um_perp.cancel_all_order(symbol)
                _, cm_response, error = self.cm_perp.cancel_all_order(symbol)
                res["um"] = um_response
                res["cm"] = cm_response


            return res
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
            # Call the perp API to get account balance
            _, response, error = self.um_perp.get_account_capital()
            _, cm_reponse, error = self.cm_perp.get_account_capital()
            if error:
                return {"error": error}
            return {
                "um": response,
                "cm": cm_reponse
            }
        except Exception as e:
            print(f"Error getting futures account balance: {e}")
            return {"error": str(e)}

    def get_um_price(self,symbol=None):
        '''
        Test futures/swap read - get futures mark price

        Returns:
            dict: Futures mark price
        '''
        if symbol is None:
            symbol = self.default_symbol
        try:
            # Call the perp API to get mark price
            _, response, error = self.um_perp.get_mark_price(symbol)
            if error:
                return {"error": error}
            return float(response.get('result',{}).get('p',0))

        except Exception as e:
            print(f"Error getting futures mark price: {e}")
            return 0

    def _get_fut_params(self, symbol, price, qty, order_type, time_in_force):
        if symbol is None:
            symbol = self.default_symbol

        if order_type == "MARKET":
            price = None
            qty = qty
            if not time_in_force:
                time_in_force = "FOK"
        elif order_type == "LIMIT":
            if not price:
                return {"error": "Price is required for LIMIT order"}
            qty = qty
            if not time_in_force:
                time_in_force = "GTC"

        # if float has only 0 decimal places, convert to int
        if isinstance(price, float) and price.is_integer():
            price = int(price)
        if isinstance(qty, float) and qty.is_integer():
            qty = int(qty)

        return symbol, price, qty, time_in_force

    def open_long_fut(self,symbol,price=None,qty=None,order_type="LIMIT",time_in_force=""):
        '''
        Test futures/swap write/trade - open a long position
        symbol: str
        price: float
        qty: float
        order_type: str
        time_in_force: str


        Returns:
            dict: Order response
        '''
        symbol, price, qty, time_in_force = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        if symbol.endswith("usdt"):
            api = self.um_perp
        elif symbol.endswith("usd"):
            api = self.cm_perp
        else:
            api = self.um_perp
        try:
            # Place a limit buy order for a long position
            _, response, error = api.send_order(
                symbol=symbol,
                amount=qty,
                order_side="BUY",
                order_type=order_type,
                position_side="LONG",
                price=price,
                time_in_force=time_in_force
            )
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error opening long futures position: {e}")
            return {"error": str(e)}

    def close_long_fut(self,symbol,price=None,qty=None,order_type="LIMIT",time_in_force=""):
        '''
        Test futures/swap write/trade - close a long position
        symbol: str
        price: float
        qty: float
        order_type: str
        time_in_force: str

        Returns:
            dict: Order response
        '''
        symbol, price, qty, time_in_force = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        if symbol.endswith("usdt"):
            api = self.um_perp
        elif symbol.endswith("usd"):
            api = self.cm_perp
        else:
            api = self.um_perp
        try:
            # Place a limit sell order to close a long position
            _, response, error = api.send_order(
                symbol=symbol,
                amount=qty,
                order_side="SELL",
                order_type=order_type,
                position_side="LONG",
                price=price,
                time_in_force=time_in_force
            )
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error closing long futures position: {e}")
            return {"error": str(e)}

    def open_short_fut(self,symbol,price=None,qty=None,order_type="LIMIT",time_in_force=""):
        '''
        Test futures/swap write/trade - open a short position
        symbol: str
        price: float
        qty: float
        order_type: str
        time_in_force: str

        Returns:
            dict: Order response
        '''
        symbol, price, qty, time_in_force = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        if symbol.endswith("usdt"):
            api = self.um_perp
        elif symbol.endswith("usd"):
            api = self.cm_perp
        else:
            api = self.um_perp
        try:
            # Place a limit sell order for a short position
            _, response, error = api.send_order(
                symbol=symbol,
                amount=qty,
                order_side="SELL",
                order_type=order_type,
                position_side="SHORT",
                price=price,
                time_in_force=time_in_force
            )
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error opening short futures position: {e}")
            return {"error": str(e)}

    def close_short_fut(self,symbol,price=None,qty=None,order_type="LIMIT",time_in_force=""):
        '''
        Test futures/swap write/trade - close a short position
        symbol: str
        price: float
        qty: float
        order_type: str
        time_in_force: str

        Returns:
            dict: Order response
        '''
        symbol, price, qty, time_in_force = self._get_fut_params(symbol, price, qty, order_type, time_in_force)
        if symbol.endswith("usdt"):
            api = self.um_perp
        elif symbol.endswith("usd"):
            api = self.cm_perp
        else:
            api = self.um_perp
        try:
            # Place a limit buy order to close a short position
            _, response, error = api.send_order(
                symbol=symbol,
                amount=qty,
                order_side="BUY",
                order_type=order_type,
                position_side="SHORT",
                price=price,
                time_in_force=time_in_force
            )
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error closing short futures position: {e}")
            return {"error": str(e)}

    def test_open_long_fut(self,price_prec,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - open a long position

        Returns:
            dict: Order response
        '''
        try:
            # Get current mark price
            _, mark_price_response, error = self.um_perp.get_mark_price(self.default_symbol)
            if error or not mark_price_response or "result" not in mark_price_response:
                return {"error": "Failed to get mark price data"}

            # Calculate a price 10% below current price to avoid execution
            current_price = float(mark_price_response.get('result',{}).get('p',0))
            buy_price = round(current_price * self.default_price_multiplier, price_prec)

            if qty_prec == 0:
                _qty = int(self.default_quantity / cont_size)
            else:
                _qty = round(self.default_quantity / cont_size, qty_prec)

            # Place a limit buy order for a long position
            _, response, error = self.um_perp.send_order(
                symbol=self.default_symbol,
                amount=_qty,
                order_side="BUY",
                order_type="LIMIT",
                position_side="LONG",
                price=buy_price,
                time_in_force="GTC"
            )
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error opening long futures position: {e}")
            return {"error": str(e)}

    def test_close_long_fut(self,price_prec,qty_prec,cont_size):
        '''
        Test futures/swap write/trade - close a long position

        Returns:
            dict: Order response
        '''
        try:
            # Get current mark price
            _, mark_price_response, error = self.um_perp.get_mark_price(self.default_symbol)

            if error or not mark_price_response or "result" not in mark_price_response:
                return {"error": "Failed to get mark price data"}

            # Calculate a price 10% above current price to avoid execution
            current_price = float(mark_price_response["result"]["p"])
            sell_price = round(current_price * (1 + (1 - self.default_price_multiplier)), price_prec)

            if qty_prec == 0:
                _qty = int(self.default_quantity / cont_size)
            else:
                _qty = round(self.default_quantity / cont_size, qty_prec)

            # Place a limit sell order to close a long position
            _, response, error = self.um_perp.send_order(
                symbol=self.default_symbol,
                amount=_qty,
                order_side="SELL",
                order_type="LIMIT",
                position_side="LONG",
                price=sell_price,
                time_in_force="GTC"
            )

            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error closing long futures position: {e}")
            return {"error": str(e)}

    def get_spot_order(self,order_id=None,client_order_id=None):
        '''
        query a single order
        either order_id or client_order_id must be provided

        Returns:
            dict: Order response
        '''
        try:
            # Call the spot API to get the order
            response = self.spot.get_order(order_id,client_order_id)
            return response
        except Exception as e:
            print(f"Error getting spot order: {e}")
            return {"error": str(e)}

    def get_spot_open_orders(self):
        '''
        Test spot read - get open orders

        Returns:
            dict: Open orders
        '''
        try:
            # Call the spot API to get open orders for the default symbol
            response = self.spot.get_open_orders( biz_type="SPOT")
            return response
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
            # Call the perp API to get open orders for the default symbol
            _, response, error = self.um_perp.get_account_order('NEW')
            if error:
                return {"error": error}
            return response
        except Exception as e:
            print(f"Error getting open futures orders: {e}")
            return {"error": str(e)}

    def get_account_config(self):
        '''
        Test futures/swap read - get futures positions

        Returns:
            dict: Futures positions
        '''
        bodymod = "application/json"
        path = "/future/user/v1/account/info"
        url = self.um_perp.host + path
        params = {}
        header = self.um_perp._create_sign(self.api_key, self.api_secret, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self.um_perp._fetch(method="GET", url=url, headers=header, data=params, timeout=self.um_perp.timeout)
        return code, success, error

    def get_fut_user_step_rate(self):
        """
        Get futures user step rate

        Returns:
            tuple: (code, success, error) - API response
        """
        bodymod = "application/json"
        path = "/future/user" + '/v1/user/step-rate'
        url = self.um_perp.host + path
        params = {}
        header = self.um_perp._create_sign(self.api_key, self.api_secret, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self.um_perp._fetch(method="GET", url=url, headers=header, data=params, timeout=self.um_perp.timeout)
        return code, success, error

    def get_um_comms_rate(self, symbol=None):
        """
        Get futures commission rates

        Args:
            symbol (str, optional): Symbol to get commission rates for. Defaults to None.

        Returns:
            dict: Commission rates
        """
        if symbol is None:
            symbol = self.default_symbol
        _, data, error = self.get_fut_user_step_rate()
        if not data:
            return {}
        if error:
            return {"error": error}

        data = data.get("result",[])
        return {
            "symbol": symbol,
            "makerCommissionRate": data["makerFee"],
            "takerCommissionRate": data["takerFee"],
        }

    def get_spot_comms_rate(self,symbol=None):
        """
        :return: account capital
        """
        if symbol is None:
            symbol = self.default_symbol
        data = self.get_spot_config(symbol)
        if not data:
            return {}
        _out = {
            "symbol": symbol,
            "makerCommissionRate": data[0]["makerFeeRate"],
            "takerCommissionRate": data[0]["takerFeeRate"],
        }
        return _out

    def transfer(self,from_account,to_account,currency,amount,symbol:str,biz_id:str=None):
        """
        BizType
        Status	Description
        SPOT	现货
        LEVER	杠杠
        FINANCE	理财
        FUTURES_U	合约u本位
        FUTURES_C	合约币本位

        @param from_account: BizType
        @param to_account: BizType
        @param currency:币种名称必须全部小写（usdt，btc）
        @param amount:
        @return:
        """
        params = {
            "bizId": biz_id if biz_id else "1",
            "from": from_account,
            "to": to_account,
            "currency": currency,
            "amount": amount,
            "symbol": symbol,
        }
        res = self.spot.req_post("/v4/balance/transfer", params, auth=True)
        return res

    def get_spot_trades(self, symbol=None, biz_type="SPOT",limit=100, start_time=None, end_time=None):
        """
        Get spot trades for a symbol

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None (uses default symbol).
            biz_type (str, optional): Business type. Defaults to "SPOT".

        Returns:
            dict: Trades data
        """
        if not symbol:
            symbol = self.default_symbol
        params = {
            "symbol": symbol,
            "limit": limit,
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        # Note: biz_type is currently not used in the implementation but kept for API consistency
        return self.spot.get_trade(**params)
    
    def get_spot_hist_orders(self, symbol=None, biz_type=None, side=None, type=None, order_id=None, from_id=None,
                           direction=None, limit=None, start_time=None, end_time=None, hidden_canceled=None):
        return self.spot.get_history_orders(
            symbol, biz_type, side, type, order_id, from_id, direction, limit, start_time, end_time, hidden_canceled)

    def get_um_hist_orders(self, symbol=None, direction=None, oid=None, limit=5, start_time=None, end_time=None):
        return self.um_perp.get_history_order(symbol, direction, oid, limit, start_time, end_time)

    def get_um_trades(self,symbol=None, direction=None, oid=None, limit=5, start_time=None, end_time=None):
        """
        :return: get_history_order
        Error
        """
        bodymod = "application/x-www-form-urlencoded"
        path = "/future/trade" + '/v1/order/trade-list'
        url = self.um_perp.host + path
        params = {}
        if symbol:
            params["symbol"] = symbol
        if direction:
            params["direction"] = direction
        if oid:
            params["id"] = oid
        if limit:
            params["limit"] = limit
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        header = self.um_perp._create_sign(self.api_key, self.api_secret, path=path, bodymod=bodymod,
                                   params=params)
        code, success, error = self.um_perp._fetch(method="GET", url=url, headers=header, params=params, timeout=self.um_perp.timeout)
        return code, success, error

    def get_um_order(self,order_id=None):
        return self.um_perp.get_order_id(order_id)

    def get_cm_order(self,order_id=None):
        return self.cm_perp.get_order_id(order_id)
    
    def get_acct_list(self,account_id=None,account_name=None,level=None):
        params = {}
        if account_id:
            params["accountId"] = account_id
        if account_name:
            params["accountName"] = account_name
        if level:
            params["level"] = level
        try:
            res = self.user_api.req_get("/v4/user/account",params,auth=True)
        
        except Exception as e:
            print(f"Error getting account list: {e}")

        return res


if __name__ == "__main__":
    import json
    # Load API keys from the keys.yaml file
    keys_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.keys.yaml')
    with open(keys_path, 'r') as f:
        keys = yaml.safe_load(f)

    def print_response(title, response):
        """Print a formatted response."""
        print(f"\n=== {title} ===")
        print(json.dumps(response, indent=2))
        print("=" * (len(title) + 8))

    # read_write api
    acct_info_1 = keys['xt']['read_write_2']
    # Initialize the XT API client
    xt_api = XtApi(spot_host=acct_info_1['spot_host'],um_host=acct_info_1['um_host'],cm_host=acct_info_1['cm_host'],api_key=acct_info_1['api_key'],api_secret=acct_info_1['api_secret'])

    breakpoint()
    data = xt_api.get_um_price("eth_usdt")
    print(data)
    breakpoint()
    # Get fees
    spot_fees = xt_api.get_spot_comms_rate()
    um_fees = xt_api.get_um_comms_rate()
    # Test spot balance
    spot_balance = xt_api.get_spot_balance()
    print_response("Spot Balance", spot_balance)

    # Test futures position
    fut_position = xt_api.get_fut_position()
    print_response("Futures Position", fut_position)

    # Test spot buy
    buy_spot = xt_api.test_buy_spot()
    print_response("Buy Spot", buy_spot)

    # Get market config to get precision values for futures trading
    config = xt_api.get_perp_market_config(xt_api.default_symbol)
    if config:
        try:
            price_precision = int(config.get("result", {}).get("priceScale", 2))
            qty_precision = int(config.get("result", {}).get("amountScale", 4))
            contract_size = float(config.get("result", {}).get("contractSize", 1))

            # Test open long futures
            open_long = xt_api.test_open_long_fut(price_precision, qty_precision, contract_size)
            print_response("Open Long Futures", open_long)

            # Test close long futures
            close_long = xt_api.test_close_long_fut(price_precision, qty_precision, contract_size)
            print_response("Close Long Futures", close_long)
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error extracting precision values: {str(e)}")
    else:
        print("Failed to get market config for futures trading")


