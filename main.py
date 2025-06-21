import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from collections import deque

from models import PriceData
from data_listener import DataListener, MockDataListener, FileDataListener
from trading_strategies import TradingStrategy, SimpleMovingAverageStrategy, RSIStrategy, MomentumStrategy


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingAssistant:
    """Main trading assistant class that orchestrates data listening and strategy execution"""
    
    def __init__(self, max_history: int = 1000):
        self.data_listener: Optional[DataListener] = None
        self.strategies: List[TradingStrategy] = []
        self.price_history: deque = deque(maxlen=max_history)
        self.running = False
        self.stats = {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'hold_signals': 0,
            'last_signal': None,
            'last_price': None,
            'start_time': None
        }
    
    def add_strategy(self, strategy: TradingStrategy) -> None:
        """Add a trading strategy to the assistant"""
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.__class__.__name__}")
    
    def set_data_listener(self, listener: DataListener) -> None:
        """Set the data listener for receiving price data"""
        self.data_listener = listener
        logger.info(f"Set data listener: {listener.__class__.__name__}")
    
    async def on_data_received(self, data: PriceData) -> None:
        """Callback function called when new price data is received"""
        try:
            # Add to history
            self.price_history.append(data)
            
            # Update stats
            self.stats['last_price'] = data.price
            
            logger.info(f"Received: {data}")
            
            # Run strategies if we have any
            if self.strategies:
                await self._analyze_with_strategies(data)
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
    
    async def _analyze_with_strategies(self, data: PriceData) -> None:
        """Analyze data with all configured strategies"""
        history_list = list(self.price_history)
        
        for strategy in self.strategies:
            try:
                signal = strategy.analyze(data, history_list)
                
                if signal and signal != 'HOLD':
                    self.stats['total_signals'] += 1
                    self.stats['last_signal'] = signal
                    
                    if signal == 'BUY':
                        self.stats['buy_signals'] += 1
                    elif signal == 'SELL':
                        self.stats['sell_signals'] += 1
                    else:
                        self.stats['hold_signals'] += 1
                    
                    logger.info(f"🔔 {strategy.__class__.__name__} Signal: {signal} at ${data.price}")
                    await self._execute_signal(signal, data, strategy)
                
            except Exception as e:
                logger.error(f"Error in strategy {strategy.__class__.__name__}: {e}")
    
    async def _execute_signal(self, signal: str, data: PriceData, strategy: TradingStrategy) -> None:
        """Execute trading signal (placeholder for actual trading logic)"""
        # This is where you would integrate with a real trading API
        # For now, we just log the signal
        timestamp = data.date.strftime('%Y-%m-%d %H:%M:%S')
        
        if signal == 'BUY':
            logger.info(f"📈 EXECUTE BUY: {data.symbol or 'UNKNOWN'} at ${data.price} ({timestamp})")
        elif signal == 'SELL':
            logger.info(f"📉 EXECUTE SELL: {data.symbol or 'UNKNOWN'} at ${data.price} ({timestamp})")
    
    def print_stats(self) -> None:
        """Print current statistics"""
        print("\n" + "="*50)
        print("📊 Trading Assistant Statistics")
        print("="*50)
        print(f"Running time: {datetime.now() - self.stats['start_time'] if self.stats['start_time'] else 'Not started'}")
        print(f"Price history: {len(self.price_history)} data points")
        print(f"Last price: ${self.stats['last_price']}")
        print(f"Total signals: {self.stats['total_signals']}")
        print(f"  • Buy signals: {self.stats['buy_signals']}")
        print(f"  • Sell signals: {self.stats['sell_signals']}")
        print(f"  • Hold signals: {self.stats['hold_signals']}")
        print(f"Last signal: {self.stats['last_signal']}")
        print(f"Active strategies: {len(self.strategies)}")
        for i, strategy in enumerate(self.strategies, 1):
            print(f"  {i}. {strategy.__class__.__name__}")
        print("="*50)
    
    async def start(self) -> None:
        """Start the trading assistant"""
        if not self.data_listener:
            raise ValueError("No data listener configured")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info("🚀 Starting Trading Assistant")
        logger.info(f"Configured with {len(self.strategies)} strategies")
        
        try:
            await self.data_listener.start(self.on_data_received)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Error in trading assistant: {e}")
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the trading assistant"""
        logger.info("🛑 Stopping Trading Assistant")
        self.running = False
        
        if self.data_listener:
            await self.data_listener.stop()
        
        self.print_stats()


async def main():
    """Main function demonstrating the trading assistant"""
    print("🤖 Automated Trading Assistant")
    print("="*40)
    
    # Create trading assistant
    assistant = TradingAssistant(max_history=100)
    
    # Add trading strategies
    assistant.add_strategy(SimpleMovingAverageStrategy(short_window=5, long_window=20))
    assistant.add_strategy(RSIStrategy(period=14, oversold=30, overbought=70))
    assistant.add_strategy(MomentumStrategy(lookback_period=10, threshold=0.015))
    
    # Configure data source
    print("\nSelect data source:")
    print("1. Mock data (simulated)")
    print("2. File data (from JSON file)")
    print("3. WebSocket (custom URL)")
    
    try:
        choice = input("Enter choice (1-3) [default: 1]: ").strip() or "1"
        
        if choice == "1":
            # Use mock data
            listener = MockDataListener(symbol="BTC-USD", interval=2.0, base_price=50000.0)
            assistant.set_data_listener(listener)
            
        elif choice == "2":
            # Use file data
            file_path = input("Enter file path [default: sample_data.json]: ").strip() or "sample_data.json"
            
            # Create sample file if it doesn't exist
            try:
                with open(file_path, 'r') as f:
                    pass  # File exists
            except FileNotFoundError:
                print(f"Creating sample data file: {file_path}")
                await create_sample_data_file(file_path)
            
            listener = FileDataListener(file_path, interval=1.0)
            assistant.set_data_listener(listener)
            
        elif choice == "3":
            # Use WebSocket
            url = input("Enter WebSocket URL: ").strip()
            if not url:
                print("No URL provided, using mock data instead")
                listener = MockDataListener(symbol="BTC-USD", interval=2.0, base_price=50000.0)
            else:
                # Note: WebSocket listener requires websockets package
                print("WebSocket listener requires 'websockets' package")
                print("Using mock data instead for this demo")
                listener = MockDataListener(symbol="BTC-USD", interval=2.0, base_price=50000.0)
            
            assistant.set_data_listener(listener)
            
        else:
            print("Invalid choice, using mock data")
            listener = MockDataListener(symbol="BTC-USD", interval=2.0, base_price=50000.0)
            assistant.set_data_listener(listener)
        
        print(f"\n🎯 Starting with {listener.__class__.__name__}")
        print("Press Ctrl+C to stop the assistant\n")
        
        # Start the assistant
        await assistant.start()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error in main: {e}")


async def create_sample_data_file(file_path: str):
    """Create a sample JSON data file for testing"""
    import json
    from datetime import datetime, timedelta
    import random
    
    sample_data = []
    base_price = 50000.0
    start_time = datetime.now() - timedelta(hours=1)
    
    for i in range(60):  # 60 data points
        # Simulate price movement
        change = random.uniform(-0.02, 0.02)  # ±2%
        base_price *= (1 + change)
        
        data_point = {
            "date": (start_time + timedelta(minutes=i)).isoformat(),
            "price": round(base_price, 2),
            "symbol": "BTC-USD"
        }
        sample_data.append(json.dumps(data_point))
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(sample_data))
    
    print(f"Created {len(sample_data)} sample data points in {file_path}")


if __name__ == "__main__":
    asyncio.run(main())
