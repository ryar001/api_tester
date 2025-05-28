import sys
from pathlib import Path
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
    def __init__(self, api_key, api_secret, spot_host="https://sapi.xt.com", perp_host="https://fapi.xt.com", default_symbol="btc_usdt", default_quantity=0.001):
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
        self.perp_host = perp_host
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity

        # Initialize the XT API client
        self.client = XtApi(
            spot_host=self.spot_host,
            um_host=self.perp_host,
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
            price (float, optional): Order price. Defaults to None (calculated based on current price).
            quantity (float, optional): Order quantity. Defaults to None (uses default quantity).
            order_type (str, optional): Order type ('LIMIT' or 'MARKET'). Defaults to 'LIMIT'.
            time_in_force (str, optional): Time in force. Defaults to 'GTC'.

        Returns:
            dict: Order response
        """
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if price is None and order_type == 'LIMIT':
            # Get current price
            current_price = self.client.get_spot_price(symbol)
            if not current_price:
                return {"error": "Failed to get current price"}

            # Get market config for precision
            config = self.client.get_spot_config(symbol)
            if config is None:
                return {"error": "Failed to get market config"}
            config = config[0]
            price_precision = int(config["pricePrecision"])

            # Calculate a price below current price to avoid execution
            price = round(current_price * self.client.default_price_multiplier, price_precision)

        return self.client.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                   order_type=order_type, time_in_force=time_in_force)

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
        if symbol is None:
            symbol = self.default_symbol

        if quantity is None:
            quantity = self.default_quantity

        if price is None and order_type == 'LIMIT':
            # Get current price
            current_price = self.client.get_spot_price(symbol)
            if not current_price:
                return {"error": "Failed to get current price"}

            # Get market config for precision
            config = self.client.get_spot_config(symbol)
            if config is None:
                return {"error": "Failed to get market config"}
            config = config[0]
            price_precision = int(config["pricePrecision"])

            # Calculate a price above current price to avoid execution
            price = round(current_price * (1 + (1 - self.client.default_price_multiplier)), price_precision)

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

    def open_long_fut(self):
        """
        Open a long futures position

        Returns:
            dict: Order response
        """
        precision_values = self._get_perp_precision_values()
        if not precision_values:
            return {"error": "Failed to get precision values"}

        price_precision, qty_precision, contract_size = precision_values
        return self.client.test_open_long_fut(price_precision, qty_precision, contract_size)

    def close_long_fut(self):
        """
        Close a long futures position

        Returns:
            dict: Order response
        """
        precision_values = self._get_perp_precision_values()
        if not precision_values:
            return {"error": "Failed to get precision values"}

        price_precision, qty_precision, contract_size = precision_values
        return self.client.test_close_long_fut(price_precision, qty_precision, contract_size)

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

    def transfer(self, from_account, to_account, currency, amount):
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
            amount (float): Amount to transfer

        Returns:
            dict: Transfer response
        """
        return self.client.transfer(from_account, to_account, currency, amount)

    def get_trades(self, symbol=None, biz_type="SPOT"):
        """
        Get account trade history

        Args:
            symbol (str, optional): Symbol to get trades for. Defaults to None (uses default symbol).
            biz_type (str, optional): BizType to get trades for. Defaults to "SPOT".

        Returns:
            dict: Trade history
        """
        return self.client.get_trades(symbol, biz_type)


if __name__ == "__main__":
    import yaml
    import json
    from pathlib import Path

    # Function to print formatted responses
    def print_response(title, response):
        """Print a formatted response."""
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

    # Load API keys from the .keys.yaml file
    keys_path = Path(__file__).parent / '.keys.yaml'
    acct_dict = {}

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
    api_key: "your_api_key"
    api_secret: "your_api_secret"
  read_write_2:
    api_key: "another_api_key"
    api_secret: "another_api_secret"
        """)
        sys.exit(1)
    except yaml.YAMLError:
        print("Error parsing .keys.yaml file. Please check the format.")
        sys.exit(1)

    # Get the XT keys
    if 'xt' not in keys:
        print("No 'xt' section found in .keys.yaml file.")
        sys.exit(1)

    for name, key_data in keys['xt'].items():
        try:
            api_key = key_data['api_key']
            api_secret = key_data['api_secret']
            # Initialize the XT Utils
            xt_utils = XtUtils(api_key, api_secret)

            # Add to accounts dictionary
            acct_dict[name] = xt_utils
            print(f"Loaded account: {name}")
        except KeyError:
            print(f"Warning: Missing API keys for account {name}")
            continue
        except Exception as e:
            print(f"Error initializing account {name}: {e}")
            continue

    if not acct_dict:
        print("No valid XT API keys found in .keys.yaml")
        sys.exit(1)

    # Account selection loop
    while True:
        print("\nAVAILABLE ACCOUNTS:")
        print("=" * 40)

        # Create a numbered list of accounts
        account_options = {}
        for i, account_name in enumerate(acct_dict.keys(), 1):
            print(f"{i}. {account_name}")
            account_options[str(i)] = account_name

        # Add exit option
        print("0. Exit")
        print("=" * 40)

        choice = input("Enter account number (or '0' to exit): ")

        if choice == '0':
            print("Exiting program.")
            sys.exit(0)

        if choice not in account_options:
            print("Invalid account number. Please try again.")
            continue

        # Get the selected account name and object
        selected_account = account_options[choice]
        acct = acct_dict[selected_account]

        # Main menu loop
        while True:
            print(f"\nSelected account: {selected_account}")
            print("=" * 40)
            print("MENU OPTIONS:")

            # Define menu categories and their options with corresponding actions
            menu_categories = {
                "ACCOUNT INFO": [
                    {"text": "Get spot balance", "action": "spot_balance"},
                    {"text": "Get futures balance", "action": "fut_balance"},
                    {"text": "Get futures position", "action": "fut_position"},
                    {"text": "Get spot open orders", "action": "spot_open_orders"},
                    {"text": "Get futures open orders", "action": "fut_open_orders"},
                    {"text": "Get spot fee", "action": "spot_fee"},
                    {"text": "Get futures fee", "action": "fut_fee"},
                    {"text": "Get account config", "action": "account_config"},
                    {"text": "Get account trades", "action": "get_trades"}
                ],
                "MARKET DATA": [
                    {"text": "Get spot price", "action": "spot_price"}
                ],
                "TRADING OPERATIONS": [
                    {"text": "Buy spot (LIMIT/MARKET)", "action": "buy_spot"},
                    {"text": "Sell spot (LIMIT/MARKET)", "action": "sell_spot"},
                    {"text": "Open long futures position", "action": "open_long_fut"},
                    {"text": "Close long futures position", "action": "close_long_fut"},
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

            # Generate menu with automatic numbering
            option_number = 1
            option_map = {}

            for category, options in menu_categories.items():
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

                    # Define action handlers
                    def handle_exit():
                        return "break"

                    def handle_quit():
                        print("Exiting program.")
                        sys.exit(0)

                    def handle_spot_balance():
                        print_response("Spot Balance", acct.get_spot_balance())

                    def handle_fut_balance():
                        print_response("Futures Balance", acct.get_fut_balance())

                    def handle_fut_position():
                        print_response("Futures Position", acct.get_fut_position())

                    def handle_spot_open_orders():
                        print_response("Spot Open Orders", acct.get_spot_open_orders())

                    def handle_fut_open_orders():
                        print_response("Futures Open Orders", acct.get_fut_open_orders())

                    def handle_spot_fee():
                        print_response("Spot Fee", acct.get_spot_fee())

                    def handle_fut_fee():
                        print_response("Futures Fee", acct.get_fut_fee())

                    def handle_account_config():
                        print_response("Account Config", acct.get_account_config())

                    def handle_get_trades():
                        symbol = input(f"Enter symbol (leave empty for default {acct.default_symbol}): ")
                        biz_type = input("Enter BizType (leave empty for SPOT): ") or "SPOT"
                        if not symbol:
                            symbol = None
                        print_response(f"Account Trades for {symbol or acct.default_symbol}", acct.get_trades(symbol, biz_type))

                    def handle_spot_price():
                        symbol = input(f"Enter symbol (leave empty for default {acct.default_symbol}): ")
                        if not symbol:
                            symbol = None
                        print_response(f"Spot Price for {symbol or acct.default_symbol}", acct.get_spot_price(symbol))

                    def handle_buy_spot():
                        symbol = input(f"Enter symbol (leave empty for default {acct.default_symbol}): ")
                        if not symbol:
                            symbol = None

                        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

                        quantity = input(f"Enter quantity (leave empty for default {acct.default_quantity}): ")
                        if quantity:
                            quantity = float(quantity)
                        else:
                            quantity = None

                        price = None
                        if order_type == "LIMIT":
                            price_input = input("Enter price (leave empty for auto-calculated price): ")
                            if price_input:
                                price = float(price_input)
                        else:
                            # get current price 
                            current_price = acct.get_spot_price(symbol)
                            if not current_price:
                                print_response("Error", "Failed to get current price")
                                return
                            price = current_price

                        time_in_force = input("Enter time in force (GTC, IOC, FOK, leave empty for GTC): ").upper() or "GTC"

                        print_response("Buy Spot Result",
                                      acct.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                                  order_type=order_type, time_in_force=time_in_force))

                    def handle_sell_spot():
                        symbol = input(f"Enter symbol (leave empty for default {acct.default_symbol}): ")
                        if not symbol:
                            symbol = None

                        order_type = input("Enter order type (LIMIT or MARKET, leave empty for LIMIT): ").upper() or "LIMIT"

                        quantity = input(f"Enter quantity (leave empty for default {acct.default_quantity}): ")
                        if quantity:
                            quantity = float(quantity)
                        else:
                            quantity = None

                        price = None
                        if order_type == "LIMIT":
                            price_input = input("Enter price (leave empty for auto-calculated price): ")
                            if price_input:
                                price = float(price_input)

                        time_in_force = input("Enter time in force (GTC, IOC, FOK, leave empty for GTC): ").upper() or "GTC"

                        print_response("Sell Spot Result",
                                      acct.sell_spot(symbol=symbol, price=price, quantity=quantity,
                                                   order_type=order_type, time_in_force=time_in_force))

                    def handle_open_long_fut():
                        print_response("Open Long Futures Position", acct.open_long_fut())

                    def handle_close_long_fut():
                        print_response("Close Long Futures Position", acct.close_long_fut())

                    def handle_cancel_spot_orders():
                        print_response("Cancel Spot Orders", acct.cancel_spot_orders())

                    def handle_cancel_fut_orders():
                        print_response("Cancel Futures Orders", acct.cancel_fut_orders())

                    def handle_transfer():
                        print("\nAvailable account types:")
                        print("  SPOT: Spot")
                        print("  LEVER: Margin")
                        print("  FINANCE: Finance")
                        print("  FUTURES_U: USDT-M Futures")
                        print("  FUTURES_C: Coin-M Futures")
                        print()

                        from_account = input("Enter source account type: ")
                        to_account = input("Enter destination account type: ")
                        currency = input("Enter currency (lowercase, e.g., usdt, btc): ")
                        amount = float(input("Enter amount: "))

                        print_response("Transfer Result",
                                      acct.transfer(from_account, to_account, currency, amount))

                    # Map actions to handler functions
                    action_handlers = {
                        "exit": handle_exit,
                        "quit": handle_quit,
                        "spot_balance": handle_spot_balance,
                        "fut_balance": handle_fut_balance,
                        "fut_position": handle_fut_position,
                        "spot_open_orders": handle_spot_open_orders,
                        "fut_open_orders": handle_fut_open_orders,
                        "spot_fee": handle_spot_fee,
                        "fut_fee": handle_fut_fee,
                        "account_config": handle_account_config,
                        "get_trades": handle_get_trades,
                        "spot_price": handle_spot_price,
                        "buy_spot": handle_buy_spot,
                        "sell_spot": handle_sell_spot,
                        "open_long_fut": handle_open_long_fut,
                        "close_long_fut": handle_close_long_fut,
                        "cancel_spot_orders": handle_cancel_spot_orders,
                        "cancel_fut_orders": handle_cancel_fut_orders,
                        "transfer": handle_transfer
                    }

                    # Execute the handler function for the selected action
                    if action in action_handlers:
                        result = action_handlers[action]()
                        if result == "break":
                            break
                    else:
                        print(f"Unknown action: {action}")
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print_response("Error", f"An error occurred: {str(e)}")

            # Pause before showing menu again
            input("\nPress Enter to continue...")
