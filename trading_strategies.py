from abc import ABC, abstractmethod
from typing import List
from models import PriceData
import logging

logger = logging.getLogger(__name__)


class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def analyze(self, data: PriceData, history: List[PriceData]) -> str:
        """
        Analyze price data and return trading signal
        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        pass


class SimpleMovingAverageStrategy(TradingStrategy):
    """Simple moving average crossover strategy"""
    
    def __init__(self, short_window: int = 5, long_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
    
    def analyze(self, data: PriceData, history: List[PriceData]) -> str:
        """Analyze using moving average crossover"""
        if len(history) < self.long_window:
            return 'HOLD'  # Not enough data
        
        # Get recent prices
        recent_prices = [d.price for d in history[-self.long_window:]]
        
        # Calculate moving averages
        short_ma = sum(recent_prices[-self.short_window:]) / self.short_window
        long_ma = sum(recent_prices) / self.long_window
        
        # Previous short MA for trend detection
        if len(history) >= self.long_window + 1:
            prev_prices = [d.price for d in history[-self.long_window-1:-1]]
            prev_short_ma = sum(prev_prices[-self.short_window:]) / self.short_window
            
            # Crossover detection
            if short_ma > long_ma and prev_short_ma <= sum(prev_prices) / self.long_window:
                return 'BUY'
            elif short_ma < long_ma and prev_short_ma >= sum(prev_prices) / self.long_window:
                return 'SELL'
        
        return 'HOLD'


class RSIStrategy(TradingStrategy):
    """Relative Strength Index (RSI) strategy"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def analyze(self, data: PriceData, history: List[PriceData]) -> str:
        """Analyze using RSI"""
        if len(history) < self.period + 1:
            return 'HOLD'
        
        # Calculate price changes
        prices = [d.price for d in history[-self.period-1:]]
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [change if change > 0 else 0 for change in price_changes]
        losses = [-change if change < 0 else 0 for change in price_changes]
        
        # Calculate average gains and losses
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        # Calculate RSI
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        if rsi < self.oversold:
            return 'BUY'
        elif rsi > self.overbought:
            return 'SELL'
        else:
            return 'HOLD'


class MomentumStrategy(TradingStrategy):
    """Price momentum strategy"""
    
    def __init__(self, lookback_period: int = 10, threshold: float = 0.02):
        self.lookback_period = lookback_period
        self.threshold = threshold  # 2% threshold
    
    def analyze(self, data: PriceData, history: List[PriceData]) -> str:
        """Analyze using price momentum"""
        if len(history) < self.lookback_period:
            return 'HOLD'
        
        # Calculate momentum (price change over lookback period)
        current_price = data.price
        past_price = history[-self.lookback_period].price
        
        momentum = (current_price - past_price) / past_price
        
        if momentum > self.threshold:
            return 'BUY'
        elif momentum < -self.threshold:
            return 'SELL'
        else:
            return 'HOLD'
