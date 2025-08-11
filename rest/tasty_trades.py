import requests
import json
import time
from datetime import datetime, timedelta

class TastytradeAPIError(Exception):
    """Custom exception for Tastytrade API errors."""
    pass

class _BaseClient:
    """
    Base client for shared functionality across API categories.
    Handles HTTP requests, authorization, and error parsing.
    """
    def __init__(self, session, base_url, user_agent):
        """
        Initializes the base client.

        Args:
            session (requests.Session): The authenticated requests session.
            base_url (str): The base URL for API requests (sandbox or production).
            user_agent (str): The User-Agent string for requests.
        """
        self.session = session
        self.base_url = base_url
        self.user_agent = user_agent

    def _request(self, method, path, **kwargs):
        """
        Makes an HTTP request to the Tastytrade API.

        Args:
            method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            path (str): The API endpoint path.
            **kwargs: Additional keyword arguments for requests.request.
                      'params' for query parameters, 'json' for request body.

        Returns:
            dict: JSON response from the API.

        Raises:
            TastytradeAPIError: If the API returns an error.
        """
        url = f"{self.base_url}{path}"
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self.user_agent
        headers['Content-Type'] = 'application/json' # Most Tastytrade APIs expect JSON

        # Convert Pythonic underscore keys in params to dasherized for API
        if 'params' in kwargs and kwargs['params'] is not None:
            kwargs['params'] = {k.replace('_', '-'): v for k, v in kwargs['params'].items()}

        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', str(e))
            except json.JSONDecodeError:
                error_message = e.response.text
            raise TastytradeAPIError(f"API Error ({e.response.status_code}): {error_message}") from e
        except requests.exceptions.RequestException as e:
            raise TastytradeAPIError(f"Network or request error: {e}") from e

