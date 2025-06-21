#!/usr/bin/env python3
"""
Quick start script for the Vibe Trader Assistant
"""
import asyncio
import sys
from main import TradingAssistant
from data_listener import MockDataListener, FileDataListener
from trading_strategies import SimpleMovingAverageStrategy, RSIStrategy, MomentumStrategy


async def quick_demo():
    """Run a quick demo with default settings"""
    print("🚀 Vibe Trader - Quick Demo")
    print("="*40)
    print("Starting with mock data and default strategies...")
    print("Press Ctrl+C to stop\n")
    
    # Create assistant with default configuration
    assistant = TradingAssistant(max_history=100)
    
    # Add all available strategies
    assistant.add_strategy(SimpleMovingAverageStrategy(short_window=5, long_window=15))
    assistant.add_strategy(RSIStrategy(period=12, oversold=35, overbought=65))
    assistant.add_strategy(MomentumStrategy(lookback_period=8, threshold=0.015))
    
    # Use mock data with reasonable settings
    listener = MockDataListener(
        symbol="BTC-USD", 
        interval=3.0,  # Update every 3 seconds
        base_price=50000.0
    )
    assistant.set_data_listener(listener)
    
    # Start the assistant
    await assistant.start()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Quick demo mode
        try:
            asyncio.run(quick_demo())
        except KeyboardInterrupt:
            print("\n👋 Demo stopped. Thanks for trying Vibe Trader!")
    else:
        # Full interactive mode
        from main import main
        asyncio.run(main())
