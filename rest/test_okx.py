#!/usr/bin/env python3
"""
Test script for OkxApi implementation.
This script tests the OkxApi class by creating an instance and calling its methods.
"""

from api_tester.rest.okx import OkxApi

def main():
    """
    Main function to test OkxApi implementation.
    """
    # Replace with your API credentials
    api_key = "YOUR_API_KEY"
    api_secret = "YOUR_API_SECRET"
    passphrase = "YOUR_PASSPHRASE"
    
    # Use simulated trading for testing
    use_simulated = True
    
    # Create an instance of OkxApi
    print("Initializing OkxApi...")
    okx_api = OkxApi(
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        spot_symbol="BTC-USDT",
        perp_symbol="BTC-USDT-SWAP",
        quantity=0.001,
        use_simulated=use_simulated
    )
    
    # Test read methods (these are safer to test first)
    print("\nTesting read methods:")
    
    print("\n1. Testing get_spot_config():")
    try:
        result = okx_api.get_spot_config()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Testing get_spot_balance():")
    try:
        result = okx_api.get_spot_balance()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing get_spot_price():")
    try:
        result = okx_api.get_spot_price()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Testing get_fut_position():")
    try:
        result = okx_api.get_fut_position()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n5. Testing get_perp_market_config():")
    try:
        result = okx_api.get_perp_market_config()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n6. Testing get_spot_open_orders():")
    try:
        result = okx_api.get_spot_open_orders()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n7. Testing get_fut_open_orders():")
    try:
        result = okx_api.get_fut_open_orders()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n8. Testing get_fut_balance():")
    try:
        result = okx_api.get_fut_balance()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Uncomment the following to test write methods (use with caution)
    # These methods can create real orders if use_simulated=False
    
    # print("\nTesting write methods (CAUTION - these can create real orders):")
    
    # print("\n9. Testing buy_spot():")
    # try:
    #     result = okx_api.buy_spot()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    # print("\n10. Testing sell_spot():")
    # try:
    #     result = okx_api.sell_spot()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    # print("\n11. Testing open_long_fut():")
    # try:
    #     result = okx_api.open_long_fut()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    # print("\n12. Testing close_long_fut():")
    # try:
    #     result = okx_api.close_long_fut()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    # print("\n13. Testing cancel_spot_open_orders():")
    # try:
    #     result = okx_api.cancel_spot_open_orders()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    # print("\n14. Testing cancel_fut_open_orders():")
    # try:
    #     result = okx_api.cancel_fut_open_orders()
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")

    # print("\n15. Testing funds_transfer():")
    # try:
    #     # Example: Transfer 0.0001 USDT from Funding to Trading account
    #     result = okx_api.funds_transfer(
    #         ccy="USDT",
    #         amt="0.0001",
    #         from_account="6",  # Funding account
    #         to_account="18"    # Trading account
    #     )
    #     print(f"Result: {result}")
    # except Exception as e:
    #     print(f"Error: {e}")

if __name__ == "__main__":
    main()
