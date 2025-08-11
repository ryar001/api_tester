#!/usr/bin/env python3
"""
OKX API Key Test Script

This script tests the OKX API keys for both read-only and read-write operations.
It verifies that read-only keys can only perform read operations and that
read-write keys can perform both read and write operations.
"""

import os
import sys
import yaml
import json
import math
import time
from pathlib import Path

# Add the parent directory to the path so we can import the api_tester module
sys.path.append(str(Path(__file__).parent.parent.parent))

from api_tester.rest.okx import OkxApi

# OKX hosts
OKX_HOST = {
    "PROD": "https://www.okx.com",
    "DEMO": "https://www.okx.com"  # OKX uses the same host but with a simulated flag
}

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

def test_api_key(test_results, key_name, api_key, api_secret, passphrase, key_type, is_qa=False, spot_symbol="BTC-USDT", perp_symbol="BTC-USDT-SWAP", quantity=0.001):
    """
    Test operations with the given OKX API key.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        api_key: The API key
        api_secret: The API secret
        passphrase: The API passphrase
        key_type: Type of key ('read_only' or 'read_write')
        use_simulated: Whether to use the demo trading environment
        spot_symbol: Symbol for spot trading tests
        perp_symbol: Symbol for perpetual swap trading tests
        quantity: Quantity to use for trading tests
    """
    print(f"\n\n========== TESTING {key_name} ({key_type}) ==========")
    
    host = OKX_HOST["DEMO"] if is_qa else OKX_HOST["PROD"]
    print(f"Using {'Demo' if is_qa else 'Production'} environment")

    try:
        # Initialize the OKX API client with the provided keys
        okx_api = OkxApi(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            spot_symbol=spot_symbol,
            perp_symbol=perp_symbol,
            quantity=quantity,
            use_simulated=is_qa
        )

        # Test read operations
        print("\n--- Testing Read Operations ---")

        # Test spot market config
        spot_config = okx_api.get_spot_config()
        print_response("Spot Market Config", spot_config)
        
        # Verify spot config
        if "code" in spot_config and spot_config["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Spot Config",
                True,
                f"Successfully retrieved spot config with {key_type} key"
            )
        else:
            error_msg = spot_config.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Spot Config",
                False,
                f"Failed to retrieve spot config: {error_msg}"
            )

        # Test spot balance
        spot_balance = okx_api.get_spot_balance()
        print_response("Spot Balance", spot_balance)
        
        # Verify spot balance
        if "code" in spot_balance and spot_balance["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Spot Balance",
                True,
                f"Successfully retrieved spot balance with {key_type} key"
            )
        else:
            error_msg = spot_balance.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Spot Balance",
                False,
                f"Failed to retrieve spot balance: {error_msg}"
            )

        # Test futures position
        fut_position = okx_api.get_fut_position()
        print_response("Futures Position", fut_position)
        
        # Verify futures position
        if "code" in fut_position and fut_position["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Futures Position",
                True,
                f"Successfully retrieved futures position with {key_type} key"
            )
        else:
            error_msg = fut_position.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Futures Position",
                False,
                f"Failed to retrieve futures position: {error_msg}"
            )
            
        # Test spot price
        spot_price = okx_api.get_spot_price()
        print_response("Spot Price", spot_price)
        
        # Verify spot price
        if "code" in spot_price and spot_price["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Spot Price",
                True,
                f"Successfully retrieved spot price with {key_type} key"
            )
        else:
            error_msg = spot_price.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Spot Price",
                False,
                f"Failed to retrieve spot price: {error_msg}"
            )

        # Test write operations
        print("\n--- Testing Write Operations ---")

        # Test spot buy
        buy_spot = okx_api.test_buy_spot()
        print_response(f"Buy Spot {'(should fail)' if key_type == 'read_only' else ''}", buy_spot)
        
        # Verify spot buy
        if "code" in buy_spot and buy_spot["code"] == "0":
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
        else:
            error_msg = buy_spot.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                test_results.add_result(
                    f"{key_name}: Buy Spot",
                    False,
                    f"Failed to place spot buy order: {error_msg}"
                )

        # Test spot sell
        sell_spot = okx_api.test_sell_spot()
        print_response(f"Sell Spot {'(should fail)' if key_type == 'read_only' else ''}", sell_spot)
        
        # Verify spot sell
        if "code" in sell_spot and sell_spot["code"] == "0":
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
        else:
            error_msg = sell_spot.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                test_results.add_result(
                    f"{key_name}: Sell Spot",
                    False,
                    f"Failed to place spot sell order: {error_msg}"
                )

        # Test open orders
        spot_orders = okx_api.get_spot_open_orders()
        print_response("Current Spot Orders", spot_orders)
        
        # Verify get open orders
        if "code" in spot_orders and spot_orders["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Spot Open Orders",
                True,
                f"Successfully retrieved spot open orders with {key_type} key"
            )
        else:
            error_msg = spot_orders.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Spot Open Orders",
                False,
                f"Failed to retrieve spot open orders: {error_msg}"
            )

        # Test cancel spot orders
        cancel_spot = okx_api.cancel_spot_open_orders()
        print_response(f"Cancel Spot Orders {'(should fail)' if key_type == 'read_only' else ''}", cancel_spot)
        
        # Verify cancel spot orders
        if "code" in cancel_spot and cancel_spot["code"] == "0":
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
        else:
            error_msg = cancel_spot.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                # If the message indicates no orders to cancel, that's fine
                if "no open orders" in error_msg.lower() or "no orders" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Cancel Spot Orders",
                        True,
                        "No open orders to cancel"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Cancel Spot Orders",
                        False,
                        f"Failed to cancel spot orders: {error_msg}"
                    )

        # Test futures operations
        print("\n--- Testing Futures Operations ---")
        
        # Test futures market config
        perp_config = okx_api.get_perp_market_config()
        print_response("Futures Market Config", perp_config)
        
        # Verify futures config
        if "code" in perp_config and perp_config["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Futures Config",
                True,
                f"Successfully retrieved futures config with {key_type} key"
            )
        else:
            error_msg = perp_config.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Futures Config",
                False,
                f"Failed to retrieve futures config: {error_msg}"
            )

        # get precision
        perp_config = perp_config['data'][0]
        price_prec = float(perp_config['tickSz'])
        qty_prec = float(perp_config['lotSz'])
        cont_size = float(perp_config['ctVal'])

        # convert from float precision to int precision
        price_prec = abs(int(math.log10(price_prec)))
        qty_prec = abs(int(math.log10(qty_prec)))

        # Test open long futures
        open_long = okx_api.test_open_long_fut(qty_prec,cont_size)
        print_response(f"Open Long Futures {'(should fail)' if key_type == 'read_only' else ''}", open_long)
        
        # Verify open long futures
        if "code" in open_long and open_long["code"] == "0":
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
        else:
            error_msg = open_long.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                test_results.add_result(
                    f"{key_name}: Open Long Futures",
                    False,
                    f"Failed to open long futures position: {error_msg}"
                )

        # Test close long futures
        close_long = okx_api.test_close_long_fut(qty_prec,cont_size)
        print_response(f"Close Long Futures {'(should fail)' if key_type == 'read_only' else ''}", close_long)
        
        # Verify close long futures
        if "code" in close_long and close_long["code"] == "0":
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
        else:
            error_msg = close_long.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                # If the message indicates no position to close, that's fine
                if "no position" in error_msg.lower() or "no long position" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        True,
                        "No long position to close"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Close Long Futures",
                        False,
                        f"Failed to close long futures position: {error_msg}"
                    )

        # Test futures orders
        fut_orders = okx_api.get_fut_open_orders()
        print_response("Current Futures Orders", fut_orders)
        
        # Verify get futures open orders
        if "code" in fut_orders and fut_orders["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Futures Open Orders",
                True,
                f"Successfully retrieved futures open orders with {key_type} key"
            )
        else:
            error_msg = fut_orders.get('msg', 'Unknown error')
            test_results.add_result(
                f"{key_name}: Get Futures Open Orders",
                False,
                f"Failed to retrieve futures open orders: {error_msg}"
            )

        # Test cancel futures orders
        cancel_fut = okx_api.cancel_fut_open_orders()
        print_response(f"Cancel Futures Orders {'(should fail)' if key_type == 'read_only' else ''}", cancel_fut)
        
        # Verify cancel futures orders
        if "code" in cancel_fut and cancel_fut["code"] == "0":
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
        else:
            error_msg = cancel_fut.get('msg', 'Unknown error')
            if key_type == 'read_only':
                # For read-only keys, errors are expected
                if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
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
                # For read-write keys, errors might be due to other issues
                # If the message indicates no orders to cancel, that's fine
                if "no open orders" in error_msg.lower() or "no orders" in error_msg.lower():
                    test_results.add_result(
                        f"{key_name}: Cancel Futures Orders",
                        True,
                        "No open futures orders to cancel"
                    )
                else:
                    test_results.add_result(
                        f"{key_name}: Cancel Futures Orders",
                        False,
                        f"Failed to cancel futures orders: {error_msg}"
                    )
         # test account config
        acct_config = okx_api.get_account_config()
        print_response("Account Config", acct_config)
        if "code" in acct_config and acct_config["code"] == "0":
            test_results.add_result(
                f"{key_name}: Get Account Config",
                True,
                f"Successfully retrieved account config with {key_type} key"
            )
        breakpoint()

    except Exception as e:
        print(f"Error testing {key_name}: {e}")
        test_results.add_result(
            f"{key_name}: Setup",
            False,
            f"Failed to set up {key_type} key test: {str(e)}"
        )

