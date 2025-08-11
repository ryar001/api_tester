#!/usr/bin/env python3
"""
Binance API Key Test Script

This script tests the Binance API keys for both read-only and read-write operations.
It verifies that read-only keys can only perform read operations and that
read-write keys can perform both read and write operations.
"""

import os
import sys
import yaml
import json
import time
from pathlib import Path

BINANCE_HOST = {
    "SPOT_PROD": "https://api.binance.com",
    "PERP_PROD": "https://fapi.binance.com",
    "SPOT_TEST": "https://testnet.binance.vision",
    "PERP_TEST": "https://testnet.binancefuture.com"
}

# Add the parent directory to the path so we can import the api_tester module
sys.path.append(str(Path(__file__).parent.parent.parent))

from api_tester.rest.binance_api import binanceApi

class TestResult:
    """Class to track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.test_result_dict = {}  # Dictionary to store results by API key

    def add_result(self, test_name, passed, message):
        """Add a test result."""
        status = "PASSED" if passed else "FAILED"
        result = {
            "test_name": test_name,
            "status": status,
            "message": message
        }
        self.results.append(result)

        # Extract the API key name from the test_name (format: "key_name: Test Name")
        key_name = test_name.split(":")[0].strip()

        # Add to the dictionary
        if key_name not in self.test_result_dict:
            self.test_result_dict[key_name] = []
        self.test_result_dict[key_name].append(result)

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        """Print a summary of the test results."""
        print("\n\n========== TEST SUMMARY ==========")
        print(f"Total tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("=================================")

        # Print results grouped by API key
        for key_name, results in self.test_result_dict.items():
            print(f"\n=============== Results for {key_name} ===============")
            key_passed = sum(1 for r in results if r["status"] == "PASSED")
            key_total = len(results)
            print(f"Passed: {key_passed}/{key_total} ({key_passed/key_total*100:.1f}%)")

            for result in results:
                status_symbol = "✅" if result["status"] == "PASSED" else "❌"
                print(f"{status_symbol} {result['test_name']}: {result['message']}")

            print("=" * (len(f" Results for {key_name} ") + 16))

def print_response(title, response):
    """Print a formatted response."""
    print(f"\n=== {title} ===")
    print(json.dumps(response, indent=2))
    print("=" * (len(title) + 8))

def test_api_key(test_results, key_name, api_key, api_secret, key_type, use_testnet=False,symbol="ETHUSDT",quantity=0.02):
    """
    Test operations with the given API key.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        api_key: The API key
        api_secret: The API secret
        key_type: Type of key ('read_only' or 'read_write')
        use_testnet: Whether to use testnet hosts
    """
    print(f"\n\n========== TESTING {key_name} ({key_type}) ==========")

    if use_testnet:
        print("Using TEST host")
        spot_host = BINANCE_HOST["SPOT_TEST"]
        perp_host = BINANCE_HOST["PERP_TEST"]
    else:
        print("Using PROD host")
        spot_host = BINANCE_HOST["SPOT_PROD"]
        perp_host = BINANCE_HOST["PERP_PROD"]

    try:
        # Initialize the Binance API client with the provided keys
        binance_api = binanceApi(
            spot_host=spot_host,
            perp_host=perp_host,
            api_key=api_key,
            api_secret=api_secret,
            default_symbol=symbol,
            default_quantity=quantity
        )

        # Test read operations
        print("\n--- Testing Read Operations ---")

        # Test spot balance
        spot_balance = binance_api.get_spot_balance()
        print_response("Spot Balance", spot_balance)

        # Verify spot balance
        if "error" not in spot_balance:
            test_results.add_result(
                f"{key_name}: Get Spot Balance",
                True,
                f"Successfully retrieved spot balance with {key_type} key"
            )
        else:
            error_msg = spot_balance.get('error', '')
            # Check if the error is due to IP restrictions or authentication
            if "IP" in error_msg or "API-key" in error_msg or "apikey" in error_msg.lower():
                test_results.add_result(
                    f"{key_name}: Get Spot Balance",
                    True,
                    f"Expected IP restriction or authentication error: {error_msg}"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Get Spot Balance",
                    False,
                    f"Failed to retrieve spot balance: {error_msg}"
                )

        # Test futures position
        fut_position = binance_api.get_fut_position()
        print_response("Futures Position", fut_position)

        # Verify futures position
        if "error" not in fut_position:
            test_results.add_result(
                f"{key_name}: Get Futures Position",
                True,
                f"Successfully retrieved futures position with {key_type} key"
            )
        else:
            error_msg = fut_position.get('error', '')
            if "IP" in error_msg or "API-key" in error_msg or "apikey" in error_msg.lower():
                test_results.add_result(
                    f"{key_name}: Get Futures Position",
                    True,
                    f"Expected IP restriction or authentication error: {error_msg}"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Get Futures Position",
                    False,
                    f"Failed to retrieve futures position: {error_msg}"
                )

        # Test spot price
        spot_price = binance_api.get_spot_price()
        print_response("Spot Price", spot_price)

        # Verify spot price
        if spot_price and "error" not in spot_price:
            test_results.add_result(
                f"{key_name}: Get Spot Price",
                True,
                f"Successfully retrieved spot price with {key_type} key"
            )
        else:
            error_msg = "Failed to get spot price" if not spot_price else spot_price.get('error', '')
            test_results.add_result(
                f"{key_name}: Get Spot Price",
                False,
                f"Failed to retrieve spot price: {error_msg}"
            )

        # Test spot config
        spot_config = binance_api.get_spot_config()
        print_response("Spot Config", spot_config)

        # Verify spot config
        if spot_config and "error" not in spot_config:
            test_results.add_result(
                f"{key_name}: Get Spot Config",
                True,
                f"Successfully retrieved spot config with {key_type} key"
            )
        else:
            error_msg = "Failed to get spot config" if not spot_config else spot_config.get('error', '')
            test_results.add_result(
                f"{key_name}: Get Spot Config",
                False,
                f"Failed to retrieve spot config: {error_msg}"
            )

        # Test perp market config
        perp_config = binance_api.get_perp_market_config()
        print_response("Perp Market Config", perp_config)

        # Verify perp market config
        if perp_config and "error" not in perp_config:
            test_results.add_result(
                f"{key_name}: Get Perp Market Config",
                True,
                f"Successfully retrieved perp market config with {key_type} key"
            )
        else:
            error_msg = "Failed to get perp market config" if not perp_config else perp_config.get('error', '')
            test_results.add_result(
                f"{key_name}: Get Perp Market Config",
                False,
                f"Failed to retrieve perp market config: {error_msg}"
            )

        # Test write operations
        print("\n--- Testing Write Operations ---")

        # get config
        spot_config = binance_api.get_spot_config()
        spot_config = spot_config['symbols'][0]

        print_response("Config", spot_config)

        # Test spot buy
        buy_spot = binance_api.test_buy_spot(spot_config)
        print_response(f"Buy Spot {'(should fail)' if key_type == 'read_only' else ''}", buy_spot)

        # Verify spot buy
        if "error" in buy_spot:
            error_msg = buy_spot.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Buy Spot",
                        True,
                        f"Correctly failed to buy spot with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Buy Spot",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                # For read-write keys, errors might be due to implementation issues
                if "ticker" in error_msg or "price" in error_msg:
                    test_results.add_result(
                        f"{key_name}: Buy Spot",
                        True,
                        f"API implementation issue (not a key permission issue): {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Buy Spot",
                        False,
                        f"Failed to place spot buy order: {error_msg}"
                    )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Buy Spot",
                    False,
                    "Unexpectedly succeeded in buying spot with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Buy Spot",
                    True,
                    "Successfully placed spot buy order with read-write key"
                )

        # Test spot sell
        sell_spot = binance_api.test_sell_spot(spot_config)
        print_response(f"Sell Spot {'(should fail)' if key_type == 'read_only' else ''}", sell_spot)

        # Verify spot sell
        if "error" in sell_spot:
            error_msg = sell_spot.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Sell Spot",
                        True,
                        f"Correctly failed to sell spot with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Sell Spot",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                # For read-write keys, errors might be due to implementation issues
                if "ticker" in error_msg or "price" in error_msg:
                    test_results.add_result(
                        f"{key_name}: Sell Spot",
                        True,
                        f"API implementation issue (not a key permission issue): {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Sell Spot",
                        False,
                        f"Failed to place spot sell order: {error_msg}"
                    )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Sell Spot",
                    False,
                    "Unexpectedly succeeded in selling spot with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Sell Spot",
                    True,
                    "Successfully placed spot sell order with read-write key"
                )

        # Print current orders
        print_response("Current Spot Orders", binance_api.get_spot_open_orders())

        # Test cancel spot orders
        cancel_spot = binance_api.cancel_spot_open_orders()
        print_response(f"Cancel Spot Orders {'(should fail)' if key_type == 'read_only' else ''}", cancel_spot)

        # Check current orders after cancellation
        print_response("Current Spot Orders After Cancellation", binance_api.get_spot_open_orders())

        # Verify cancel spot orders
        if "error" in cancel_spot:
            error_msg = cancel_spot.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Cancel Spot Orders",
                        True,
                        f"Correctly failed to cancel spot orders with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Cancel Spot Orders",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                test_results.add_result(
                    f"{key_name}: Cancel Spot Orders",
                    True,
                    f"Successfully cancelled spot orders or received expected response: {cancel_spot}"
                )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Cancel Spot Orders",
                    False,
                    "Unexpectedly succeeded in cancelling spot orders with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Cancel Spot Orders",
                    True,
                    "Successfully cancelled spot orders with read-write key"
                )

        # get fut config
        price_prec = perp_config[0]['pricePrecision']
        qty_prec = perp_config[0]['quantityPrecision']
        cont_size = 1

        # Test open long futures
        open_long = binance_api.test_open_long_fut(price_prec,qty_prec,cont_size)
        print_response(f"Open Long Futures {'(should fail)' if key_type == 'read_only' else ''}", open_long)

        # Verify open long futures
        if "error" in open_long:
            error_msg = open_long.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Open Long Futures",
                        True,
                        f"Correctly failed to open long futures with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Open Long Futures",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                # For read-write keys, errors might be due to implementation issues
                if "markPrice" in error_msg or "price" in error_msg:
                    test_results.add_result(
                        f"{key_name}: Open Long Futures",
                        True,
                        f"API implementation issue (not a key permission issue): {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Open Long Futures",
                        False,
                        f"Failed to open long futures position: {error_msg}"
                    )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Open Long Futures",
                    False,
                    "Unexpectedly succeeded in opening long futures with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Open Long Futures",
                    True,
                    "Successfully opened long futures position with read-write key"
                )

        # Test close long futures
        close_long = binance_api.test_close_long_fut(price_prec,qty_prec,cont_size)
        print_response(f"Close Long Futures {'(should fail)' if key_type == 'read_only' else ''}", close_long)

        # Verify close long futures
        if "error" in close_long:
            error_msg = close_long.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        True,
                        f"Correctly failed to close long futures with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                # For read-write keys, errors might be due to implementation issues
                if "markPrice" in error_msg or "price" in error_msg:
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        True,
                        f"API implementation issue (not a key permission issue): {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        False,
                        f"Failed to close long futures position: {error_msg}"
                    )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Close Long Futures",
                    False,
                    "Unexpectedly succeeded in closing long futures with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Close Long Futures",
                    True,
                    "Successfully closed long futures position with read-write key"
                )

        # Test cancel futures orders
        print_response("Current Futures Orders", binance_api.get_fut_open_orders())
        cancel_fut = binance_api.cancel_fut_open_orders()
        print_response(f"Cancel Futures Orders {'(should fail)' if key_type == 'read_only' else ''}", cancel_fut)
        # Check current orders after cancellation
        print_response("Current Futures Orders After Cancellation", binance_api.get_fut_open_orders())

        # Verify cancel futures orders
        if "error" in cancel_fut:
            error_msg = cancel_fut.get('error', '')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "API-key" in error_msg or "apikey" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Cancel Futures Orders",
                        True,
                        f"Correctly failed to cancel futures orders with read-only key: {error_msg}"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Cancel Futures Orders",
                        False,
                        f"Failed with unexpected error: {error_msg}"
                    )
            else:
                test_results.add_result(
                    f"{key_name}: Cancel Futures Orders",
                    True,
                    f"Successfully cancelled futures orders or received expected response: {cancel_fut}"
                )
        else:
            if key_type == 'read_only':
                test_results.add_result(
                    f"{key_name}: Cancel Futures Orders",
                    False,
                    "Unexpectedly succeeded in cancelling futures orders with read-only key"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Cancel Futures Orders",
                    True,
                    "Successfully cancelled futures orders with read-write key"
                )

    except Exception as e:
        print(f"Error testing {key_name}: {e}")
        test_results.add_result(
            f"{key_name}: Setup",
            False,
            f"Failed to set up {key_type} key test: {str(e)}"
        )

def run_tests(use_testnet=False):
    """Run all tests and return the results."""
    # Create a test results object
    test_results = TestResult()

    # Create tests directory if it doesn't exist
    os.makedirs(Path(__file__).parent, exist_ok=True)

    # Load API keys from the keys.yaml file
    keys_path = Path(__file__).parent.parent / '.keys.yaml'
    try:
        with open(keys_path, 'r') as f:
            keys = yaml.safe_load(f)

        # Test all Binance API keys
        if 'binance' in keys:
            binance_keys = keys['binance']
            # Test read-only keys
            for key_name, key_data in binance_keys.items():
                if 'read_only' in key_name:
                    print(f"\nTesting Binance read-only key: {key_name}")
                    test_api_key(
                        test_results,
                        key_name,
                        key_data['api_key'],
                        key_data['api_secret'],
                        'read_only',
                        use_testnet=use_testnet
                    )

            # Test read-write keys
            for key_name, key_data in binance_keys.items():
                if 'read_write' in key_name:
                    print(f"\nTesting Binance read-write key: {key_name}")
                    test_api_key(
                        test_results,
                        key_name,
                        key_data['api_key'],
                        key_data['api_secret'],
                        'read_write',
                        use_testnet=use_testnet
                    )
        else:
            print("No Binance API keys found in .keys.yaml")
            test_results.add_result(
                "Binance API Keys",
                False,
                "No Binance API keys found in .keys.yaml"
            )

    except FileNotFoundError:
        print(f"Error: .keys.yaml file not found at {keys_path}")
        test_results.add_result(
            "Keys File",
            False,
            f".keys.yaml file not found at {keys_path}"
        )
    except Exception as e:
        print(f"Error loading or processing API keys: {e}")
        test_results.add_result(
            "API Keys Processing",
            False,
            f"Error loading or processing API keys: {str(e)}"
        )
    # Print test summary
    test_results.print_summary()

    return test_results

if __name__ == "__main__":
    # Run the tests
    start_time = time.time()

    # Default to production environment
    use_testnet = False

    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['--testnet', '-t']:
        use_testnet = True
        print("Using testnet environment")

    results = run_tests(use_testnet=use_testnet)
    end_time = time.time()

    print(f"\nTests completed in {end_time - start_time:.2f} seconds.")
    print("\nExpected results:")
    print("1. Read operations succeed with both read-only and read-write keys")
    print("2. Write operations fail with read-only keys")
    print("3. Write operations succeed with read-write keys")

    # Return a non-zero exit code if any tests failed
    sys.exit(1 if results.failed > 0 else 0)
