# 🤖 Vibe Trader - Automated Trading Assistant

An advanced automated trading assistant that listens to streaming price data and executes trading strategies in real-time.

## 🚀 Features

- **Real-time Data Processing**: Handles streaming price data with date and price fields
- **Multiple Data Sources**: Support for WebSocket, file-based, and mock data streams
- **Trading Strategies**: Built-in strategies including Moving Average, RSI, and Momentum
- **Extensible Architecture**: Easy to add new strategies and data sources
- **Comprehensive Logging**: Detailed logging and statistics tracking
- **Async/Await Support**: High-performance asynchronous processing

## 📁 Project Structure

```
vibe_trader/
├── main.py                 # Main application entry point
├── models.py               # Data models (PriceData)
├── data_listener.py        # Data listener implementations
├── trading_strategies.py   # Trading strategy implementations
├── test_assistant.py       # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠 Installation

1. **Clone the repository**:
   ```bash
   cd /Users/code/source/vibe_trader
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Install WebSocket support**:
   ```bash
   pip install websockets
   ```

## 🎯 Quick Start

### Run the Interactive Assistant

```bash
python main.py
```

This will start an interactive session where you can choose:
1. **Mock Data**: Simulated price data for testing
2. **File Data**: Read from JSON file
3. **WebSocket**: Connect to real-time data stream

### Run Tests

```bash
python test_assistant.py
```

## 📊 Data Format

The assistant expects streaming data with the following JSON format:

```json
{
  "date": "2025-06-21T10:30:00",
  "price": 50000.50,
  "symbol": "BTC-USD"
}
```

- `date`: ISO format timestamp
- `price`: Numeric price value
- `symbol`: Optional trading symbol

## 🧠 Trading Strategies

### 1. Simple Moving Average (SMA)
- **Strategy**: Crossover of short-term and long-term moving averages
- **Signals**: BUY when short MA crosses above long MA, SELL when below
- **Parameters**: `short_window`, `long_window`

### 2. Relative Strength Index (RSI)
- **Strategy**: Momentum oscillator (0-100 scale)
- **Signals**: BUY when RSI < oversold threshold, SELL when RSI > overbought
- **Parameters**: `period`, `oversold`, `overbought`

### 3. Momentum Strategy
- **Strategy**: Price momentum over a lookback period
- **Signals**: BUY/SELL based on momentum threshold
- **Parameters**: `lookback_period`, `threshold`

## 🔧 Usage Examples

### Basic Usage with Mock Data

```python
import asyncio
from main import TradingAssistant
from data_listener import MockDataListener
from trading_strategies import SimpleMovingAverageStrategy

async def example():
    # Create assistant
    assistant = TradingAssistant()
    
    # Add strategy
    assistant.add_strategy(SimpleMovingAverageStrategy(short_window=5, long_window=20))
    
    # Set data source
    listener = MockDataListener(symbol="BTC-USD", interval=1.0, base_price=50000.0)
    assistant.set_data_listener(listener)
    
    # Start processing
    await assistant.start()

asyncio.run(example())
```

### Custom Strategy Implementation

```python
from trading_strategies import TradingStrategy
from models import PriceData
from typing import List

class MyCustomStrategy(TradingStrategy):
    def __init__(self, my_parameter: float = 0.02):
        self.my_parameter = my_parameter
    
    def analyze(self, data: PriceData, history: List[PriceData]) -> str:
        # Your custom logic here
        if len(history) < 10:
            return 'HOLD'
        
        # Example: Simple price change strategy
        recent_avg = sum(d.price for d in history[-5:]) / 5
        if data.price > recent_avg * (1 + self.my_parameter):
            return 'BUY'
        elif data.price < recent_avg * (1 - self.my_parameter):
            return 'SELL'
        
        return 'HOLD'
```

### File-based Data Source

Create a JSON file with price data:

```json
{"date": "2025-06-21T10:00:00", "price": 50000.0, "symbol": "BTC-USD"}
{"date": "2025-06-21T10:01:00", "price": 50050.0, "symbol": "BTC-USD"}
{"date": "2025-06-21T10:02:00", "price": 49980.0, "symbol": "BTC-USD"}
```

Then use the FileDataListener:

```python
from data_listener import FileDataListener

listener = FileDataListener("my_data.json", interval=1.0)
assistant.set_data_listener(listener)
```

## 📈 Output Example

```
🚀 Starting Trading Assistant
Configured with 3 strategies
Received: PriceData(date=2025-06-21 10:30:15, price=50250.0, symbol=BTC-USD)
🔔 SimpleMovingAverageStrategy Signal: BUY at $50250.0
📈 EXECUTE BUY: BTC-USD at $50250.0 (2025-06-21 10:30:15)
Received: PriceData(date=2025-06-21 10:30:17, price=50180.0, symbol=BTC-USD)
🔔 MomentumStrategy Signal: SELL at $50180.0
📉 EXECUTE SELL: BTC-USD at $50180.0 (2025-06-21 10:30:17)
```

## 🎛 Configuration Options

### TradingAssistant Parameters
- `max_history`: Maximum number of price points to keep in memory (default: 1000)

### Strategy Parameters
- **SimpleMovingAverageStrategy**: `short_window=5`, `long_window=20`
- **RSIStrategy**: `period=14`, `oversold=30`, `overbought=70`
- **MomentumStrategy**: `lookback_period=10`, `threshold=0.02`

### Data Listener Parameters
- **MockDataListener**: `symbol`, `interval`, `base_price`
- **FileDataListener**: `file_path`, `interval`
- **WebSocketDataListener**: `uri`, `reconnect_interval`

## 🔍 Monitoring & Statistics

The assistant provides real-time statistics:

```
📊 Trading Assistant Statistics
==================================================
Running time: 0:05:23.456789
Price history: 323 data points
Last price: $50,234.56
Total signals: 15
  • Buy signals: 7
  • Sell signals: 8
  • Hold signals: 0
Last signal: SELL
Active strategies: 3
  1. SimpleMovingAverageStrategy
  2. RSIStrategy
  3. MomentumStrategy
==================================================
```

## 🧪 Testing

The project includes comprehensive tests in `test_assistant.py`:

- **Single Data Point Test**: Validates strategy execution
- **Mock Data Test**: Tests with simulated streaming data
- **File Data Test**: Tests with historical data playback

## 🚨 Error Handling

The assistant includes robust error handling:
- **Connection Issues**: Automatic reconnection for WebSocket sources
- **Data Parsing Errors**: Graceful handling of malformed data
- **Strategy Errors**: Isolated error handling prevents one strategy from affecting others
- **Graceful Shutdown**: Clean shutdown on Ctrl+C

## 🔮 Future Enhancements

- [ ] Integration with real trading APIs (Binance, Coinbase, etc.)
- [ ] Portfolio management and position tracking
- [ ] Risk management features
- [ ] Backtesting framework
- [ ] Web-based dashboard
- [ ] Email/SMS notifications
- [ ] Machine learning strategies
- [ ] Multi-asset support

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Happy Trading! 📈💰**