class _AuthClient(_BaseClient):
    """
    Handles authentication-related API endpoints.
    """
    def __init__(self, session, base_url, user_agent, api_key, api_secret):
        super().__init__(session, base_url, user_agent)
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None

    def get_oauth_token(self):
        """
        Obtains an OAuth2 access token using client credentials.
        Assumes client_id = api_key and client_secret = api_secret.
        """
        token_url = f"{self.base_url}/oauth/token"
        headers = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json'
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
            # Additional OAuth2 parameters like 'scope' might be needed
            # depending on Tastytrade's specific OAuth2 implementation.
            # Consult their full OAuth2 guide if this basic setup fails.
        }
        try:
            response = requests.post(token_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token') # Refresh token might not be present for client_credentials
            expires_in = data.get('expires_in', 3600) # Default to 1 hour if not provided
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60) # Refresh 60 seconds before actual expiry

            if not self.access_token:
                raise TastytradeAPIError("Failed to obtain access token: 'access_token' not found in response.")

            # Update the session's Authorization header
            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            print("Successfully obtained new OAuth2 access token.")
            return True
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('error', {}).get('message', str(e))
            except json.JSONDecodeError:
                error_message = e.response.text
            raise TastytradeAPIError(f"OAuth Token Error ({e.response.status_code}): {error_message}") from e
        except requests.exceptions.RequestException as e:
            raise TastytradeAPIError(f"Network or request error during token acquisition: {e}") from e

    def refresh_oauth_token(self):
        """
        Refreshes the OAuth2 access token using the refresh token.
        Note: Client credentials flow typically doesn't involve refresh tokens.
        This method is more relevant for authorization code flow.
        If refresh_token is not available, it will try to get a new token.
        """
        if not self.refresh_token:
            print("No refresh token available. Attempting to get a new access token.")
            return self.get_oauth_token()

        token_url = f"{self.base_url}/oauth/token"
        headers = {
            'User-Agent': self.user_agent,
            'Content-Type': 'application/json'
        }
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.api_key, # Client ID might be required for refresh
            "client_secret": self.api_secret # Client Secret might be required for refresh
        }
        try:
            response = requests.post(token_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token', self.refresh_token) # Refresh token might be new or same
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            if not self.access_token:
                raise TastytradeAPIError("Failed to refresh access token: 'access_token' not found in response.")

            self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            print("Successfully refreshed OAuth2 access token.")
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Failed to refresh token, attempting to get a new one. Error: {e.response.text}")
            return self.get_oauth_token() # Fallback to getting a new token if refresh fails
        except requests.exceptions.RequestException as e:
            raise TastytradeAPIError(f"Network or request error during token refresh: {e}") from e

    def ensure_token_valid(self):
        """
        Checks if the current access token is valid and refreshes it if necessary.
        """
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            print("Access token expired or not present. Attempting to refresh/obtain new token.")
            if self.refresh_token:
                return self.refresh_oauth_token()
            else:
                return self.get_oauth_token()
        return True

class Customer(_BaseClient):
    """
    API endpoints related to customer information.
    """
    def get_customer_information(self):
        """
        Retrieves information about the authenticated customer.
        GET /customers/me
        """
        return self._request('GET', '/customers/me')

    def get_customer_accounts(self):
        """
        Retrieves a list of accounts associated with the authenticated customer.
        This is functionally similar to /accounts but explicitly under the customer path.
        GET /customers/me/accounts
        """
        return self._request('GET', '/customers/me/accounts')

    def get_customer_account(self, account_number):
        """
        Retrieves details for a specific account associated with the customer.
        GET /customers/me/accounts/{account_number}
        """
        return self._request('GET', f'/customers/me/accounts/{account_number}')

class Accounts(_BaseClient):
    """
    API endpoints related to user accounts.
    """
    def get_accounts(self):
        """
        Lists all accounts associated with the authenticated user.
        GET /accounts
        """
        return self._request('GET', '/accounts')

    def get_account_balances(self, account_number):
        """
        Retrieves balance information for a specific account.
        GET /accounts/{account_number}/balances
        """
        return self._request('GET', f'/accounts/{account_number}/balances')

    def list_account_balance_snapshots(self, account_number, snapshot_date=None, time_of_day=None):
        """
        Lists account balance snapshots for a specific account.
        GET /accounts/{account_number}/balance-snapshots

        Args:
            account_number (str): The account number.
            snapshot_date (str, optional): Date of desired balance snapshot (YYYY-MM-DD).
            time_of_day (str, optional): Snapshot time of day ('BOD' or 'EOD'). Required if snapshot_date is provided.
        """
        params = {}
        if snapshot_date:
            params['snapshot_date'] = snapshot_date
        if time_of_day:
            params['time_of_day'] = time_of_day
        return self._request('GET', f'/accounts/{account_number}/balance-snapshots', params=params)


    def get_account_positions(self, account_number):
        """
        Retrieves positions for a specific account.
        GET /accounts/{account_number}/positions
        """
        return self._request('GET', f'/accounts/{account_number}/positions')

    def list_transactions(self, account_number, **params):
        """
        Lists transactions for a specific account.
        GET /accounts/{account_number}/transactions
        Optional params: sort, type, sub_type, start_date, end_date, instrument_type, symbol, underlying_symbol, action, partition_key, futures_symbol, start_at, end_at.
        """
        return self._request('GET', f'/accounts/{account_number}/transactions', params=params)

    def get_transaction(self, account_number, transaction_id):
        """
        Retrieves a specific transaction by ID for an account.
        GET /accounts/{account_number}/transactions/{id}
        """
        return self._request('GET', f'/accounts/{account_number}/transactions/{transaction_id}')

    def get_total_fees(self, account_number, date=None):
        """
        Retrieves total fees for a specific account on a given date.
        GET /accounts/{account_number}/transactions/total-fees

        Args:
            account_number (str): The account number.
            date (str, optional): The date to get fees for (YYYY-MM-DD). Defaults to today.
        """
        params = {}
        if date:
            params['date'] = date
        return self._request('GET', f'/accounts/{account_number}/transactions/total-fees', params=params)

class Markets(_BaseClient):
    """
    API endpoints related to market data and instruments.
    """
    def list_equities(self, **params):
        """
        Lists equities.
        GET /instruments/equities
        Optional params: symbol[] (array of strings), lendability, is_index, is_etf.
        """
        return self._request('GET', '/instruments/equities', params=params)

    def list_active_equities(self, **params):
        """
        Lists active equities.
        GET /instruments/equities/active
        Optional params: lendability, per_page, page_offset.
        """
        return self._request('GET', '/instruments/equities/active', params=params)

    def get_equity(self, symbol):
        """
        Gets details for a specific equity.
        GET /instruments/equities/{symbol}
        """
        return self._request('GET', f'/instruments/equities/{symbol}')

    def list_nested_option_chains(self, underlying_symbol):
        """
        Lists nested option chains for an underlying symbol.
        GET /option-chains/{underlying_symbol}/nested
        """
        return self._request('GET', f'/option-chains/{underlying_symbol}/nested')

    def list_detailed_option_chains(self, underlying_symbol):
        """
        Lists detailed option chains for an underlying symbol.
        GET /option-chains/{underlying_symbol}/detailed
        """
        return self._request('GET', f'/option-chains/{underlying_symbol}/detailed')

    def list_equity_options(self, **params):
        """
        Lists equity options.
        GET /instruments/equity-options
        Optional params: symbol[] (array of strings), underlying_symbol, expiration_date, strike_price, option_type.
        """
        return self._request('GET', '/instruments/equity-options', params=params)

    def get_equity_option(self, symbol):
        """
        Gets details for a specific equity option.
        GET /instruments/equity-options/{symbol}
        """
        return self._request('GET', f'/instruments/equity-options/{symbol}')

    def list_futures(self, **params):
        """
        Lists futures contracts.
        GET /instruments/futures
        Optional params: symbol[] (array of strings), product_code, month, year.
        """
        return self._request('GET', '/instruments/futures', params=params)

    def get_future(self, symbol):
        """
        Gets details for a specific future contract.
        GET /instruments/futures/{symbol}
        """
        return self._request('GET', f'/instruments/futures/{symbol}')

    def list_future_products(self):
        """
        Lists all available future products.
        GET /instruments/future-products
        """
        return self._request('GET', '/instruments/future-products')

    def list_future_options(self, **params):
        """
        Lists future options.
        GET /instruments/future-options
        Optional params: symbol[] (array of strings), underlying_symbol, expiration_date, strike_price, option_type.
        """
        return self._request('GET', '/instruments/future-options', params=params)

    def get_future_option(self, symbol):
        """
        Gets details for a specific future option.
        GET /instruments/future-options/{symbol}
        """
        return self._request('GET', f'/instruments/future-options/{symbol}')

    def list_future_option_products(self):
        """
        Lists all available future option products.
        GET /instruments/future-option-products
        """
        return self._request('GET', '/instruments/future-option-products')

    def list_cryptocurrencies(self):
        """
        Lists all available cryptocurrencies.
        GET /instruments/cryptocurrencies
        """
        return self._request('GET', '/instruments/cryptocurrencies')

    def get_cryptocurrency(self, symbol):
        """
        Gets details for a specific cryptocurrency.
        GET /instruments/cryptocurrencies/{symbol}
        """
        return self._request('GET', f'/instruments/cryptocurrencies/{symbol}')

    def list_warrants(self, **params):
        """
        Lists warrants.
        GET /instruments/warrants
        Optional params: symbol[] (array of strings), underlying_symbol, expiration_date, strike_price.
        """
        return self._request('GET', '/instruments/warrants', params=params)

    def get_warrant(self, symbol):
        """
        Gets details for a specific warrant.
        GET /instruments/warrants/{symbol}
        """
        return self._request('GET', f'/instruments/warrants/{symbol}')

    def list_quantity_decimal_precisions(self):
        """
        Lists quantity decimal precisions.
        GET /instruments/quantity-decimal-precisions
        """
        return self._request('GET', '/instruments/quantity-decimal-precisions')

class Orders(_BaseClient):
    """
    API endpoints related to order management.
    """
    def submit_order(self, account_number, order_data):
        """
        Submits a new order for a specific account.
        POST /accounts/{account_number}/orders
        order_data should be a dictionary conforming to Tastytrade's order submission schema.
        """
        return self._request('POST', f'/accounts/{account_number}/orders', json=order_data)

    def get_orders(self, account_number, **params):
        """
        Retrieves a list of orders for a specific account.
        GET /accounts/{account_number}/orders
        Optional params: status, underlying_symbol, etc.
        """
        return self._request('GET', f'/accounts/{account_number}/orders', params=params)

    def get_order(self, account_number, order_id):
        """
        Retrieves details of a specific order by ID.
        GET /accounts/{account_number}/orders/{id}
        """
        return self._request('GET', f'/accounts/{account_number}/orders/{order_id}')

    def cancel_order(self, account_number, order_id):
        """
        Cancels an open order.
        DELETE /accounts/{account_number}/orders/{id}
        """
        return self._request('DELETE', f'/accounts/{account_number}/orders/{order_id}')

class Sessions(_BaseClient):
    """
    API endpoints related to user sessions (login/logout).
    Note: OAuth2 is the recommended authentication method.
    These endpoints are primarily for session token based authentication.
    """
    def destroy_session(self):
        """
        Destroys the current session (logs out).
        DELETE /sessions
        """
        return self._request('DELETE', '/sessions')

class MarketsWs:
    """
    Placeholder for WebSocket API endpoints related to streaming market data.
    Requires a separate WebSocket client implementation (e.g., using 'websockets' library).
    """
    def __init__(self, api_quote_token=None, base_ws_url="wss://tasty-openapi-ws.dxfeed.com/realtime"):
        self.api_quote_token = api_quote_token
        self.base_ws_url = base_ws_url
        print("MarketsWs requires a WebSocket client implementation (e.g., using 'websockets').")
        print("To get an API quote token, you would typically use GET /api-quote-tokens via HTTP API.")

    def subscribe_quotes(self, symbols):
        """
        Example: Subscribes to real-time quotes for given symbols.
        This method would involve WebSocket communication.
        """
        print(f"Subscribing to quotes for {symbols} via WebSocket (not implemented).")
        # Example: self.ws_client.send(json.dumps({"type": "subscribe", "symbols": symbols}))

class AccountsWs:
    """
    Placeholder for WebSocket API endpoints related to streaming account updates.
    Requires a separate WebSocket client implementation.
    """
    def __init__(self, base_ws_url="wss://api.tastyworks.com/accounts-streamer/v1/accounts"):
        self.base_ws_url = base_ws_url
        print("AccountsWs requires a WebSocket client implementation (e.g., using 'websockets').")

    def subscribe_account_updates(self, account_numbers):
        """
        Example: Subscribes to real-time account updates for given account numbers.
        This method would involve WebSocket communication.
        """
        print(f"Subscribing to account updates for {account_numbers} via WebSocket (not implemented).")
        # Example: self.ws_client.send(json.dumps({"type": "subscribe", "accounts": account_numbers}))


class TastyTradesApi:
    """
    Main class for interacting with the Tastytrade API.
    Provides access to various API categories through sub-classes.
    """
    def __init__(self, api_key, api_secret, sandbox=True, user_agent="tastytrade-api-client/1.0", **kwargs):
        """
        Initializes the TastyTradesApi client.

        Args:
            api_key (str): Your Tastytrade API key (client ID for OAuth).
            api_secret (str): Your Tastytrade API secret (client secret for OAuth).
            sandbox (bool): If True, uses the sandbox environment. Otherwise, uses production.
                            Defaults to True.
            user_agent (str): Custom User-Agent string for API requests.
                              Defaults to "tastytrade-api-client/1.0".
            **kwargs: Additional keyword arguments (currently not used, but for future expansion).
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
        self.user_agent = user_agent

        self.base_url = "https://api.cert.tastyworks.com" if sandbox else "https://api.tastyworks.com"
        self.session = requests.Session()

        # Initialize the internal authentication client
        self._auth_client = _AuthClient(self.session, self.base_url, self.user_agent, self.api_key, self.api_secret)

        # Authenticate and obtain the initial access token
        self._auth_client.get_oauth_token()

        # Initialize sub-classes with the authenticated session
        self.customer = Customer(self.session, self.base_url, self.user_agent)
        self.accounts = Accounts(self.session, self.base_url, self.user_agent)
        self.markets = Markets(self.session, self.base_url, self.user_agent)
        self.orders = Orders(self.session, self.base_url, self.user_agent)
        self.sessions = Sessions(self.session, self.base_url, self.user_agent)

        # WebSocket clients (placeholders - require separate implementation)
        # To use these, you'd typically first get an API quote token via HTTP API.
        # self.markets_ws = MarketsWs(api_quote_token="YOUR_API_QUOTE_TOKEN")
        # self.accounts_ws = AccountsWs()


    def close_session(self):
        """
        Closes the underlying requests session.
        Good practice to call when done with the API.
        """
        self.session.close()
        print("TastyTradesApi session closed.")

# Example Usage:
if __name__ == "__main__":
    # Replace with your actual API Key and Secret (from Tastytrade developer portal)
    # For sandbox, you'll need to register an OAuth client in the sandbox environment.
    # If the OAuth client credentials flow is not working, you might need to use
    # username/password for session token authentication (POST /sessions)
    # and adjust the _AuthClient accordingly.
    YOUR_API_KEY = "YOUR_TASTYTRADE_API_KEY" # Replace with your actual API Key
    YOUR_API_SECRET = "YOUR_TASTYTRADE_API_SECRET" # Replace with your actual API Secret

    # --- IMPORTANT ---
    # The OAuth client credentials flow requires you to register an OAuth client
    # with Tastytrade to get a client_id (API Key) and client_secret (API Secret).
    # If you haven't done this, the authentication will fail.
    # If you only have a username/password, you'd need to modify the _AuthClient
    # to use the /sessions endpoint for session token authentication.
    # --- IMPORTANT ---

    try:
        # Initialize the API client for the sandbox environment
        api = TastyTradesApi(api_key=YOUR_API_KEY, api_secret=YOUR_API_SECRET, sandbox=True)
        print("TastyTradesApi initialized successfully for sandbox.")

        # Example: Get current customer information
        print("\nFetching customer information...")
        customer_info = api.customer.get_customer_information()
        print(f"Customer Info: {json.dumps(customer_info, indent=2)}")

        # Example: Get current user's accounts
        print("\nFetching accounts...")
        accounts_data = api.accounts.get_accounts()
        if accounts_data and accounts_data.get('data', {}).get('items'):
            print("Accounts fetched:")
            for account in accounts_data['data']['items']:
                account_number = account['account-number']
                print(f"  Account Number: {account_number}, Account Type: {account['account-type']}")

                # Example: Get balances for the first account
                print(f"\nFetching balances for account: {account_number}")
                balances = api.accounts.get_account_balances(account_number)
                print(f"  Balances: {json.dumps(balances, indent=2)}")

                # Example: List account balance snapshots (e.g., EOD for a specific date)
                # from datetime import date
                # snapshot_date_example = (date.today() - timedelta(days=1)).isoformat() # Yesterday
                # print(f"\nFetching EOD balance snapshot for account {account_number} on {snapshot_date_example}")
                # snapshots = api.accounts.list_account_balance_snapshots(account_number, snapshot_date=snapshot_date_example, time_of_day='EOD')
                # print(f"  Balance Snapshots: {json.dumps(snapshots, indent=2)}")

                # Example: Get positions for the first account
                print(f"\nFetching positions for account: {account_number}")
                positions = api.accounts.get_account_positions(account_number)
                print(f"  Positions: {json.dumps(positions, indent=2)}")

                break # Process only the first account for demonstration

        else:
            print("No accounts found or unexpected response structure.")

        # Example: List equities (e.g., SPY and AAPL)
        print("\nFetching equities (SPY, AAPL)...")
        equities = api.markets.list_equities(symbol=['SPY', 'AAPL'])
        print(f"Equities: {json.dumps(equities, indent=2)}")

        # Example: List active equities
        print("\nFetching active equities (first 5)...")
        active_equities = api.markets.list_active_equities(per_page=5)
        print(f"Active Equities: {json.dumps(active_equities, indent=2)}")

        # Example: Get nested option chain for SPY
        print("\nFetching nested option chain for SPY...")
        option_chain = api.markets.list_nested_option_chains('SPY')
        print(f"Option Chain for SPY (first expiration): {json.dumps(option_chain['data']['items'][0] if option_chain and option_chain.get('data', {}).get('items') else 'No data', indent=2)}")

        # Example: List cryptocurrencies
        print("\nFetching cryptocurrencies...")
        cryptos = api.markets.list_cryptocurrencies()
        print(f"Cryptocurrencies: {json.dumps(cryptos, indent=2)}")

        # Example: Destroy session (logout)
        # print("\nDestroying session...")
        # logout_response = api.sessions.destroy_session()
        # print(f"Logout Response: {json.dumps(logout_response, indent=2)}")


    except TastytradeAPIError as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'api' in locals() and isinstance(api, TastyTradesApi):
            api.close_session()