def run_tests(is_qa=True):
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

        # Test all OKX API keys
        if 'okx' in keys:
            okx_keys = keys['okx']
            # Test read-only keys
            for key_name, key_data in okx_keys.items():
                if 'read_only' in key_name:
                    print(f"\nTesting OKX read-only key: {key_name}")
                    test_api_key(
                        test_results,
                        key_name,
                        key_data['api_key'],
                        key_data['api_secret'],
                        key_data['passphrase'],
                        'read_only',
                        is_qa=is_qa
                    )

            # Test read-write keys
            for key_name, key_data in okx_keys.items():
                if 'read_trade' in key_name or 'read_write' in key_name:
                    print(f"\nTesting OKX read-write key: {key_name}")
                    test_api_key(
                        test_results,
                        key_name,
                        key_data['api_key'],
                        key_data['api_secret'],
                        key_data['passphrase'],
                        'read_write',
                        is_qa=is_qa
                    )
        else:
            print("No OKX API keys found in .keys.yaml")
            test_results.add_result(
                "OKX API Keys",
                False,
                "No OKX API keys found in .keys.yaml"
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
    # Run the tests with simulated trading (demo mode)
    start_time = time.time()
    results = run_tests(is_qa=False)
    end_time = time.time()

    print(f"\nTests completed in {end_time - start_time:.2f} seconds.")
    print("\nExpected results:")
    print("1. Read operations succeed with both read-only and read-write keys")
    print("2. Write operations fail with read-only keys")
    print("3. Write operations succeed with read-write keys")

    # Return a non-zero exit code if any tests failed
    sys.exit(1 if results.failed > 0 else 0)
