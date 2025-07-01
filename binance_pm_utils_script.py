import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))
from rest.binance_PM_addon import BinancePmTestWrapper


class BinancePmUtils:
    """Utility class for interacting with Binance Portfolio Margin API."""

    def __init__(self, api_key: str, api_secret: str, pm_host: str = "https://papi.binance.com",
                 default_symbol: str = "BTCUSDT", default_quantity: float = 0.001):
        """
        Initialize the Binance PM Utils.

        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            pm_host: Portfolio Margin API host URL
            default_symbol: Default trading symbol
            default_quantity: Default trading quantity
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.pm_host = pm_host
        self.default_symbol = default_symbol
        self.default_quantity = default_quantity

        self.client = BinancePmTestWrapper(
            pm_host=self.pm_host,
            api_key=self.api_key,
            api_secret=self.api_secret,
            default_symbol=self.default_symbol,
            default_quantity=self.default_quantity
        )

    def get_listen_key(self) -> dict:
        """Get a listen key for user data streams."""
        return self.client.client.create_listenKey()

    def get_spot_balance(self) -> Dict[str, Any]:
        """Get spot account balance."""
        return self.client.get_spot_balance()

    def get_spot_price(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get spot price for a symbol."""
        return self.client.get_spot_price(symbol=symbol)

    def get_spot_acct_balance(self) -> Dict[str, Any]:
        """Get spot account balance."""
        return self.client.get_spot_acct_balance()

    def get_um_position(self) -> Dict[str, Any]:
        """Get UM futures positions."""
        return self.client.get_fut_position()

    def get_spot_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get open spot orders."""
        return self.client.get_spot_open_orders(symbol=symbol)

    def get_um_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get open UM futures orders."""
        return self.client.get_fut_open_orders(symbol=symbol)

    def get_spot_fee(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get spot commission rates.

        Args:
            symbol: Optional symbol to get commission rates for
        """
        return self.client.get_spot_comms_rate(symbol=symbol)

    def get_um_fee(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get UM futures commission rates.

        Args:
            symbol: Optional symbol to get commission rates for
        """
        return self.client.get_um_comms_rate(symbol=symbol)

    def get_account_config(self) -> Dict[str, Any]:
        """Get account configuration."""
        return self.client.get_account_config()

    def get_spot_config(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get spot market configuration.

        Args:
            symbol: Optional symbol to get configuration for
        """
        return self.client.get_spot_config(symbol=symbol)

    def get_perp_market_config(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get perpetual futures market configuration.

        Args:
            symbol: Optional symbol to get configuration for
        """
        return self.client.get_perp_market_config(symbol=symbol)

    def buy_spot(self, symbol: Optional[str] = None, price: Optional[float] = None,
                quantity: Optional[float] = None, order_type: str = 'LIMIT',
                time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a spot buy order.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            price: Order price (required for LIMIT orders)
            quantity: Order quantity (defaults to default_quantity if None)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.buy_spot(symbol=symbol, price=price, quantity=quantity,
                                   order_type=order_type, time_in_force=time_in_force)

    def sell_spot(self, symbol: Optional[str] = None, price: Optional[float] = None,
                 quantity: Optional[float] = None, order_type: str = 'LIMIT',
                 time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Place a spot sell order.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            price: Order price (required for LIMIT orders)
            quantity: Order quantity (defaults to default_quantity if None)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.sell_spot(symbol=symbol, price=price, quantity=quantity,
                                    order_type=order_type, time_in_force=time_in_force)

    def open_long_fut(self, symbol: Optional[str] = None, quantity: Optional[float] = None,
                     price: Optional[float] = None, order_type: str = 'LIMIT',
                     time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Open a long futures position.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            quantity: Order quantity (defaults to default_quantity if None)
            price: Order price (required for LIMIT orders)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.open_long_fut(symbol=symbol, qty=quantity, price=price,
                                        order_type=order_type, time_in_force=time_in_force)

    def close_long_fut(self, symbol: Optional[str] = None, quantity: Optional[float] = None,
                      price: Optional[float] = None, order_type: str = 'LIMIT',
                      time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Close a long futures position.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            quantity: Order quantity (defaults to default_quantity if None)
            price: Order price (required for LIMIT orders)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.close_long_fut(symbol=symbol, qty=quantity, price=price,
                                         order_type=order_type, time_in_force=time_in_force)

    def open_short_fut(self, symbol: Optional[str] = None, quantity: Optional[float] = None,
                      price: Optional[float] = None, order_type: str = 'LIMIT',
                      time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Open a short futures position.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            quantity: Order quantity (defaults to default_quantity if None)
            price: Order price (required for LIMIT orders)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.open_short_fut(symbol=symbol, qty=quantity, price=price,
                                         order_type=order_type, time_in_force=time_in_force)

    def close_short_fut(self, symbol: Optional[str] = None, quantity: Optional[float] = None,
                       price: Optional[float] = None, order_type: str = 'LIMIT',
                       time_in_force: str = 'GTC') -> Dict[str, Any]:
        """
        Close a short futures position.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            quantity: Order quantity (defaults to default_quantity if None)
            price: Order price (required for LIMIT orders)
            order_type: Order type ('LIMIT' or 'MARKET')
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')

        Returns:
            Dict containing order response
        """
        if symbol is None:
            symbol = self.default_symbol
        if quantity is None:
            quantity = self.default_quantity
        return self.client.close_short_fut(symbol=symbol, qty=quantity, price=price,
                                          order_type=order_type, time_in_force=time_in_force)

    def cancel_spot_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel all open spot orders for a symbol.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)

        Returns:
            Dict containing cancellation response
        """
        if symbol is None:
            symbol = self.default_symbol
        return self.client.cancel_spot_open_orders(symbol=symbol)

    def cancel_fut_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel all open futures orders for a symbol.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)

        Returns:
            Dict containing cancellation response
        """
        if symbol is None:
            symbol = self.default_symbol
        return self.client.cancel_fut_open_orders(symbol=symbol)

    def get_spot_trades(self, symbol: Optional[str] = None, order_id: Optional[int] = None,
                       start_time: Optional[int] = None, end_time: Optional[int] = None,
                       from_id: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get spot trade history.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            order_id: Filter trades by order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            from_id: Trade ID to fetch from
            limit: Maximum number of trades to return

        Returns:
            Dict containing trade history
        """
        if symbol is None:
            symbol = self.default_symbol
        return self.client.get_spot_trades(
            symbol=symbol,
            orderId=order_id,
            startTime=start_time,
            endTime=end_time,
            fromId=from_id,
            limit=limit
        )

    def get_um_trades(self, symbol: Optional[str] = None, order_id: Optional[int] = None,
                     start_time: Optional[int] = None, end_time: Optional[int] = None,
                     from_id: Optional[int] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get UM futures trade history.

        Args:
            symbol: Trading symbol (defaults to default_symbol if None)
            order_id: Filter trades by order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            from_id: Trade ID to fetch from
            limit: Maximum number of trades to return

        Returns:
            Dict containing trade history
        """
        if symbol is None:
            symbol = self.default_symbol
        return self.client.get_um_trades(
            symbol=symbol,
            orderId=order_id,
            startTime=start_time,
            endTime=end_time,
            fromId=from_id,
            limit=limit
        )

    def transfer_usdt_to_PM(self, amount: float) -> Dict[str, Any]:
        """Transfer USDT from spot to PM account."""
        return self.client.send_usdt_from_spot_to_pm(amount)

    def transfer_usdt_to_spot(self, amount: float) -> Dict[str, Any]:
        """Transfer USDT from PM to spot account."""
        return self.client.transfer_to_spot("USDT", amount)

    def transfer_asset_to_spot(self, asset: str, amount: float) -> Dict[str, Any]:
        """Transfer an asset from PM to spot account."""
        return self.client.transfer_to_spot(asset, amount)

    def get_pm_balance(self) -> Dict[str, Any]:
        """Get Portfolio Margin account balance."""
        return self.client.get_pm_balance()


class BinancePmUtilsApp:
    """Application class for Binance Portfolio Margin utilities."""

    def __init__(self):
        """Initialize the application."""
        self.accounts: Dict[str, BinancePmUtils] = {}
        self.current_account: Optional[BinancePmUtils] = None
        self.current_account_name: Optional[str] = None
        self.separator = "=" * 30

        # Define menu options as a dictionary mapping option number to (method_name, description)
        self.menu_options = {
            "1": ("get_pm_balance", "Get PM balance"),
            "2": ("get_um_position", "Get um position"),
            "3": ("get_spot_open_orders", "Get spot open orders"),
            "4": ("get_um_open_orders", "Get um open orders"),
            "5": ("get_spot_fee", "Get spot fee"),
            "6": ("get_um_fee", "Get um fee"),
            "7": ("get_account_config", "Get account config"),
            "8": ("get_spot_config", "Get spot market config"),
            "9": ("get_perp_market_config", "Get perp market config"),
            "10": ("buy_spot", "Buy spot"),
            "11": ("sell_spot", "Sell spot"),
            "12": ("open_long_fut", "Open long futures position"),
            "13": ("close_long_fut", "Close long futures position"),
            "14": ("open_short_fut", "Open short futures position"),
            "15": ("close_short_fut", "Close short futures position"),
            "16": ("cancel_spot_open_orders", "Cancel spot open orders"),
            "17": ("cancel_fut_open_orders", "Cancel futures open orders"),
            "18": ("get_spot_trades", "Get spot trades history"),
            "19": ("get_um_trades", "Get UM futures trades history"),
            "20": ("transfer_usdt_to_pm", "Transfer usdt to PM"),
            "21": ("transfer_usdt_to_spot", "Transfer usdt to spot"),
            "22": ("transfer_asset_to_spot", "Transfer asset to spot"),
            "23": ("get_spot_price", "Get spot price"),
            "24": ("get_spot_balance", "Get spot acct balance"),
            "25": ("get_listen_key", "Get listen key"),
            "0": ("exit_app", "Exit")
        }

    def load_accounts(self) -> None:
        """Load accounts from .keys.yaml file."""
        keys_path = Path(__file__).parent / '.keys.yaml'

        try:
            with open(keys_path, 'r') as f:
                keys = yaml.safe_load(f)

            for name, key_data in keys['binance'].items():
                try:
                    api_key = key_data['api_key']
                    api_secret = key_data['api_secret']
                    self.accounts[name] = BinancePmUtils(api_key, api_secret)
                except KeyError:
                    print(f"Missing API key or secret for account: {name}")

            if not self.accounts:
                raise ValueError("No valid accounts found in .keys.yaml")

        except FileNotFoundError:
            raise ValueError(f"Keys file not found at {keys_path}")
        except KeyError:
            raise ValueError("No 'binance' section found in .keys.yaml")

    def select_account(self) -> bool:
        """
        Prompt user to select an account by number.

        Returns:
            bool: True if account was selected successfully, False otherwise
        """
        while True:
            # Get account names and display with numbers
            account_names = list(self.accounts.keys())
            print("Available accounts:")
            for i, name in enumerate(account_names, 1):
                print(f"{i}. {name}")
            print(self.separator)

            user_input = input("Enter account number (or 'exit' to quit): ")

            if user_input.lower() == 'exit':
                return False

            try:
                # Convert input to integer and check if it's a valid account number
                account_idx = int(user_input) - 1
                if 0 <= account_idx < len(account_names):
                    selected_account = account_names[account_idx]
                    self.current_account = self.accounts[selected_account]
                    self.current_account_name = selected_account
                    return True
                else:
                    print(f"Invalid account number. Please enter a number between 1 and {len(account_names)}\n{self.separator}")
            except ValueError:
                print(f"Invalid input. Please enter a number or 'exit'\n{self.separator}")

    def display_menu(self) -> None:
        """Display the menu options."""
        print(f"Selected account: {self.current_account_name}")
        print(self.separator)
        print("What would you like to do?")
        print(self.separator)

        # Display menu options from the dictionary
        for option_num, (_, description) in self.menu_options.items():
            print(f"{option_num}. {description}")

        print(self.separator)

    def process_choice(self, choice: str) -> bool:
        """
        Process the user's menu choice.

        Args:
            choice: The user's choice from the menu

        Returns:
            bool: True to continue, False to exit
        """
        if choice not in self.menu_options:
            print(f"Invalid choice\n{self.separator}")
            return True

        method_name, _ = self.menu_options[choice]

        # Call the appropriate method
        method = getattr(self, method_name, None)
        if method:
            try:
                method()
                print(f"\n{self.separator}")
            except Exception as e:
                print(f"Error: {e}\n{self.separator}")
        else:
            print(f"Method {method_name} not implemented\n{self.separator}")

        return choice != "0"  # Continue unless choice is "0" (exit)

    def print_result(self, result: Any) -> None:
        """Print the result of an operation with proper formatting."""
        print(result)
        print(f"\n{self.separator}")

    # Menu option methods
    def get_pm_balance(self) -> None:
        """Get and display PM balance."""
        result = self.current_account.get_pm_balance()
        self.print_result(result)

    def get_um_position(self) -> None:
        """Get and display UM position."""
        result = self.current_account.get_um_position()
        self.print_result(result)

    def get_spot_open_orders(self) -> None:
        """Get and display spot open orders."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_spot_open_orders(symbol=symbol)
        self.print_result(result)

    def get_listen_key(self) -> None:
        """Get and display a listen key."""
        result = self.current_account.get_listen_key()
        self.print_result(result)

    def get_um_open_orders(self) -> None:
        """Get and display UM open orders."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_um_open_orders(symbol=symbol)
        self.print_result(result)

    def get_spot_fee(self) -> None:
        """Get and display spot fee."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_spot_fee(symbol=symbol)
        self.print_result(result)

    def get_um_fee(self) -> None:
        """Get and display UM fee."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_um_fee(symbol=symbol)
        self.print_result(result)

    def get_account_config(self) -> None:
        """Get and display account config."""
        result = self.current_account.get_account_config()
        self.print_result(result)

    def transfer_usdt_to_pm(self) -> None:
        """Transfer USDT to PM account."""
        try:
            amount = float(input("Enter amount: "))
            result = self.current_account.transfer_usdt_to_PM(amount)
            self.print_result(result)
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

    def transfer_usdt_to_spot(self) -> None:
        """Transfer USDT to spot account."""
        try:
            amount = float(input("Enter amount: "))
            result = self.current_account.transfer_usdt_to_spot(amount)
            self.print_result(result)
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

    def transfer_asset_to_spot(self) -> None:
        """Transfer asset to spot account."""
        try:
            asset = input("Enter asset: ")
            amount = float(input("Enter amount: "))
            result = self.current_account.transfer_asset_to_spot(asset, amount)
            self.print_result(result)
        except ValueError:
            print("Invalid amount. Please enter a valid number.")

    def get_spot_price(self) -> None:
        """Get and display spot price."""
        symbol = input("Enter symbol: ")
        result = self.current_account.get_spot_price(symbol)
        self.print_result(result)

    def get_spot_balance(self) -> None:
        """Get and display spot account balance."""
        result = self.current_account.get_spot_balance()
        self.print_result(result)

    def get_spot_config(self) -> None:
        """Get and display spot market configuration."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_spot_config(symbol=symbol)
        self.print_result(result)

    def get_perp_market_config(self) -> None:
        """Get and display perpetual futures market configuration."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.get_perp_market_config(symbol=symbol)
        self.print_result(result)

    def buy_spot(self) -> None:
        """Place a spot buy order."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.buy_spot(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def sell_spot(self) -> None:
        """Place a spot sell order."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.sell_spot(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def open_long_fut(self) -> None:
        """Open a long futures position."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.open_long_fut(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def close_long_fut(self) -> None:
        """Close a long futures position."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.close_long_fut(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def open_short_fut(self) -> None:
        """Open a short futures position."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.open_short_fut(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def close_short_fut(self) -> None:
        """Close a short futures position."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            quantity_input = input("Enter quantity (or press Enter for default): ")
            quantity = float(quantity_input) if quantity_input else None

            order_type = input("Enter order type (LIMIT/MARKET) [default: LIMIT]: ").upper()
            order_type = order_type if order_type in ["LIMIT", "MARKET"] else "LIMIT"

            price = None
            if order_type == "LIMIT":
                price_input = input("Enter price: ")
                if not price_input:
                    print("Price is required for LIMIT orders")
                    return
                price = float(price_input)

            time_in_force = input("Enter time in force (GTC/IOC/FOK) [default: GTC]: ").upper()
            time_in_force = time_in_force if time_in_force in ["GTC", "IOC", "FOK"] else "GTC"

            result = self.current_account.close_short_fut(
                symbol=symbol,
                price=price,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    def cancel_spot_open_orders(self) -> None:
        """Cancel all open spot orders for a symbol."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.cancel_spot_open_orders(symbol=symbol)
        self.print_result(result)

    def cancel_fut_open_orders(self) -> None:
        """Cancel all open futures orders for a symbol."""
        symbol = input("Enter symbol (or press Enter for default): ")
        symbol = symbol if symbol else None
        result = self.current_account.cancel_fut_open_orders(symbol=symbol)
        self.print_result(result)

    def get_spot_trades(self) -> None:
        """Get and display spot trade history."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            order_id_input = input("Enter order ID (optional): ")
            order_id = int(order_id_input) if order_id_input else None

            start_time_input = input("Enter start time in milliseconds (optional): ")
            start_time = int(start_time_input) if start_time_input else None

            end_time_input = input("Enter end time in milliseconds (optional): ")
            end_time = int(end_time_input) if end_time_input else None

            from_id_input = input("Enter from ID (optional): ")
            from_id = int(from_id_input) if from_id_input else None

            limit_input = input("Enter limit (optional): ")
            limit = int(limit_input) if limit_input else None

            result = self.current_account.get_spot_trades(
                symbol=symbol,
                order_id=order_id,
                start_time=start_time,
                end_time=end_time,
                from_id=from_id,
                limit=limit
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers for numeric fields.")

    def get_um_trades(self) -> None:
        """Get and display UM futures trade history."""
        try:
            symbol = input("Enter symbol (or press Enter for default): ")
            symbol = symbol if symbol else None

            order_id_input = input("Enter order ID (optional): ")
            order_id = int(order_id_input) if order_id_input else None

            start_time_input = input("Enter start time in milliseconds (optional): ")
            start_time = int(start_time_input) if start_time_input else None

            end_time_input = input("Enter end time in milliseconds (optional): ")
            end_time = int(end_time_input) if end_time_input else None

            from_id_input = input("Enter from ID (optional): ")
            from_id = int(from_id_input) if from_id_input else None

            limit_input = input("Enter limit (optional): ")
            limit = int(limit_input) if limit_input else None

            result = self.current_account.get_um_trades(
                symbol=symbol,
                order_id=order_id,
                start_time=start_time,
                end_time=end_time,
                from_id=from_id,
                limit=limit
            )
            self.print_result(result)
        except ValueError:
            print("Invalid input. Please enter valid numbers for numeric fields.")

    def exit_app(self) -> None:
        """Exit the application."""
        print("Exiting application...")

    def run(self) -> None:
        """Run the main application loop."""
        try:
            # Load accounts from .keys.yaml
            self.load_accounts()

            # Select an account
            if not self.select_account():
                print("Exiting application...")
                return

            # Main menu loop
            while True:
                self.display_menu()
                choice = input("Enter choice: ")

                if not self.process_choice(choice):
                    break

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    app = BinancePmUtilsApp()
    app.run()