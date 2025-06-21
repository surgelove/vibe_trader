#!/usr/bin/env python3
"""
Simple test script for the trading assistant
"""
import asyncio
import logging
from datetime import datetime, timedelta
import json

from models import PriceData
from data_listener import MockDataListener, FileDataListener
from trading_strategies import SimpleMovingAverageStrategy, RSIStrategy, MomentumStrategy
from main import TradingAssistant


async def create_test_data_file():
    """Create test data file with realistic price movements"""
    import random
    
    data_points = []
    base_price = 50000.0
    start_time = datetime.now() - timedelta(hours=2)
    
    # Generate 120 data points (2 hours of minute data)
    for i in range(120):
        # Add some realistic volatility
        change = random.gauss(0, 0.01)  # Normal distribution with 1% std dev
        base_price *= (1 + change)
        base_price = max(base_price, 1000)  # Prevent negative prices
        
        data_point = {
            "date": (start_time + timedelta(minutes=i)).isoformat(),
            "price": round(base_price, 2),
            "symbol": "BTC-USD"
        }
        data_points.append(json.dumps(data_point))
    
    with open("test_data.json", "w") as f:
        f.write("\n".join(data_points))
    
    print(f"Created test_data.json with {len(data_points)} data points")


async def test_mock_data():
    """Test with mock data"""
    print("🧪 Testing with Mock Data")
    print("-" * 30)
    
    assistant = TradingAssistant(max_history=50)
    
    # Add strategies
    assistant.add_strategy(SimpleMovingAverageStrategy(short_window=3, long_window=10))
    assistant.add_strategy(MomentumStrategy(lookback_period=5, threshold=0.01))
    
    # Use mock data with faster updates for testing
    listener = MockDataListener(symbol="TEST-USD", interval=0.5, base_price=1000.0)
    assistant.set_data_listener(listener)
    
    print("Running for 10 seconds...")
    
    # Run for a limited time
    task = asyncio.create_task(assistant.start())
    await asyncio.sleep(10)
    await assistant.stop()
    
    print("✅ Mock data test completed")


async def test_file_data():
    """Test with file data"""
    print("\n🧪 Testing with File Data")
    print("-" * 30)
    
    # Create test data
    await create_test_data_file()
    
    assistant = TradingAssistant(max_history=100)
    
    # Add all strategies
    assistant.add_strategy(SimpleMovingAverageStrategy(short_window=5, long_window=15))
    assistant.add_strategy(RSIStrategy(period=10, oversold=35, overbought=65))
    assistant.add_strategy(MomentumStrategy(lookback_period=8, threshold=0.008))
    
    # Use file data
    listener = FileDataListener("test_data.json", interval=0.1)  # Fast playback
    assistant.set_data_listener(listener)
    
    print("Processing file data...")
    await assistant.start()
    
    print("✅ File data test completed")


async def test_single_data_point():
    """Test processing a single data point"""
    print("\n🧪 Testing Single Data Point Processing")
    print("-" * 40)
    
    assistant = TradingAssistant()
    assistant.add_strategy(SimpleMovingAverageStrategy())
    
    # Create some sample data
    test_data = [
        PriceData(datetime.now() - timedelta(minutes=i), 50000 + i*10, "BTC-USD")
        for i in range(25, 0, -1)  # 25 data points going backwards in time
    ]
    
    # Add to history
    for data in test_data:
        assistant.price_history.append(data)
    
    # Test with new data point
    new_data = PriceData(datetime.now(), 50500.0, "BTC-USD")
    await assistant.on_data_received(new_data)
    
    print("✅ Single data point test completed")


async def main():
    """Run all tests"""
    print("🚀 Trading Assistant Test Suite")
    print("=" * 40)
    
    # Set logging to show more details during testing
    logging.getLogger().setLevel(logging.INFO)
    
    try:
        await test_single_data_point()
        await test_mock_data()
        await test_file_data()
        
        print("\n🎉 All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.exception("Test error details:")


if __name__ == "__main__":
    asyncio.run(main())
