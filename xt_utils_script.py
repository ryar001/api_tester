import sys
import yaml
import json
from pathlib import Path
import pandas as pd
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))
from rest.xt import XtApi

"""
XT Exchange Utility Script

This script provides a command-line interface for interacting with the XT Exchange API.
It allows users to perform various operations on both spot and futures markets,
including checking balances, placing orders, and transferring assets between accounts.

Usage:
    python xt_utils_script.py

The script will load API keys from the .keys.yaml file in the same directory.
"""

class XtUtils:
    def __init__(self, api_key, api_secret, spot_host="https://sapi.xt.com", um_host="https://fapi.xt.com",cm_host="https://dapi.xt.com",user_api_host="https://api.xt.com",default_symbol="btc_usdt", default_quantity=0.001):
        """
        Initialize the XT Utils client

        Args:
            api_key (str): XT API key
            api_secret (str): XT API secret
            spot_host (str, optional): Spot API host URL. Defaults to "https://sapi.xt.com".
            perp_host (str, optional): Perpetual futures API host URL. Defaults to "https://fapi.xt.com".
            default_symbol (str, optional): Default trading symbol. Defaults to "BTC_USDT".
            default_quantity (float, optional): Default trading quantity. Defaults to 0.001.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.spot_host = spot_host
        self.um_host = um_host
        self.cm_host = cm_host
        self.user_api_host = user_api_host
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity

        # Initialize the XT API client
        self.client = XtApi(
            spot_host=self.spot_host,
            um_host=self.um_host,
            cm_host=self.cm_host,
            user_api_host=self.user_api_host,
            api_key=self.api_key,
            api_secret=self.api_secret,
            default_symbol=self.default_symbol,
            default_quantity=self.default_quantity
        )

    def get_spot_balance(self):
        """
        Get spot account balance

        Returns:
            dict: Spot account balance
        """
        return self.client.get_spot_balance()

    def get_spot_config(self, symbol=None):
        """
        Get spot market configuration for a symbol

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None (uses default symbol).

        Returns:
            dict: Market config containing information about the trading pair
        """
        return self.client.get_spot_config(symbol=symbol)

    def get_perp_market_config(self, symbol=None):
        """
        Get perpetual futures market configuration for a symbol

        Args:
            symbol (str, optional): Symbol to get config for. Defaults to None (uses default symbol).

        Returns:
            dict: Market config containing information about the futures trading pair
        """
        return self.client.get_perp_market_config(symbol=symbol)

    def get_spot_price(self, symbol=None):
        """
        Get spot price for a symbol

        Args:
            symbol (str, optional): Symbol to get price for. Defaults to None (uses default symbol).

        Returns:
            float or dict: Spot price or ticker data
        """
        return self.client.get_spot_price(symbol=symbol)

    def get_fut_balance(self):
        """
        Get futures account balance

        Returns:
            dict: Futures account balance
        """
        return self.client.get_fut_balance()

    def get_fut_position(self):
        """
        Get futures positions

        Returns:
            dict: Futures positions
        """
        return self.client.get_fut_position()

    def get_spot_open_orders(self):
        """
        Get open spot orders

        Returns:
            dict: Open spot orders
        """
        return self.client.get_spot_open_orders()
    
    def get_spot_trades(self, symbol=None, biz_type="SPOT", limit=100):
        """
        Get spot account trade history

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None (uses default symbol).
            biz_type (str, optional): BizType to get trades for. Defaults to "SPOT".
            limit (int, optional): Maximum number of trades to return. Defaults to 100.

        Returns:
            dict: Spot trade history
        """
        return self.client.get_spot_trades(symbol, biz_type, limit)


    def get_fut_open_orders(self):
        """
        Get open futures orders

        Returns:
            dict: Open futures orders
        """
        return self.client.get_fut_open_orders()

    def get_spot_fee(self):
        """
        Get spot trading fees

        Returns:
            dict: Spot trading fees
        """
        return self.client.get_spot_comms_rate()

    def get_fut_fee(self):
        """
        Get futures trading fees

        Returns:
            dict: Futures trading fees
        """
        return self.client.get_um_comms_rate()

    def get_account_config(self):
        """
        Get account configuration

        Returns:
            dict: Account configuration
        """
        return self.client.get_account_config()

    def buy_spot(self, symbol=None, price=None, quantity=None, order_type='LIMIT', time_in_force='GTC'):
        """
        Place a spot buy order

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        """
        return self.client.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                   order_type=order_type, time_in_force=time_in_force)

    def sell_spot(self, symbol=None, price=None, quantity=None, order_type='LIMIT', time_in_force='GTC'):
        """
        Place a spot sell order

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        """
        return self.client.sell_spot(symbol=symbol, price=price, quantity=quantity,
                                    order_type=order_type, time_in_force=time_in_force)

    def _get_perp_precision_values(self):
        """
        Helper method to get precision values for futures trading

        Returns:
            tuple: (price_precision, qty_precision, contract_size) or None if error
        """
        config = self.client.get_perp_market_config(self.default_symbol)
        if not config or isinstance(config, tuple):
            print(f"Error: Failed to get market config")
            return None

        try:
            price_precision = int(config.get("result", {}).get("priceScale", 2))
            qty_precision = int(config.get("result", {}).get("amountScale", 4))
            contract_size = float(config.get("result", {}).get("contractSize", 1))
            return price_precision, qty_precision, contract_size
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error extracting precision values: {str(e)}")
            return None

    def open_long_fut(self, symbol=None, price=None, quantity=None, order_type="LIMIT", time_in_force=""):
        """
        Open a long futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to '' (uses default based on order type).

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if order_type == "MARKET":
            # For market orders, set price to None and use FOK time_in_force
            price = None
            if not time_in_force:
                time_in_force = "FOK"
        else:
            # For limit orders, price is required
            if price is None:
                return {"error": "Price is required for LIMIT orders"}
            if not time_in_force:
                time_in_force = "GTC"

        return self.client.open_long_fut(
            symbol=symbol,
            price=price,
            qty=quantity,
            order_type=order_type,
            time_in_force=time_in_force
        )

    def close_long_fut(self, symbol=None, price=None, quantity=None, order_type="LIMIT", time_in_force=""):
        """
        Close a long futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to '' (uses default based on order type).

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if order_type == "MARKET":
            # For market orders, set price to None and use FOK time_in_force
            price = None
            if not time_in_force:
                time_in_force = "FOK"
        else:
            # For limit orders, price is required
            if price is None:
                return {"error": "Price is required for LIMIT orders"}
            if not time_in_force:
                time_in_force = "GTC"

        return self.client.close_long_fut(
            symbol=symbol,
            price=price,
            qty=quantity,
            order_type=order_type,
            time_in_force=time_in_force
        )

    def open_short_fut(self, symbol=None, price=None, quantity=None, order_type="LIMIT", time_in_force=""):
        """
        Open a short futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to '' (uses default based on order type).

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if order_type == "MARKET":
            # For market orders, set price to None and use FOK time_in_force
            price = None
            if not time_in_force:
                time_in_force = "FOK"
        else:
            # For limit orders, price is required
            if price is None:
                return {"error": "Price is required for LIMIT orders"}
            if not time_in_force:
                time_in_force = "GTC"

        return self.client.open_short_fut(
            symbol=symbol,
            price=price,
            qty=quantity,
            order_type=order_type,
            time_in_force=time_in_force
        )

    def close_short_fut(self, symbol=None, price=None, quantity=None, order_type="LIMIT", time_in_force=""):
        """
        Close a short futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for LIMIT orders, ignored for MARKET orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to '' (uses default based on order type).

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if order_type == "MARKET":
            # For market orders, set price to None and use FOK time_in_force
            price = None
            if not time_in_force:
                time_in_force = "FOK"
        else:
            # For limit orders, price is required
            if price is None:
                return {"error": "Price is required for LIMIT orders"}
            if not time_in_force:
                time_in_force = "GTC"

        return self.client.close_short_fut(
            symbol=symbol,
            price=price,
            qty=quantity,
            order_type=order_type,
            time_in_force=time_in_force
        )

    def cancel_spot_orders(self,symbol=None):
        """
        Cancel all open spot orders

        Returns:
            dict: Cancellation response
        """
        return self.client.cancel_spot_open_orders(symbol=symbol)

    def cancel_fut_orders(self,symbol=None):
        """
        Cancel all open futures orders

        Returns:
            dict: Cancellation response
        """
        return self.client.cancel_fut_open_orders(symbol=symbol)

    def transfer(self, from_account, to_account, currency, amount, symbol):
        """
        Transfer assets between accounts

        BizType options:
        - SPOT: Spot
        - LEVER: Margin
        - FINANCE: Finance
        - FUTURES_U: USDT-M Futures
        - FUTURES_C: Coin-M Futures

        Args:
            from_account (str): Source account type (BizType)
            to_account (str): Destination account type (BizType)
            currency (str): Currency name (must be lowercase, e.g., usdt, btc)
            symbol (str): Symbol name (must be uppercase, e.g., BTCUSDT)
            amount (float): Amount to transfer

        Returns:
            dict: Transfer response
        """
        print(f"Transferring {amount} {currency} from {from_account} to {to_account}")
        return self.client.transfer(from_account, to_account, currency, amount, symbol)

    def handle_get_spot_trades(self):
        """Handle get spot trades request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        biz_type = input("Enter BizType (leave empty for SPOT): ") or "SPOT"
        output_csv = input("Output to CSV? (yes/no, default: no): ").lower() == 'yes'
        if not symbol:
            symbol = None
        self.print_response(f"Spot Trades for {symbol or self.acct.default_symbol}",
                           self.acct.get_spot_trades(symbol, biz_type, to_csv=output_csv))

    def get_um_trades(self, symbol=None, direction=None, oid=None, limit=5, start_time=None, end_time=None):
        """
        Get USDT-M futures trade history

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None (uses default symbol).
            direction (str, optional): Trade direction. Defaults to None.
            oid (int, optional): Order ID to filter by. Defaults to None.
            limit (int, optional): Maximum number of trades to return. Defaults to 5.
            start_time (int, optional): Start time in milliseconds. Defaults to None.
            end_time (int, optional): End time in milliseconds. Defaults to None.

        Returns:
            dict: Futures trade history
        """
        return self.client.get_um_trades(symbol, direction, oid, limit, start_time, end_time)

    def get_spot_hist_orders(self, symbol=None, limit=5, start_time=None, end_time=None):
        """
        Get spot historical orders

        Args:
            symbol (str, optional): Symbol to get orders for. Defaults to None (uses default symbol).
            limit (int, optional): Maximum number of orders to return. Defaults to 5.
            start_time (int, optional): Start time in milliseconds. Defaults to None.
            end_time (int, optional): End time in milliseconds. Defaults to None.

        Returns:
            dict: Spot historical orders
        """
        return self.client.get_spot_hist_orders(
            symbol=symbol, 
            limit=limit, 
            start_time=start_time, 
            end_time=end_time
        )

    def get_um_hist_orders(self, symbol=None, limit=5, start_time=None, end_time=None):
        """
        Get USDT-M futures historical orders

        Args:
            symbol (str, optional): Symbol to get orders for. Defaults to None (uses default symbol).
            limit (int, optional): Maximum number of orders to return. Defaults to 5.
            start_time (int, optional): Start time in milliseconds. Defaults to None.
            end_time (int, optional): End time in milliseconds. Defaults to None.

        Returns:
            dict: Futures historical orders
        """
        return self.client.get_um_hist_orders(
            symbol=symbol, 
            limit=limit, 
            start_time=start_time, 
            end_time=end_time
        )


    def get_spot_order(self, order_id):
        """
        Get spot order by ID

        Args:
            order_id (int): Order ID to get

        Returns:
            dict: Spot order
        """
        return self.client.get_spot_order(order_id)
    
    def get_um_order(self, order_id):
        """
        Get USDT-M futures order by ID

        Args:
            order_id (int): Order ID to get

        Returns:
            dict: Futures order
            """
        return self.client.get_um_order(order_id)
    
    def get_cm_order(self, order_id):
        """
        Get Coin-M Futures order
        """
        return self.client.get_cm_order(order_id)

    def get_spot_order(self, order_id):
        """
        Get spot order by ID

        Args:
            order_id (str): Order ID to get

        Returns:
            dict: Spot order
        """
        return self.client.get_spot_order(order_id=order_id)

    def get_um_order(self, order_id):
        """
        Get USDT-M futures order by ID

        Args:
            order_id (str): Order ID to get

        Returns:
            dict: Futures order
        """
        return self.client.get_um_order(order_id=order_id)

    def get_cm_order(self, order_id):
        """
        Get Coin-M Futures order by ID
        Args:
            order_id (str): Order ID to get
        Returns:
            dict: Futures order
        """
        return self.client.get_cm_order(order_id=order_id)

    def get_acct_list(self, account_id=None, account_name=None, level=None):
        """
        Get account list from user center.

        Args:
            account_id (str, optional): Account ID. Defaults to None.
            account_name (str, optional): Account Name. Defaults to None.
            level (int, optional): Level type. Defaults to None.

        Returns:
            dict: Account list response
        """
        return self.client.get_acct_list(account_id=account_id, account_name=account_name, level=level)


