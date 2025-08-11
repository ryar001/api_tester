#!/usr/bin/env python3
"""
Binance Portfolio Margin API Key Test Script

This script tests the Binance Portfolio Margin API keys for both read-only and read-write operations.
It verifies that read-only keys can only perform read operations and that
read-write keys can perform both read and write operations.
"""

import os
import sys
import yaml
import json
import time
from pathlib import Path

# Add the parent directory to the path so we can import the api_tester module
sys.path.append(str(Path(__file__).parent.parent.parent))

from api_tester.rest.binance_PM_addon import BinancePmTestWrapper

# Binance hosts
BINANCE_PERP_HOST = {
    "PROD": "https://fapi.binance.com",
    "DEMO": "https://testnet.binancefuture.com"  # Note: PM might not be available on testnet
}
BINANCE_PM_HOST = {
    "PROD": "https://papi.binance.com",
    "DEMO": "https://papi.binance.com"  # Note: PM might not be available on testnet
}
BINANCE_SPOT_HOST = {   
    "PROD": "https://api.binance.com",
    "DEMO": "https://testnet.binance.vision"
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

def test_read_operation(test_results, key_name, key_type, api, method_name, display_name, *args, **kwargs):
    """
    Test a read operation and add the result to test_results.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        key_type: Type of key ('read_only' or 'read_write')
        api: The API client instance
        method_name: The name of the method to call on the API client
        display_name: The display name for the test
        *args, **kwargs: Arguments to pass to the method
    """
    method = getattr(api, method_name)
    if method_name in ["get_spot_balance", "get_spot_price","get_perp_market_config"]:
        pass
        # breakpoint()
    result = method(*args, **kwargs)
    print_response(display_name, result)

    if "error" not in result:
        test_results.add_result(
            f"{key_name}: {display_name}",
            True,
            f"Successfully {display_name.lower()} with {key_type} key"
        )
        return result
    else:
        error_msg = result.get('error', 'Unknown error')
        test_results.add_result(
            f"{key_name}: {display_name}",
            False,
            f"Failed to {display_name.lower()}: {error_msg}"
        )
        return result

def test_write_operation(test_results, key_name, key_type, api, method_name, display_name, *args, **kwargs):
    """
    Test a write operation and add the result to test_results.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        key_type: Type of key ('read_only' or 'read_write')
        api: The API client instance
        method_name: The name of the method to call on the API client
        display_name: The display name for the test
        *args, **kwargs: Arguments to pass to the method
    """
    method = getattr(api, method_name)
    result = method(*args, **kwargs)
    print_response(f"{display_name} {'(should fail)' if key_type == 'read_only' else ''}", result)

    if method_name in ["test_buy_spot", "test_sell_spot"]:
        # breakpoint()
        pass
    
    # Check for errors
    error_msg = result.get('msg', 'Unknown error')
    if key_type == 'read_only':
        # For read-only keys, errors are expected
        if "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
            test_results.add_result(
                f"{key_name}: {display_name}",
                True,
                f"Correctly failed to {display_name.lower()} with read-only key: {error_msg}"
            )
        else:
            test_results.add_result(
                f"{key_name}: {display_name}",
                False,
                f"Failed with unexpected error: {error_msg}"
            )
    else:
        # For read-write keys, errors might be due to other issues
        # Check for specific error messages that might be acceptable
        acceptable_errors = {
            "Cancel Spot Orders": ["no open orders", "no orders"],
            "Cancel Futures Orders": ["no open orders", "no orders"],
            "Close Long Futures": ["no position", "no long position"]
        }

        acceptable = False
        if display_name in acceptable_errors:
            for error_text in acceptable_errors[display_name]:
                if error_text in error_msg.lower():
                    acceptable = True
                    break

        if acceptable:
            test_results.add_result(
                f"{key_name}: {display_name}",
                True,
                f"No {display_name.lower()} needed"
            )
        else:
            test_results.add_result(
                f"{key_name}: {display_name}",
                False,
                f"Failed to {display_name.lower()}: {error_msg}"
            )

    return result

def test_api_key(test_results, key_name, api_key, api_secret, key_type, use_testnet=False,spot_symbol="BTCUSDT", perp_symbol="BTCUSDT", quantity=0.001):
    """
    Test operations with the given Binance Portfolio Margin API key.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        api_key: The API key
        api_secret: The API secret
        key_type: Type of key ('read_only' or 'read_write')
        use_testnet: Whether to use the testnet environment
        perp_symbol: Symbol for perpetual swap trading tests
        quantity: Quantity to use for trading tests
    """
    print(f"\n\n========== TESTING {key_name} ({key_type}) ==========")

    spot_host = BINANCE_SPOT_HOST["DEMO"] if use_testnet else BINANCE_SPOT_HOST["PROD"]
    perp_host = BINANCE_PERP_HOST["DEMO"] if use_testnet else BINANCE_PERP_HOST["PROD"]
    pm_host = BINANCE_PM_HOST["DEMO"] if use_testnet else BINANCE_PM_HOST["PROD"]
    print(f"Using {spot_host} for spot, {perp_host} for futures, and {pm_host} for PM")

    try:
        # Initialize the Binance PM API client with the provided keys
        api = BinancePmTestWrapper(
            spot_host=spot_host,
            perp_host=perp_host,
            pm_host=pm_host,
            api_key=api_key,
            api_secret=api_secret,
            default_symbol=perp_symbol,
            default_quantity=quantity
        )

        # Test read operations
        print("\n--- Testing Read Operations ---")

        # Define read operations to test
        read_operations = [
            ("get_spot_config", "Get Spot Config"),
            ("get_spot_balance", "Get Spot Balance"),
            ("get_pm_balance", "Get PM Balance"),
            ("get_fut_position", "Get Futures Position"),
            {"get_fut_balance", "Get Futures Balance"},
            ("get_spot_price", "Get Spot Price"),
            ("get_spot_open_orders", "Get Spot Open Orders"),
            ("get_fut_open_orders", "Get Futures Open Orders"),
            ("get_perp_market_config", "Get Futures Config"),
            ("get_account_config", "Get Account Config")
        ]

        # Execute read operations
        for method_name, display_name in read_operations:
            test_read_operation(test_results, key_name, key_type, api, method_name, display_name)

        # Test write operations
        print("\n--- Testing Write Operations ---")

        # Define write operations to test
        write_operations = [
            ("test_buy_spot", "Buy Spot"),
            ("test_sell_spot", "Sell Spot"),
            ("cancel_spot_open_orders", "Cancel Spot Orders"),
            ("open_long_fut", "Open Long Futures"),
            ("close_long_fut", "Close Long Futures"),
            ("cancel_fut_open_orders", "Cancel Futures Orders")
        ]

        # Execute write operations
        for method_name, display_name in write_operations:
            test_write_operation(test_results, key_name, key_type, api, method_name, display_name)

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
                    print(f"\nTesting Binance PM read-only key: {key_name}")
                    test_api_key(
                        test_results,
                        key_name,
                        key_data['api_key'],
                        key_data['api_secret'],
                        'read_only',
                        use_testnet=use_testnet,
                        perp_symbol="BTCUSDT",
                        quantity=0.001
                    )

            # Test read-write keys
            for key_name, key_data in binance_keys.items():
                if 'read_trade' in key_name or 'read_write' in key_name:
                    print(f"\nTesting Binance PM read-write key: {key_name}")
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
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test Binance Portfolio Margin API keys')
    parser.add_argument('--testnet', action='store_true', help='Use testnet instead of production')
    args = parser.parse_args()

    # Run the tests
    start_time = time.time()
    results = run_tests(use_testnet=args.testnet)
    end_time = time.time()

    print(f"\nTests completed in {end_time - start_time:.2f} seconds.")
    print("\nExpected results:")
    print("1. Read operations succeed with both read-only and read-write keys")
    print("2. Write operations fail with read-only keys")
    print("3. Write operations succeed with read-write keys")

    # Return a non-zero exit code if any tests failed
    sys.exit(1 if results.failed > 0 else 0)
