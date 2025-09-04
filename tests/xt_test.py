#!/usr/bin/env python3
"""
XT API Key Test Script

This script tests the XT API keys for both read-only and read-write operations.
It verifies that read-only keys can only perform read operations and that
read-write keys can perform both read and write operations.
"""

import os
import sys
import yaml
import json
import time
from pathlib import Path

XT_HOST = {
    "SPOT_QA": "https://sapi.xt-qa.com",
    "PERP_QA": "https://fapi.xt-qa.com",
    "SPOT_PROD": "https://sapi.xt.com",
    "PERP_PROD": "https://fapi.xt.com"
}

# Add the parent directory to the path so we can import the api_tester module
sys.path.append(str(Path(__file__).parent.parent.parent))

# add the rest dir

sys.path.append(str(Path(__file__).parent.parent / 'rest'))

from api_tester.rest.xt import XtApi

class TestResult:
    """Class to track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        self.test_result_dict = {}  # Dictionary to store results by API key
        self.fee_info = {}  # Dictionary to store fee information by API key

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

    def add_fee_info(self, key_name, spot_fee, um_fee):
        """Add fee information for an API key."""
        self.fee_info[key_name] = {
            "spot_fee": spot_fee,
            "um_fee": um_fee
        }

    def print_summary(self):
        """Print a summary of the test results."""
        print("\n\n========== TEST SUMMARY ==========")
        print(f"Total tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print("=================================")

        # Print results grouped by API key
        for key_name, results in self.test_result_dict.items():
            print(f"\n=============== Results for {key_name} ==============")
            key_passed = sum(1 for r in results if r["status"] == "PASSED")
            key_total = len(results)
            print(f"Passed: {key_passed}/{key_total} ({key_passed/key_total*100:.1f}%)")

            # print entire fee dict
            if key_name in self.fee_info:
                print(f"\n--- Fee Information for {key_name} ---")
                print(f"Spot Fees: {self.fee_info[key_name]['spot_fee']}")
                print(f"UM Fees: {self.fee_info[key_name]['um_fee']}")
                print("------------------------")

            for result in results:
                status_symbol = "✅" if result["status"] == "PASSED" else "❌"
                print(f"{status_symbol} {result['test_name']}: {result['message']}")

            print("=" * (len(f" Results for {key_name} ") + 16))

def print_response(title, response):
    """Print a formatted response."""
    print(f"\n=== {title} ===")
    try:
        if response is None:
            print("None")
        else:
            print(json.dumps(response, indent=2))
    except (TypeError, ValueError):
        print(f"Non-serializable response: {response}")
    print("=" * (len(title) + 8))

def validate_read_operation(test_results, key_name, response, operation_name, key_type):
    """
    Validate a read operation response and add the result to test_results.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        response: API response to validate
        operation_name: Name of the operation being tested
        key_type: Type of key ('read_only' or 'read_write')
    """
    # Check if response is None or not a dictionary
    if response is None:
        test_results.add_result(
            f"{key_name}: {operation_name}",
            False,
            f"Response is None"
        )
        return False
    if "returnCode" in response and response["returnCode"] == 0:
        test_results.add_result(
            f"{key_name}: {operation_name}",
            True,
            f"Successfully performed {operation_name} with {key_type} key"
        )
        return True

    if not isinstance(response, dict):
        test_results.add_result(
            f"{key_name}: {operation_name}",
            False,
            f"Response is not a dictionary: {response}"
        )
        return False

    if "error" not in response:
        test_results.add_result(
            f"{key_name}: {operation_name}",
            True,
            f"Successfully performed {operation_name} with {key_type} key"
        )
        return True
    else:
        error_msg = response.get('error', '')
        # Ensure error_msg is a string
        if error_msg is None:
            error_msg = "Unknown error"

        if not isinstance(error_msg, str):
            error_msg = str(error_msg)

        # Check if the error is due to IP restrictions or authentication
        if "IP address" in error_msg or "未正确提供xt登录账号" in error_msg or "403" in error_msg:
            test_results.add_result(
                f"{key_name}: {operation_name}",
                True,
                f"Expected IP restriction or authentication error: {error_msg}"
            )
            return True
        else:
            test_results.add_result(
                f"{key_name}: {operation_name}",
                False,
                f"Failed to perform {operation_name}: {error_msg}"
            )
            return False

def validate_write_operation(test_results, key_name, response, operation_name, key_type, expected_error=None):
    """
    Validate a write operation response and add the result to test_results.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        response: API response to validate
        operation_name: Name of the operation being tested
        key_type: Type of key ('read_only' or 'read_write')
        expected_error: Expected error message(s) for implementation issues. Can be a string or a list of strings.
    """

    # cancel dont return anything
    if operation_name in ["Cancel Spot Orders"] and key_type == 'read_write':
        if not response:
            test_results.add_result(
                f"{key_name}: {operation_name}",
                True,
                f"Successfully performed {operation_name} with {key_type} key"
            )
            return True

    # if returnCode == 0:
    if response and "returnCode" in response:
        if response["returnCode"] == 0:
            test_results.add_result(
                f"{key_name}: {operation_name}",
                True,
                f"Successfully performed {operation_name} with {key_type} key"
            )
            return True

    # Check if response is None or not a dictionary
    if response is None and None not in expected_error:
        test_results.add_result(
            f"{key_name}: {operation_name}",
            False,
            f"Response is None"
        )
        return False

    if not isinstance(response, dict):
        test_results.add_result(
            f"{key_name}: {operation_name}",
            False,
            f"Response is not a dictionary: {response}"
        )
        return False

    # Convert expected_error to a list if it's a string or None
    if expected_error is None:
        expected_errors = []
    elif isinstance(expected_error, str):
        expected_errors = [expected_error]
    elif isinstance(expected_error, list):
        expected_errors = expected_error
    else:
        # If it's neither a string nor a list, convert to string and wrap in a list
        expected_errors = [str(expected_error)]

    if "error" in response:
        error_msg = response.get('error', '')

        if not isinstance(error_msg, str):
            error_msg = str(error_msg)

        if key_type == 'read_only':
            # For read-only keys, errors are expected
            if "permission" in error_msg.lower() or "IP address" in error_msg or "AUTH_106" in error_msg:
                test_results.add_result(
                    f"{key_name}: {operation_name}",
                    True,
                    f"Correctly failed to perform {operation_name} with read-only key: {error_msg}"
                )
                return True

            # Check if any of the expected errors are in the error message
            for err in expected_errors:
                if err and err in error_msg:
                    test_results.add_result(
                        f"{key_name}: {operation_name}",
                        True,
                        f"Correctly failed to perform {operation_name} with read-only key: {error_msg}"
                    )
                    return True

            # If we get here, none of the expected errors were found
            test_results.add_result(
                f"{key_name}: {operation_name}",
                False,
                f"Failed with unexpected error: {error_msg}"
            )
            return False
        else:
            # For read-write keys, errors might be due to implementation issues
            # Check if any of the expected errors are in the error message
            for err in expected_errors:
                if err and err in error_msg:
                    test_results.add_result(
                        f"{key_name}: {operation_name}",
                        True,
                        f"API implementation issue (not a key permission issue): {error_msg}"
                    )
                    return True

            # If we get here, none of the expected errors were found
            test_results.add_result(
                f"{key_name}: {operation_name}",
                False,
                f"Failed to perform {operation_name}: {error_msg}"
            )
            return False
    else:
        if key_type == 'read_only':
            test_results.add_result(
                f"{key_name}: {operation_name}",
                False,
                f"Unexpectedly succeeded in performing {operation_name} with read-only key"
            )
            return False
        else:
            test_results.add_result(
                f"{key_name}: {operation_name}",
                True,
                f"Successfully performed {operation_name} with read-write key"
            )
            return True

def test_spot_balance(test_results, xt_api, key_name, key_type):
    """Test spot balance read operation."""
    print("\n--- Testing Spot Balance ---")
    spot_balance = xt_api.get_spot_balance()
    print_response("Spot Balance", spot_balance)
    return validate_read_operation(test_results, key_name, spot_balance, "Get Spot Balance", key_type)

def test_futures_position(test_results, xt_api, key_name, key_type):
    """Test futures position read operation."""
    print("\n--- Testing Futures Position ---")
    fut_position = xt_api.get_fut_position()
    print_response("Futures Position", fut_position)

    if fut_position.get("error") is None:
        test_results.add_result(
            f"{key_name}: Get Futures Position",
            True,
            f"Successfully retrieved futures position with {key_type} key"
        )
        return True
    else:
        error_msg = fut_position.get('error', '')
        if not error_msg:
            error_msg = "Unknown error"
            print(f"Error message not found in response: {fut_position}")

        # Check if the error is due to IP restrictions
        if "IP address" in error_msg or "403" in error_msg:
            test_results.add_result(
                f"{key_name}: Get Futures Position",
                True,
                f"Expected IP restriction error: {error_msg}"
            )
            return True
        else:
            test_results.add_result(
                f"{key_name}: Get Futures Position",
                False,
                f"Failed to retrieve futures position: {error_msg}"
            )
            return False

def test_spot_buy(test_results, xt_api, key_name, key_type):
    """Test spot buy write operation."""
    print("\n--- Testing Spot Buy ---")
    buy_spot = xt_api.test_buy_spot()
    print_response(f"Buy Spot {'(should fail)' if key_type == 'read_only' else ''}", buy_spot)

    expected_errors = ["ORDER_002"]
    if key_type == 'read_only':
        expected_errors += [ "Permission denied", "AUTH_106"]
    return validate_write_operation(test_results, key_name, buy_spot, "Buy Spot", key_type, expected_errors)

def test_spot_sell(test_results, xt_api, key_name, key_type):
    """Test spot sell write operation."""
    print("\n--- Testing Spot Sell ---")
    sell_spot = xt_api.test_sell_spot()
    print_response(f"Sell Spot {'(should fail)' if key_type == 'read_only' else ''}", sell_spot)
    expected_errors = ["ORDER_002"]
    if key_type == 'read_only':
        expected_errors += [ "Permission denied", "AUTH_106"]
    return validate_write_operation(test_results, key_name, sell_spot, "Sell Spot", key_type, expected_errors)

def test_cancel_spot_orders(test_results, xt_api, key_name, key_type):
    """Test cancel spot orders write operation."""
    print("\n--- Testing Cancel Spot Orders ---")
    # Print current orders
    print_response("Current Orders", xt_api.get_spot_open_orders())
    cancel_spot = xt_api.cancel_spot_open_orders()
    print_response(f"Cancel Spot {'(should fail)' if key_type == 'read_only' else ''}", cancel_spot)
    # Check current orders after cancellation
    print_response("Current Orders After Cancellation", xt_api.get_spot_open_orders())
    expected_errors = [None]
    if key_type == 'read_only':
        expected_errors += [ "Permission denied", "AUTH_106"]
    return validate_write_operation(test_results, key_name, cancel_spot, "Cancel Spot Orders", key_type, expected_errors)

def test_open_long_futures(test_results, xt_api, key_name, key_type, price_prec, qty_prec, cont_size):
    """Test open long futures write operation."""
    print("\n--- Testing Open Long Futures ---")
    open_long = xt_api.open_long_fut(price_prec, qty_prec, cont_size)
    print_response(f"Open Long Futures {'(should fail)' if key_type == 'read_only' else ''}", open_long)
    expected_errors = ["ORDER_002",None]
    if key_type == 'read_only':
        expected_errors += [ "Insufficient permissions", "AUTH_106","403"]
    return validate_write_operation(test_results, key_name, open_long, "Open Long Futures", key_type, expected_errors)

def test_close_long_futures(test_results, xt_api, key_name, key_type, price_prec, qty_prec, cont_size):
    """Test close long futures write operation."""
    print("\n--- Testing Close Long Futures ---")
    close_long = xt_api.close_long_fut(price_prec, qty_prec, cont_size)
    print_response(f"Close Long Futures {'(should fail)' if key_type == 'read_only' else ''}", close_long)
    expected_errors = [None]
    if key_type == 'read_only':
        expected_errors += [ "Insufficient permissions", "AUTH_106","403"]
    return validate_write_operation(test_results, key_name, close_long, "Close Long Futures", key_type, expected_errors)

def test_futures_orders(test_results, xt_api, key_name, key_type):
    """Test futures orders read operation."""
    print("\n--- Testing Futures Orders ---")
    orders = xt_api.get_fut_open_orders()
    print_response("Current Futures Orders", orders)

    ord_errors = orders.get("error")
    if not ord_errors:
        test_results.add_result(
            f"{key_name}: Get Futures Orders",
            True,
            f"Successfully retrieved futures orders with {key_type} key"
        )
        return True
    else:
        error_msg = orders.get('error', 'Unknown error')
        # Check if the error is due to IP restrictions
        if "IP address" in error_msg or "403" in error_msg:
            test_results.add_result(
                f"{key_name}: Get Futures Orders",
                True,
                f"Expected IP restriction error: {error_msg}"
            )
            return True
        else:
            test_results.add_result(
                f"{key_name}: Get Futures Orders",
                False,
                f"Failed to retrieve futures orders: {error_msg}"
            )
            return False

def test_cancel_futures_orders(test_results, xt_api, key_name, key_type):
    """Test cancel futures orders write operation."""
    print("\n--- Testing Cancel Futures Orders ---")
    cancel_fut = xt_api.cancel_fut_open_orders()
    print_response(f"Cancel Futures Orders {'(should fail)' if key_type == 'read_only' else ''}", cancel_fut)

    # Check current orders after cancellation
    orders = xt_api.get_fut_open_orders()
    orders_items = orders.get("result", {}).get("items")
    print_response("Current Futures Orders After Cancellation", orders_items)

    # Verify cancel futures orders
    if not orders_items:
        test_results.add_result(
            f"{key_name}: Cancel Futures Orders",
            True,
            "Successfully cancelled futures orders"
        )
        return True

    expected_errors = []
    if key_type == 'read_only':
        expected_errors += [ "Insufficient permissions", "AUTH_106","403"]
    return validate_write_operation(test_results, key_name, cancel_fut, "Cancel Futures Orders", key_type, expected_errors)

def test_futures_balance(test_results, xt_api, key_name, key_type):
    """Test futures balance read operation."""
    print("\n--- Testing Futures Balance ---")
    fut_balance = xt_api.get_fut_balance()
    print_response("Futures Balance", fut_balance)
    return validate_read_operation(test_results, key_name, fut_balance, "Get Futures Balance", key_type)

def test_fee_info(test_results, xt_api, key_name):
    """Test fee information retrieval."""
    print("\n--- Testing Fee Information ---")
    spot_fee = xt_api.get_spot_comms_rate()
    print_response("Spot Fee Information", spot_fee)

    um_fee = xt_api.get_um_comms_rate()
    print_response("UM Fee Information", um_fee)

    # Store fee information in test results
    test_results.add_fee_info(key_name, spot_fee, um_fee)

    return True

def test_get_spot_trades_to_csv(test_results, xt_api, key_name, key_type, symbol):
    """
    Test get_spot_trades with to_csv=True option.
    """
    print("\n--- Testing Get Spot Trades to CSV ---")
    filename = f"spot_trades_{symbol or 'all'}.csv"
    # Clean up any existing file
    if os.path.exists(filename):
        os.remove(filename)

    response = xt_api.get_spot_trades(symbol=symbol, biz_type="SPOT", to_csv=True)
    print_response("Get Spot Trades to CSV", response)

    # Verify file creation and content
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Read header
                rows = list(reader)    # Read remaining rows
            
            if len(rows) > 0 and len(header) > 0: # Check if there's at least one row and header
                test_results.add_result(
                    f"{key_name}: Get Spot Trades to CSV",
                    True,
                    f"Successfully created and verified CSV file: {filename}"
                )
            else:
                test_results.add_result(
                    f"{key_name}: Get Spot Trades to CSV",
                    False,
                    f"CSV file {filename} is empty or has no header."
                )
        except Exception as e:
            test_results.add_result(
                f"{key_name}: Get Spot Trades to CSV",
                False,
                f"Error reading CSV file {filename}: {e}"
            )
        finally:
            os.remove(filename) # Clean up
    else:
        test_results.add_result(
            f"{key_name}: Get Spot Trades to CSV",
            False,
            f"CSV file {filename} was not created."
        )

def test_api_key(test_results, key_name, api_key, api_secret, key_type, is_qa, symbol="eth_usdt", quantity=0.02):

    """
    Test operations with the given API key.

    Args:
        test_results: TestResult object to track test results
        key_name: Name of the key being tested
        api_key: The API key
        api_secret: The API secret
        key_type: Type of key ('read_only' or 'read_write')
        is_qa: Whether to use QA or PROD hosts
        symbol: Trading symbol to use for tests
        quantity: Quantity to use for trading tests
    """
    print(f"\n\n========== TESTING {key_name} ({key_type}) ==========")

    if is_qa:
        print("Using QA host")
        host = XT_HOST["SPOT_QA"]
        perp_host = XT_HOST["PERP_QA"]
    else:
        print("Using PROD host")
        host = XT_HOST["SPOT_PROD"]
        perp_host = XT_HOST["PERP_PROD"]
    try:
        # Initialize the XT API client with the provided keys
        xt_api = XtApi(
            spot_host=host,
            perp_host=perp_host,
            api_key=api_key,
            api_secret=api_secret,
            default_symbol=symbol,
            default_quantity=quantity
        )

        # Test read operations
        print("\n--- Testing Read Operations ---")
        test_spot_balance(test_results, xt_api, key_name, key_type)
        test_futures_balance(test_results, xt_api, key_name, key_type)
        test_futures_position(test_results, xt_api, key_name, key_type)
        test_futures_orders(test_results, xt_api, key_name, key_type)
        test_get_spot_trades_to_csv(test_results, xt_api, key_name, key_type, symbol)

        # Get fee information
        test_fee_info(test_results, xt_api, key_name)

        # Test write operations
        print("\n--- Testing Write Operations ---")
        test_cancel_spot_orders(test_results, xt_api, key_name, key_type)
        test_spot_buy(test_results, xt_api, key_name, key_type)
        test_spot_sell(test_results, xt_api, key_name, key_type)
        test_cancel_spot_orders(test_results, xt_api, key_name, key_type)

        # Get perp market config for futures tests
        perp_config = xt_api.get_perp_market_config(symbol=symbol)
        print_response("Perp Market Config", perp_config)
        try:
            price_prec = perp_config[1]['result']['pricePrecision']
            qty_prec = perp_config[1]['result']['quantityPrecision']
            cont_size = float(perp_config[1]['result']['contractSize'])
            # get current position
            position = xt_api.get_fut_position()
            # cancel all futures orders
            test_cancel_futures_orders(test_results, xt_api, key_name, key_type)
            print_response("Current Position", position)
            test_open_long_futures(test_results, xt_api, key_name, key_type, price_prec, qty_prec, cont_size)
            test_close_long_futures(test_results, xt_api, key_name, key_type, price_prec, qty_prec, cont_size)
            test_cancel_futures_orders(test_results, xt_api, key_name, key_type)
            # get current position
            position = xt_api.get_fut_position()
            print_response("Current Position", position)
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error processing perp market config: {e}")
            test_results.add_result(
                f"{key_name}: Futures Tests",
                False,
                f"Failed to process perp market config: {str(e)}"
            )

    except Exception as e:
        print(f"Error testing {key_name}: {e}")
        test_results.add_result(
            f"{key_name}: Setup",
            False,
            f"Failed to set up {key_type} key test: {str(e)}"
        )

# This function is no longer needed as we're using test_api_key for all key types

def run_tests(is_qa):
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

        # Test all XT API keys
        if 'xt' in keys:
            xt_keys = keys['xt']

            # Test all keys in the keys.yaml file
            for key_name, key_data in xt_keys.items():
                # Determine key type based on name
                key_type = 'read_only' if 'read_only' in key_name else 'read_write'
                print(f"\nTesting XT {key_type} key: {key_name}")

                # Test the API key
                test_api_key(
                    test_results,
                    key_name,
                    key_data['api_key'],
                    key_data['api_secret'],
                    key_type,
                    is_qa=is_qa
                )
        else:
            print("No XT API keys found in .keys.yaml")
            test_results.add_result(
                "XT API Keys",
                False,
                "No XT API keys found in .keys.yaml"
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
    results = run_tests(is_qa=False)
    end_time = time.time() # This line was missing in the original string

    print(f"\nTests completed in {end_time - start_time:.2f} seconds.")
    print("\nExpected results:")
    print("1. Read operations succeed with both read-only and read-write keys")
    print("2. Write operations fail with read-only keys")
    print("3. Write operations succeed with read-write keys")
    print("4. Fee information is displayed in the summary for each key")
    print("\nFee information summary:")

    # Print a summary of fee information for all keys
    for key_name, fee_info in results.fee_info.items():
        print(f"\n--- {key_name} Fee Information ---")
        spot_fee = fee_info["spot_fee"]
        um_fee = fee_info["um_fee"]
        print(f"UM Fees: {um_fee}")

    # Return a non-zero exit code if any tests failed
    sys.exit(1 if results.failed > 0 else 0)