class XtUtilsApp:
    """
    XT Exchange Utility Application

    This class provides a command-line interface for interacting with the XT Exchange API.
    It allows users to perform various operations on both spot and futures markets,
    including checking balances, placing orders, and transferring assets between accounts.
    """

    def __init__(self):
        """Initialize the XT Utils Application"""
        self.acct_dict = {}
        self.selected_account = None
        self.acct:XtUtils = None

        # Define menu categories and their options with corresponding actions
        self.menu_categories = {
            "ACCOUNT INFO": [
                {"text": "Get spot balance", "action": "spot_balance"},
                {"text": "Get futures balance", "action": "fut_balance"},
                {"text": "Get futures position", "action": "fut_position"},
                {"text": "Get spot open orders", "action": "spot_open_orders"},
                {"text": "Get futures open orders", "action": "fut_open_orders"},
                {"text": "Get spot fee", "action": "spot_fee"},
                {"text": "Get futures fee", "action": "fut_fee"},
                {"text": "Get account config", "action": "account_config"},
                {"text": "Get spot trades", "action": "get_spot_trades"},
                {"text": "Get futures trades", "action": "get_um_trades"},
                {"text": "Get spot historical orders", "action": "get_spot_hist_orders"},
                {"text": "Get futures historical orders", "action": "get_um_hist_orders"},
                {"text": "Get spot order by ID", "action": "get_spot_order"},
                {"text": "Get UM futures order by ID", "action": "get_um_order"},
                {"text": "Get CM futures order by ID", "action": "get_cm_order"},
                {"text": "Get account list (User Center)", "action": "get_acct_list"}
            ],
            "MARKET DATA": [
                {"text": "Get spot price", "action": "spot_price"},
                {"text": "Get spot market config", "action": "spot_config"},
                {"text": "Get futures market config", "action": "perp_market_config"}
            ],
            "TRADING OPERATIONS": [
                {"text": "Buy spot (LIMIT/MARKET)", "action": "buy_spot"},
                {"text": "Sell spot (LIMIT/MARKET)", "action": "sell_spot"},
                {"text": "Open long futures position", "action": "open_long_fut"},
                {"text": "Close long futures position", "action": "close_long_fut"},
                {"text": "Open short futures position", "action": "open_short_fut"},
                {"text": "Close short futures position", "action": "close_short_fut"},
                {"text": "Cancel spot open orders", "action": "cancel_spot_orders"},
                {"text": "Cancel futures open orders", "action": "cancel_fut_orders"}
            ],
            "TRANSFERS": [
                {"text": "Transfer between accounts", "action": "transfer"}
            ],
            "OTHER": [
                {"text": "Exit to account selection", "action": "exit"},
                {"text": "Quit program", "action": "quit"}
            ]
        }

        # Map actions to handler methods
        self.action_handlers = {
            "exit": self.handle_exit,
            "quit": self.handle_quit,
            "spot_balance": self.handle_spot_balance,
            "fut_balance": self.handle_fut_balance,
            "fut_position": self.handle_fut_position,
            "spot_open_orders": self.handle_spot_open_orders,
            "fut_open_orders": self.handle_fut_open_orders,
            "spot_fee": self.handle_spot_fee,
            "fut_fee": self.handle_fut_fee,
            "account_config": self.handle_account_config,
            "get_spot_trades": self.handle_get_spot_trades,
            "get_um_trades": self.handle_get_um_trades,
            "get_spot_hist_orders": self.handle_get_spot_hist_orders,
            "get_um_hist_orders": self.handle_get_um_hist_orders,
            "get_spot_order": self.handle_get_spot_order,
            "get_um_order": self.handle_get_um_order,
            "get_cm_order": self.handle_get_cm_order,
            "get_acct_list": self.handle_get_acct_list,
            "spot_price": self.handle_spot_price,
            "spot_config": self.handle_spot_config,
            "perp_market_config": self.handle_perp_market_config,
            "buy_spot": self.handle_buy_spot,
            "sell_spot": self.handle_sell_spot,
            "open_long_fut": self.handle_open_long_fut,
            "close_long_fut": self.handle_close_long_fut,
            "open_short_fut": self.handle_open_short_fut,
            "close_short_fut": self.handle_close_short_fut,
            "cancel_spot_orders": self.handle_cancel_spot_orders,
            "cancel_fut_orders": self.handle_cancel_fut_orders,
            "transfer": self.handle_transfer
        }

    def print_response(self, title, response):
        """
        Print a formatted response.

        Args:
            title (str): Title of the response
            response (any): Response data to print
        """
        print(f"\n=== {title} ===")
        try:
            if isinstance(response, dict) or isinstance(response, list):
                print(json.dumps(response, indent=2))
            else:
                print(response)
        except:
            print(response)
        print("=" * (len(title) + 8))
        print()  # Add an extra newline for better readability

    def load_api_keys(self):
        """
        Load API keys from the .keys.yaml file

        Returns:
            bool: True if keys were loaded successfully, False otherwise
        """
        keys_path = Path(__file__).parent / '.keys.yaml'

        try:
            with open(keys_path, 'r') as f:
                keys = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: .keys.yaml file not found at {keys_path}")
            print("Please create a .keys.yaml file with your XT API keys.")
            print("Example format:")
            print("""
xt:
  read_only_1:
    api_key: \"your_api_key\"
    api_secret: \"your_api_secret\"
  read_write_2:
    api_key: \"another_api_key\"
    api_secret: \"another_api_secret\"
            """)
            return False
        except yaml.YAMLError:
            print("Error parsing .keys.yaml file. Please check the format.")
            return False

        # Get the XT keys
        if 'xt' not in keys:
            print("No 'xt' section found in .keys.yaml file.")
            return False

        for name, key_data in keys['xt'].items():
            try:
                api_key = key_data['api_key']
                api_secret = key_data['api_secret']
                spot_host = key_data.get('spot_host', 'https://sapi.xt.com')
                um_host = key_data.get('perp_host', 'https://fapi.xt.com')
                cm_host = key_data.get('cm_host', 'https://cmapi.xt.com')
                user_api_host = key_data.get('user_api_host', 'https://api.xt.com')


                # Initialize the XT Utils
                xt_utils = XtUtils(api_key, api_secret, spot_host=spot_host, um_host=um_host, cm_host=cm_host, user_api_host=user_api_host)

                # Add to accounts dictionary
                self.acct_dict[name] = xt_utils
                print(f"Loaded account: {name}")
            except KeyError:
                print(f"Warning: Missing API keys for account {name}")
                continue
            except Exception as e:
                print(f"Error initializing account {name}: {e}")
                continue

        if not self.acct_dict:
            print("No valid XT API keys found in .keys.yaml")
            return False

        return True

    def select_account(self):
        """
        Display available accounts and handle account selection

        Returns:
            bool: True if an account was selected, False to exit
        """
        print("\nAVAILABLE ACCOUNTS:")
        print("=" * 40)

        # Create a numbered list of accounts
        account_options = {}
        for i, account_name in enumerate(self.acct_dict.keys(), 1):
            print(f"{i}. {account_name}")
            account_options[str(i)] = account_name

        # Add exit option
        print("0. Exit")
        print("=" * 40)

        choice = input("Enter account number (or '0' to exit): ")

        if choice == '0':
            print("Exiting program.")
            return False

        if choice not in account_options:
            print("Invalid account number. Please try again.")
            return True  # Continue the loop

        # Get the selected account name and object
        self.selected_account = account_options[choice]
        self.acct = self.acct_dict[self.selected_account]
        
        # print acct name and  pubkey selected
        print(f"Selected account: {self.selected_account}")
        print(f"Public key: {self.acct.client.api_key}") 
        print(f"Spot host: {self.acct.client.spot_host}")
        print(f"Um host: {self.acct.client.um_host}")
        print(f"Cm host: {self.acct.client.cm_host}")
        print("=" * 40)

        return True

    def display_menu(self):
        """
        Display the menu options and handle user choices

        Returns:
            bool: True to continue, False to go back to account selection
        """
        print(f"\nSelected account: {self.selected_account}")
        print("=" * 40)
        print("MENU OPTIONS:")

        # Generate menu with automatic numbering
        option_number = 1
        option_map = {}

        for category, options in self.menu_categories.items():
            print(f"  {category}:")
            for option in options:
                if category == "OTHER":
                    if option["action"] == "exit":
                        print(f"    0. {option['text']}")
                        option_map["0"] = option["action"]
                    elif option["action"] == "quit":
                        print(f"    q. {option['text']}")
                        option_map["q"] = option["action"]
                else:
                    print(f"    {option_number}. {option['text']}")
                    option_map[str(option_number)] = option["action"]
                    option_number += 1
            print("")  # Add a newline between categories
        print("=" * 40)

        choice = input("Enter choice: ")

        try:
            if choice in option_map:
                # Get the action from the map
                action = option_map[choice]

                # Find the description for the selected option
                selected_description = ""
                for category, options in self.menu_categories.items():
                    for option in options:
                        if option["action"] == action:
                            selected_description = option["text"]
                            break
                    if selected_description:
                        break

                # Print a description of what was selected
                if selected_description:
                    print(f"\n{choice}) {selected_description}, selected")

                # Execute the handler function for the selected action
                if action in self.action_handlers:
                    result = self.action_handlers[action]()
                    if result == "break":
                        return False
                else:
                    print(f"Unknown action: {action}")
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            self.print_response("Error", f"An error occurred: {str(e)}")

        # Pause before showing menu again
        input("\nPress Enter to continue...")
        return True

    # Action handler methods
    def handle_exit(self):
        """Exit to account selection"""
        return "break"

    def handle_quit(self):
        """Quit the program"""
        print("Exiting program.")
        sys.exit(0)

    def handle_spot_balance(self):
        """Handle spot balance request"""
        self.print_response("Spot Balance", self.acct.get_spot_balance())

    def handle_fut_balance(self):
        """Handle futures balance request"""
        self.print_response("Futures Balance", self.acct.get_fut_balance())

    def handle_fut_position(self):
        """Handle futures position request"""
        self.print_response("Futures Position", self.acct.get_fut_position())

    def handle_spot_open_orders(self):
        """Handle spot open orders request"""
        res = self.acct.get_spot_open_orders()
        self.print_response("Spot Open Orders", f"{res}\nNo. of orders: {len(res)}")

    def handle_fut_open_orders(self):
        """Handle futures open orders request"""
        res = self.acct.get_fut_open_orders()
        self.print_response("Futures Open Orders", f"{res}\nNo. of orders: {len(res)}")

    def handle_spot_fee(self):
        """Handle spot fee request"""
        self.print_response("Spot Fee", self.acct.get_spot_fee())

    def handle_fut_fee(self):
        """Handle futures fee request"""
        self.print_response("Futures Fee", self.acct.get_fut_fee())

    def handle_account_config(self):
        """Handle account config request"""
        self.print_response("Account Config", self.acct.get_account_config())

    def handle_get_spot_trades(self):
        """Handle get spot trades request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        biz_type = input("Enter BizType (leave empty for SPOT): ") or "SPOT"
        if not symbol:
            symbol = None
        output_csv = input("Output to CSV? (yes/no, default: no): ").lower() in ['yes', 'y']
        limit = 20
        if output_csv:
            limit = input("Enter limit (leave empty for default 100): ")
            if limit:
                limit = int(limit)
            else:
                limit = 100
        data = self.acct.get_spot_trades(symbol, biz_type, limit)
        if not output_csv:
            print(f"Spot Trades for {symbol or self.acct.default_symbol}",
                               self.acct.get_spot_trades(symbol, biz_type))
            return
        
        print(f"Spot trades for {symbol or self.acct.default_symbol} written to spot_trades_{symbol or self.acct.default_symbol}.csv")
        data_df = pd.DataFrame(data["items"])
        data_df.to_csv(f"spot_trades_{symbol or self.acct.default_symbol}.csv", index=False)

    def handle_get_um_trades(self):
        """Handle get futures trades request"""
        symbol = input(f"Enter symbol (leave empty for ALL trades): ")
        if not symbol:
            symbol = None

        direction = input("Enter direction (leave empty for all): ")
        if not direction:
            direction = None

        oid = input("Enter order ID (leave empty for all): ")
        if oid:
            oid = int(oid)
        else:
            oid = None

        limit = input("Enter limit (leave empty for default 5): ")
        if limit:
            limit = int(limit)
        else:
            limit = 5

        start_time = input("Enter start time in milliseconds (leave empty for none): ")
        if start_time:
            start_time = int(start_time)
        else:
            start_time = None

        end_time = input("Enter end time in milliseconds (leave empty for none): ")
        if end_time:
            end_time = int(end_time)
        else:
            end_time = None

        self.print_response(f"Futures Trades for {symbol or self.acct.default_symbol}",
                           self.acct.get_um_trades(symbol, direction, oid, limit, start_time, end_time))

    def handle_spot_config(self):
        """Handle spot market config request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Spot Market Config for {symbol or self.acct.default_symbol}",
                           self.acct.get_spot_config(symbol))

    def handle_perp_market_config(self):
        """Handle perpetual futures market config request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Futures Market Config for {symbol or self.acct.default_symbol}",
                           self.acct.get_perp_market_config(symbol))

    def handle_spot_price(self):
        """Handle spot price request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Spot Price for {symbol or self.acct.default_symbol}",
                           self.acct.get_spot_price(symbol))

    def handle_buy_spot(self):
        """Handle buy spot request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = self.acct.default_symbol

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = self.acct.default_quantity

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (leave empty for auto-calculated price): ")
            if price_input:
                price = float(price_input)
        if not price:
            # get current price
            price = self.acct.get_spot_price(symbol)
            if not price:
                self.print_response("Error", "Failed to get current price")
                return

        time_in_force = input("Enter time in force,For Market order only FOK/IOC is valid (GTC, IOC, FOK, leave empty for GTC): ").upper() or "GTC"

        self.print_response("Buy Spot Result",
                          self.acct.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                          order_type=order_type, time_in_force=time_in_force))

    def handle_sell_spot(self):
        """Handle sell spot request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = self.acct.default_symbol

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = self.acct.default_quantity

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (leave empty for current price): ")
            if price_input:
                price = float(price_input)
            else:
                current_price = self.acct.get_spot_price(symbol)
                if not current_price:
                    self.print_response("Error", "Failed to get current price")
                    return

        time_in_force = input("Enter time in force,For Market order only FOK/IOC is valid (GTC, IOC, FOK, leave empty for GTC): ").upper() or "GTC"

        self.print_response("Sell Spot Result",
                          self.acct.sell_spot(symbol=symbol, price=price, quantity=quantity,
                                           order_type=order_type, time_in_force=time_in_force))

    def handle_open_long_fut(self):
        """Handle open long futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (required for LIMIT orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for LIMIT orders")
                return

        time_in_force = input(f"Enter time in force (leave empty for {'FOK' if order_type == 'MARKET' else 'GTC'}): ").upper() or ""

        self.print_response("Open Long Futures Position",
                           self.acct.open_long_fut(symbol=symbol, price=price, quantity=quantity,
                                                 order_type=order_type, time_in_force=time_in_force))

    def handle_close_long_fut(self):
        """Handle close long futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (required for LIMIT orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for LIMIT orders")
                return

        time_in_force = input(f"Enter time in force (leave empty for {'FOK' if order_type == 'MARKET' else 'GTC'}): ").upper() or ""

        self.print_response("Close Long Futures Position",
                           self.acct.close_long_fut(symbol=symbol, price=price, quantity=quantity,
                                                  order_type=order_type, time_in_force=time_in_force))

    def handle_open_short_fut(self):
        """Handle open short futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (required for LIMIT orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for LIMIT orders")
                return

        time_in_force = input(f"Enter time in force (leave empty for {'FOK' if order_type == 'MARKET' else 'GTC'}): ").upper() or ""

        self.print_response("Open Short Futures Position",
                           self.acct.open_short_fut(symbol=symbol, price=price, quantity=quantity,
                                                  order_type=order_type, time_in_force=time_in_force))

    def handle_close_short_fut(self):
        """Handle close short futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.default_quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "LIMIT":
            price_input = input("Enter price (required for LIMIT orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for LIMIT orders")
                return

        time_in_force = input(f"Enter time in force (leave empty for {'FOK' if order_type == 'MARKET' else 'GTC'}): ").upper() or ""

        self.print_response("Close Short Futures Position",
                           self.acct.close_short_fut(symbol=symbol, price=price, quantity=quantity,
                                                   order_type=order_type, time_in_force=time_in_force))

    def handle_cancel_spot_orders(self):
        """Handle cancel spot orders request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = self.acct.default_symbol
        self.print_response("Cancel Spot Orders", self.acct.cancel_spot_orders(symbol=symbol))

    def handle_cancel_fut_orders(self):
        """Handle cancel futures orders request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = self.acct.default_symbol
        self.print_response("Cancel Futures Orders", self.acct.cancel_fut_orders(symbol=symbol))

    def handle_transfer(self):
        """Handle transfer between accounts request"""
        print("\nAvailable account types:")
        print("  SPOT : Spot")
        print("  LEVER : Margin")
        print("  FINANCE : Finance")
        print("  FUTURES_U : USDT-M Futures")
        print("  FUTURES_C : Coin-M Futures")
        print()

        from_account = input("Enter source account type: ")
        to_account = input("Enter destination account type: ")
        currency = input("Enter currency (lowercase, e.g., usdt, btc): ")
        symbol = input("Enter symbol: ")
        amount = float(input("Enter amount: "))

        self.print_response("Transfer Result",
                          self.acct.transfer(from_account, to_account, currency, amount, symbol))

    def handle_get_spot_hist_orders(self):
        """Handle get spot historical orders request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None
            
        limit = input("Enter limit (leave empty for default 5): ")
        if limit:
            limit = int(limit)
        else:
            limit = 5
            
        self.print_response(f"Spot Historical Orders for {symbol or self.acct.default_symbol}",
                           self.acct.get_spot_hist_orders(symbol=symbol, limit=limit))

    def handle_get_um_hist_orders(self):
        """Handle get futures historical orders request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.default_symbol}): ")
        if not symbol:
            symbol = None
            
        limit = input("Enter limit (leave empty for default 5): ")
        if limit:
            limit = int(limit)
        else:
            limit = 5
            
        self.print_response(f"Futures Historical Orders for {symbol or self.acct.default_symbol}",
                           self.acct.get_um_hist_orders(symbol=symbol, limit=limit))

    def handle_get_spot_order(self):
        """Handle get spot order by ID request"""
        order_id = input("Enter Spot Order ID: ")
        if not order_id:
            self.print_response("Error", "Order ID cannot be empty.")
            return
        self.print_response(f"Spot Order Details for ID {order_id}",
                           self.acct.get_spot_order(order_id))

    def handle_get_um_order(self):
        """Handle get UM futures order by ID request"""
        order_id = input("Enter UM Futures Order ID: ")
        if not order_id:
            self.print_response("Error", "Order ID cannot be empty.")
            return
        self.print_response(f"UM Futures Order Details for ID {order_id}",
                           self.acct.get_um_order(order_id))

    def handle_get_cm_order(self):
        """Handle get CM futures order by ID request"""
        order_id = input("Enter CM Futures Order ID: ")
        if not order_id:
            self.print_response("Error", "Order ID cannot be empty.")
            return
        self.print_response(f"CM Futures Order Details for ID {order_id}",
                           self.acct.get_cm_order(order_id))

    def handle_get_acct_list(self):
        """Handle get account list request"""
        account_id = input("Enter Account ID (leave empty for none): ")
        if not account_id:
            account_id = None

        account_name = input("Enter Account Name (leave empty for none): ")
        if not account_name:
            account_name = None

        level_input = input("Enter Level (leave empty for default 1): ")
        if level_input:
            try:
                level = int(level_input)
            except ValueError:
                self.print_response("Error", "Level must be an integer.")
                return
        else:
            level = 1

        self.print_response("Account List", self.acct.get_acct_list(account_id, account_name, level))

    def main(self):
        """
        Main application loop

        This method runs the main application loop, handling account selection
        and menu navigation.
        """
        # Load API keys
        if not self.load_api_keys():
            return

        # Account selection loop
        while True:
            # Select an account
            if not self.select_account():
                break

            # Menu loop for the selected account
            while True:
                if not self.display_menu():
                    break


if __name__ == "__main__":
    # Create an instance of the XtUtilsApp and run it
    app = XtUtilsApp()
    app.main()
