import sys
import yaml
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))
from rest.okx import OkxApi

"""
OKX Exchange Utility Script

This script provides a command-line interface for interacting with the OKX Exchange API.
It allows users to perform various operations on both spot and futures markets,
including checking balances, placing orders, and managing positions.

Usage:
    python okx_utils_script.py

The script will load API keys from the .keys.yaml file in the same directory.
"""

PRICE_REQ = OkxApi.PRICE_REQ

class OkxUtils:
    def __init__(self, api_key, api_secret, passphrase, use_simulated=False, spot_symbol="BTC-USDT", perp_symbol="BTC-USDT-SWAP", quantity=0.001):
        """
        Initialize the OKX Utils client

        Args:
            api_key (str): OKX API key
            api_secret (str): OKX API secret
            passphrase (str): OKX API passphrase
            use_simulated (bool, optional): Whether to use simulated trading. Defaults to True.
            spot_symbol (str, optional): Default spot trading symbol. Defaults to "BTC-USDT".
            perp_symbol (str, optional): Default perpetual futures trading symbol. Defaults to "BTC-USDT-SWAP".
            quantity (float, optional): Default trading quantity. Defaults to 0.001.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase
        self.use_simulated = use_simulated
        self.spot_symbol = spot_symbol
        self.perp_symbol = perp_symbol
        self.quantity = quantity

        # Initialize the OKX API client
        self.client = OkxApi(
            api_key=self.api_key,
            api_secret=self.api_secret,
            passphrase=self.passphrase,
            spot_symbol=self.spot_symbol,
            perp_symbol=self.perp_symbol,
            quantity=self.quantity,
            use_simulated=self.use_simulated
        )

    def get_spot_balance(self):
        """
        Get spot account balance

        Returns:
            dict: Spot account balance
        """
        return self.client.get_spot_balance()

    def get_fut_balance(self):
        """
        Get futures account balance

        Returns:
            dict: Futures account balance
        """
        return self.client.get_fut_balance()

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
            dict: Spot price information
        """
        return self.client.get_spot_price(symbol=symbol)

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

    def get_fut_open_orders(self):
        """
        Get open futures orders

        Returns:
            dict: Open futures orders
        """
        return self.client.get_fut_open_orders()

    def get_account_config(self):
        """
        Get account configuration

        Returns:
            dict: Account configuration
        """
        return self.client.get_account_config()

    def get_spot_fee(self, symbol=None):
        """
        Get spot trading fees

        Args:
            symbol (str, optional): Symbol to get fees for. Defaults to None (uses default symbol).

        Returns:
            dict: Spot trading fees
        """
        return self.client.get_spot_comms_rate(symbol=symbol)

    def get_fut_fee(self, symbol=None):
        """
        Get futures trading fees

        Args:
            symbol (str, optional): Symbol to get fees for. Defaults to None (uses default symbol).

        Returns:
            dict: Futures trading fees
        """
        return self.client.get_um_comms_rate(symbol=symbol)

    def get_spot_trades(self, instId='', uly='', ordId='', after='', before='', limit='', instFamily='', begin='', end=''):
        """
        Get spot trades history

        Args:
            instId (str, optional): Instrument ID. Defaults to ''.
            uly (str, optional): Underlying. Defaults to ''.
            ordId (str, optional): Order ID. Defaults to ''.
            after (str, optional): Pagination of data to return records earlier than the requested trade ID. Defaults to ''.
            before (str, optional): Pagination of data to return records newer than the requested trade ID. Defaults to ''.
            limit (str, optional): Number of results per request. Maximum 100. Defaults to ''.
            instFamily (str, optional): Instrument family. Defaults to ''.
            begin (str, optional): Start time (Unix timestamp in milliseconds). Defaults to ''.
            end (str, optional): End time (Unix timestamp in milliseconds). Defaults to ''.

        Returns:
            dict: Spot trades history
        """
        return self.client.get_spot_trades(instId=instId, uly=uly, ordId=ordId, after=after, before=before,
                                          limit=limit, instFamily=instFamily, begin=begin, end=end)

    def get_um_trades(self, instId='', uly='', ordId='', after='', before='', limit='', instFamily='', begin='', end=''):
        """
        Get futures trades history

        Args:
            instId (str, optional): Instrument ID. Defaults to ''.
            uly (str, optional): Underlying. Defaults to ''.
            ordId (str, optional): Order ID. Defaults to ''.
            after (str, optional): Pagination of data to return records earlier than the requested trade ID. Defaults to ''.
            before (str, optional): Pagination of data to return records newer than the requested trade ID. Defaults to ''.
            limit (str, optional): Number of results per request. Maximum 100. Defaults to ''.
            instFamily (str, optional): Instrument family. Defaults to ''.
            begin (str, optional): Start time (Unix timestamp in milliseconds). Defaults to ''.
            end (str, optional): End time (Unix timestamp in milliseconds). Defaults to ''.

        Returns:
            dict: Futures trades history
        """
        return self.client.get_um_trades(instId=instId, uly=uly, ordId=ordId, after=after, before=before,
                                        limit=limit, instFamily=instFamily, begin=begin, end=end)

    def buy_spot(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Place a spot buy order

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.spot_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.buy_spot(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def sell_spot(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Place a spot sell order

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.spot_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.sell_spot(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def open_long_fut(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Open a long futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.perp_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.open_long_fut(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def close_long_fut(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Close a long futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.perp_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.close_long_fut(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def open_short_fut(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Open a short futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.perp_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.open_short_fut(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def close_short_fut(self, symbol=None, price=None, quantity=None, order_type='limit'):
        """
        Close a short futures position

        Args:
            symbol (str, optional): Trading symbol. Defaults to None (uses default symbol).
            price (float, optional): Order price. Required for limit orders.
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('limit' or 'market'). Defaults to 'limit'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.perp_symbol

        if quantity is None:
            quantity = self.quantity

        if price is None and order_type.lower() == 'limit':
            return {"error": "Price is required for limit orders"}

        return self.client.close_short_fut(
            symbol=symbol,
            price=price,
            quantity=quantity,
            order_type=order_type
        )

    def cancel_spot_orders(self):
        """
        Cancel all open spot orders

        Returns:
            dict: Cancellation response
        """
        return self.client.cancel_spot_open_orders()

    def cancel_fut_orders(self):
        """
        Cancel all open futures orders

        Returns:
            dict: Cancellation response
        """
        return self.client.cancel_fut_open_orders()
    
    def cancel_algo_orders(self):
        """
        Cancel all open futures algo orders

        Returns:
            dict: Cancellation response
        """
        return self.client.cancel_algo_open_orders()

    def test_buy_spot(self):
        """
        Test spot buy with market order using default settings

        Returns:
            dict: Order response
        """
        return self.client.test_buy_spot()

    def test_sell_spot(self):
        """
        Test spot sell with market order using default settings

        Returns:
            dict: Order response
        """
        return self.client.test_sell_spot()

    def test_open_long_fut(self, qty_prec=0, cont_size=1):
        """
        Test opening a long futures position

        Args:
            qty_prec (int, optional): Quantity precision. Defaults to 0.
            cont_size (float, optional): Contract size. Defaults to 1.

        Returns:
            dict: Order response
        """
        return self.client.test_open_long_fut(qty_prec=qty_prec, cont_size=cont_size)

    def test_close_long_fut(self, qty_prec=0, cont_size=1):
        """
        Test closing a long futures position

        Args:
            qty_prec (int, optional): Quantity precision. Defaults to 0.
            cont_size (float, optional): Contract size. Defaults to 1.

        Returns:
            dict: Order response
        """
        return self.client.test_close_long_fut(qty_prec=qty_prec, cont_size=cont_size)

    def set_account_level(self, acct_lv):
        """
        Set account level

        Args:
            acct_lv (int): Account level
                1: Spot
                2: Spot and futures mode
                3: Multi-currency margin code
                4: Portfolio margin mode

        Returns:
            dict: Response
        """
        return self.client.set_account_level(acct_lv=acct_lv)

    def set_position_mode(self, pos_mode):
        """
        Set position mode

        Args:
            pos_mode (str): Position mode
                long_short_mode: Long/short mode
                net_mode: Net mode

        Returns:
            dict: Response
        """
        return self.client.set_position_mode(pos_mode=pos_mode)

    def funds_transfer(self, ccy: str, amt: str, from_account: str, to_account: str, type: str = "0", subAcct: str = "", instId: str = "", toInstId: str = "", loanTrans: bool = False, omitPosRisk: bool = False):
        """
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
        """
        return self.client.funds_transfer(ccy=ccy, amt=amt, from_account=from_account, to_account=to_account, type=type, subAcct=subAcct, instId=instId, toInstId=toInstId, loanTrans=loanTrans, omitPosRisk=omitPosRisk)


class OkxUtilsApp:
    """
    OKX Exchange Utility Application

    This class provides a command-line interface for interacting with the OKX Exchange API.
    It allows users to perform various operations on both spot and futures markets,
    including checking balances, placing orders, and managing positions.
    """
    def __init__(self):
        """Initialize the OKX Utils Application"""
        self.acct_dict = {}
        self.selected_account = None
        self.acct = None

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
                {"text": "Get futures trades", "action": "get_um_trades"}
            ],
            "MARKET DATA": [
                {"text": "Get spot price", "action": "spot_price"},
                {"text": "Get spot market config", "action": "spot_config"},
                {"text": "Get futures market config", "action": "perp_market_config"}
            ],
            "TRADING OPERATIONS": [
                {"text": "Buy spot (limit/market)", "action": "buy_spot"},
                {"text": "Sell spot (limit/market)", "action": "sell_spot"},
                {"text": "Open long futures position", "action": "open_long_fut"},
                {"text": "Close long futures position", "action": "close_long_fut"},
                {"text": "Open short futures position", "action": "open_short_fut"},
                {"text": "Close short futures position", "action": "close_short_fut"},
                {"text": "Cancel spot open orders", "action": "cancel_spot_orders"},
                {"text": "Cancel futures open orders", "action": "cancel_fut_orders"},
                {"text": "Cancel algo open orders", "action": "cancel_algo_orders"}
            ],
            "TEST OPERATIONS": [
                {"text": "Test buy spot (market)", "action": "test_buy_spot"},
                {"text": "Test sell spot (market)", "action": "test_sell_spot"},
                {"text": "Test open long futures", "action": "test_open_long_fut"},
                {"text": "Test close long futures", "action": "test_close_long_fut"}
            ],
            "ACCOUNT SETTINGS": [
                {"text": "Set account level", "action": "set_account_level"},
                {"text": "Set position mode", "action": "set_position_mode"}
            ],
            "FUNDS MANAGEMENT": [
                {"text": "Funds Transfer", "action": "funds_transfer"}
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
            "test_buy_spot": self.handle_test_buy_spot,
            "test_sell_spot": self.handle_test_sell_spot,
            "test_open_long_fut": self.handle_test_open_long_fut,
            "test_close_long_fut": self.handle_test_close_long_fut,
            "set_account_level": self.handle_set_account_level,
            "set_position_mode": self.handle_set_position_mode,
            "cancel_algo_orders": self.handle_cancel_algo_orders
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
            print("Please create a .keys.yaml file with your OKX API keys.")
            print("Example format:")
            print("""
okx:
  read_only_1:
    api_key: "your_api_key"
    api_secret: "your_api_secret"
    passphrase: "your_passphrase"
    use_simulated: true
  read_write_2:
    api_key: "another_api_key"
    api_secret: "another_api_secret"
    passphrase: "another_passphrase"
    use_simulated: true
            """)
            return False
        except yaml.YAMLError:
            print("Error parsing .keys.yaml file. Please check the format.")
            return False

        # Get the OKX keys
        if 'okx' not in keys:
            print("No 'okx' section found in .keys.yaml file.")
            return False

        for name, key_data in keys['okx'].items():
            try:
                api_key = key_data['api_key']
                api_secret = key_data['api_secret']
                passphrase = key_data['passphrase']
                use_simulated = key_data.get('use_simulated', True)
                print(f"Loading account: {name}, api_key: {api_key}, api_secret: {api_secret}, passphrase: {passphrase}, use_simulated: {use_simulated}")
                # Initialize the OKX Utils
                okx_utils = OkxUtils(
                    api_key=api_key,
                    api_secret=api_secret,
                    passphrase=passphrase,
                    use_simulated=use_simulated
                )

                # Add to accounts dictionary
                self.acct_dict[name] = okx_utils
                print(f"Loaded account: {name} (Simulated: {use_simulated})")
            except KeyError as e:
                print(f"Warning: Missing API keys for account {name}: {e}")
                continue
            except Exception as e:
                print(f"Error initializing account {name}: {e}")
                continue

        if not self.acct_dict:
            print("No valid OKX API keys found in .keys.yaml")
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
        self.print_response("Spot Open Orders", self.acct.get_spot_open_orders())

    def handle_fut_open_orders(self):
        """Handle futures open orders request"""
        self.print_response("Futures Open Orders", self.acct.get_fut_open_orders())

    def handle_spot_fee(self):
        """Handle spot fee request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.spot_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response("Spot Fee", self.acct.get_spot_fee(symbol=symbol))

    def handle_fut_fee(self):
        """Handle futures fee request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response("Futures Fee", self.acct.get_fut_fee(symbol=symbol))

    def handle_account_config(self):
        """Handle account config request"""
        self.print_response("Account Config", self.acct.get_account_config())

    def handle_get_spot_trades(self):
        """Handle get spot trades request"""
        instId = input(f"Enter instrument ID (leave empty for default {self.acct.spot_symbol}): ")
        ordId = input("Enter order ID (leave empty for none): ")
        limit = input("Enter limit (leave empty for default): ")

        self.print_response(f"Spot Trades for {instId or self.acct.spot_symbol}",
                           self.acct.get_spot_trades(instId=instId, ordId=ordId, limit=limit))

    def handle_get_um_trades(self):
        """Handle get futures trades request"""
        instId = input(f"Enter instrument ID (leave empty for default {self.acct.perp_symbol}): ")
        ordId = input("Enter order ID (leave empty for none): ")
        limit = input("Enter limit (leave empty for default): ")

        self.print_response(f"Futures Trades for {instId or self.acct.perp_symbol}",
                           self.acct.get_um_trades(instId=instId, ordId=ordId, limit=limit))

    def handle_spot_config(self):
        """Handle spot market config request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.spot_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Spot Market Config for {symbol or self.acct.spot_symbol}",
                           self.acct.get_spot_config(symbol=symbol))

    def handle_perp_market_config(self):
        """Handle perpetual futures market config request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Futures Market Config for {symbol or self.acct.perp_symbol}",
                           self.acct.get_perp_market_config(symbol=symbol))

    def handle_spot_price(self):
        """Handle spot price request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.spot_symbol}): ")
        if not symbol:
            symbol = None
        self.print_response(f"Spot Price for {symbol or self.acct.spot_symbol}",
                           self.acct.get_spot_price(symbol=symbol))

    def handle_buy_spot(self):
        """Handle buy spot request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.spot_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None

        if order_type  in PRICE_REQ:
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Buy Spot Result",
                          self.acct.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                          order_type=order_type))

    def handle_sell_spot(self):
        """Handle sell spot request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.spot_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "limit":
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Sell Spot Result",
                          self.acct.sell_spot(symbol=symbol, price=price, quantity=quantity,
                                           order_type=order_type))

    def handle_open_long_fut(self):
        """Handle open long futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "limit":
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Open Long Futures Position",
                           self.acct.open_long_fut(symbol=symbol, price=price, quantity=quantity,
                                                 order_type=order_type))

    def handle_close_long_fut(self):
        """Handle close long futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "limit":
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Close Long Futures Position",
                           self.acct.close_long_fut(symbol=symbol, price=price, quantity=quantity,
                                                  order_type=order_type))

    def handle_open_short_fut(self):
        """Handle open short futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "limit":
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Open Short Futures Position",
                           self.acct.open_short_fut(symbol=symbol, price=price, quantity=quantity,
                                                  order_type=order_type))

    def handle_close_short_fut(self):
        """Handle close short futures position request"""
        symbol = input(f"Enter symbol (leave empty for default {self.acct.perp_symbol}): ")
        if not symbol:
            symbol = None

        order_type = input("Enter order type (limit or market, leave empty for limit): ").lower() or "limit"

        quantity = input(f"Enter quantity (leave empty for default {self.acct.quantity}): ")
        if quantity:
            quantity = float(quantity)
        else:
            quantity = None

        price = None
        if order_type == "limit":
            price_input = input("Enter price (required for limit orders): ")
            if price_input:
                price = float(price_input)
            else:
                self.print_response("Error", "Price is required for limit orders")
                return

        self.print_response("Close Short Futures Position",
                           self.acct.close_short_fut(symbol=symbol, price=price, quantity=quantity,
                                                   order_type=order_type))

    def handle_cancel_spot_orders(self):
        """Handle cancel spot orders request"""
        self.print_response("Cancel Spot Orders", self.acct.cancel_spot_orders())

    def handle_cancel_fut_orders(self):
        """Handle cancel futures orders request"""
        self.print_response("Cancel Futures Orders", self.acct.cancel_fut_orders())

    def handle_test_buy_spot(self):
        """Handle test buy spot request"""
        self.print_response("Test Buy Spot Result", self.acct.test_buy_spot())

    def handle_test_sell_spot(self):
        """Handle test sell spot request"""
        self.print_response("Test Sell Spot Result", self.acct.test_sell_spot())

    def handle_test_open_long_fut(self):
        """Handle test open long futures position request"""
        qty_prec = input("Enter quantity precision (leave empty for default 0): ")
        if qty_prec:
            qty_prec = int(qty_prec)
        else:
            qty_prec = 0

        cont_size = input("Enter contract size (leave empty for default 1): ")
        if cont_size:
            cont_size = float(cont_size)
        else:
            cont_size = 1

        self.print_response("Test Open Long Futures Position",
                           self.acct.test_open_long_fut(qty_prec=qty_prec, cont_size=cont_size))

    def handle_test_close_long_fut(self):
        """Handle test close long futures position request"""
        qty_prec = input("Enter quantity precision (leave empty for default 0): ")
        if qty_prec:
            qty_prec = int(qty_prec)
        else:
            qty_prec = 0

        cont_size = input("Enter contract size (leave empty for default 1): ")
        if cont_size:
            cont_size = float(cont_size)
        else:
            cont_size = 1

        self.print_response("Test Close Long Futures Position",
                           self.acct.test_close_long_fut(qty_prec=qty_prec, cont_size=cont_size))

    def handle_set_account_level(self):
        """Handle set account level request"""
        print("\nAvailable account levels:")
        print("  1: Spot")
        print("  2: Spot and futures mode")
        print("  3: Multi-currency margin code")
        print("  4: Portfolio margin mode")
        print()

        acct_lv = input("Enter account level (1-4): ")
        if acct_lv not in ["1", "2", "3", "4"]:
            self.print_response("Error", "Invalid account level")
            return

        self.print_response("Set Account Level Result", self.acct.set_account_level(acct_lv=acct_lv))

    def handle_set_position_mode(self):
        """Handle set position mode request"""
        print("\nAvailable position modes:")
        print("  long_short_mode: Long/short mode")
        print("  net_mode: Net mode")
        print()

        pos_mode = input("Enter position mode (long_short_mode or net_mode): ")
        if pos_mode not in ["long_short_mode", "net_mode"]:
            self.print_response("Error", "Invalid position mode")
            return

        self.print_response("Set Position Mode Result", self.acct.set_position_mode(pos_mode=pos_mode))

    def handle_cancel_algo_orders(self):
        """Handle cancel algo orders request"""
        self.print_response("Cancel Algo Orders", self.acct.cancel_algo_orders())

    def handle_funds_transfer(self):
        """
        Handle funds transfer request.
        """
        print("\n--- Funds Transfer ---")
        ccy = input("Enter currency (e.g., USDT): ")
        amt = input("Enter amount: ")
        
        print("\nAccount Types:")
        print("  6: Funding Account")
        print("  18: Trading Account")
        from_account = input("Transfer FROM account (6 or 18): ")
        to_account = input("Transfer TO account (6 or 18): ")

        if from_account not in ["6", "18"] or to_account not in ["6", "18"]:
            self.print_response("Error", "Invalid account type. Please use 6 or 18.")
            return

        try:
            self.print_response("Funds Transfer Result",
                               self.acct.funds_transfer(
                                   ccy=ccy,
                                   amt=amt,
                                   from_account=from_account,
                                   to_account=to_account
                               ))
        except Exception as e:
            self.print_response("Error", f"An error occurred during funds transfer: {e}")

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
    # Create an instance of the OkxUtilsApp and run it
    app = OkxUtilsApp()
    app.main()
