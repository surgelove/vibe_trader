import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from models import PriceData


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataListener(ABC):
    """Abstract base class for data listeners"""
    
    @abstractmethod
    async def start(self, callback: Callable[[PriceData], None]) -> None:
        """Start listening for data and call callback with received data"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop listening for data"""
        pass


class WebSocketDataListener(DataListener):
    """WebSocket data listener for receiving streaming price data (requires websockets package)"""
    
    def __init__(self, uri: str, reconnect_interval: int = 5):
        self.uri = uri
        self.reconnect_interval = reconnect_interval
        self.websocket = None
        self.running = False
        self.callback = None
    
    async def start(self, callback: Callable[[PriceData], None]) -> None:
        """Start WebSocket connection and listen for data"""
        try:
            import websockets
        except ImportError:
            raise ImportError("websockets package is required for WebSocket listener. Install with: pip install websockets")
        
        self.callback = callback
        self.running = True
        
        while self.running:
            try:
                logger.info(f"Connecting to WebSocket: {self.uri}")
                async with websockets.connect(self.uri) as websocket:
                    self.websocket = websocket
                    logger.info("WebSocket connected successfully")
                    
                    async for message in websocket:
                        if not self.running:
                            break
                        
                        try:
                            # Parse incoming message as PriceData
                            price_data = PriceData.from_json(message)
                            logger.debug(f"Received data: {price_data}")
                            
                            # Call the callback with the parsed data
                            if self.callback:
                                await self._safe_callback(price_data)
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON: {e}")
                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            
            except Exception as e:
                if "ConnectionClosed" in str(type(e)):
                    logger.warning("WebSocket connection closed")
                else:
                    logger.error(f"WebSocket error: {e}")
            
            if self.running:
                logger.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)
    
    async def _safe_callback(self, data: PriceData) -> None:
        """Safely execute callback to prevent listener from crashing"""
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(data)
            else:
                self.callback(data)
        except Exception as e:
            logger.error(f"Error in callback: {e}")
    
    async def stop(self) -> None:
        """Stop the WebSocket listener"""
        logger.info("Stopping WebSocket listener")
        self.running = False
        if self.websocket:
            await self.websocket.close()


class FileDataListener(DataListener):
    """File-based data listener for testing purposes"""
    
    def __init__(self, file_path: str, interval: float = 1.0):
        self.file_path = file_path
        self.interval = interval
        self.running = False
    
    async def start(self, callback: Callable[[PriceData], None]) -> None:
        """Start reading data from file and simulate streaming"""
        self.running = True
        
        try:
            with open(self.file_path, 'r') as file:
                logger.info(f"Reading data from file: {self.file_path}")
                
                for line in file:
                    if not self.running:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        price_data = PriceData.from_json(line)
                        logger.debug(f"File data: {price_data}")
                        
                        if asyncio.iscoroutinefunction(callback):
                            await callback(price_data)
                        else:
                            callback(price_data)
                        
                        await asyncio.sleep(self.interval)
                        
                    except Exception as e:
                        logger.error(f"Error processing line: {e}")
                        
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
        except Exception as e:
            logger.error(f"File reading error: {e}")
    
    async def stop(self) -> None:
        """Stop the file listener"""
        logger.info("Stopping file listener")
        self.running = False


class MockDataListener(DataListener):
    """Mock data listener for testing - generates sample price data"""
    
    def __init__(self, symbol: str = "BTC-USD", interval: float = 1.0, base_price: float = 50000.0):
        self.symbol = symbol
        self.interval = interval
        self.base_price = base_price
        self.running = False
    
    async def start(self, callback: Callable[[PriceData], None]) -> None:
        """Start generating mock price data"""
        self.running = True
        import random
        
        logger.info(f"Starting mock data generation for {self.symbol}")
        
        current_price = self.base_price
        
        while self.running:
            try:
                # Generate realistic price movement
                change_percent = random.uniform(-0.02, 0.02)  # ±2% change
                current_price *= (1 + change_percent)
                
                price_data = PriceData(
                    date=datetime.now(),
                    price=round(current_price, 2),
                    symbol=self.symbol
                )
                
                logger.debug(f"Generated mock data: {price_data}")
                
                if asyncio.iscoroutinefunction(callback):
                    await callback(price_data)
                else:
                    callback(price_data)
                
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                logger.error(f"Error generating mock data: {e}")
    
    async def stop(self) -> None:
        """Stop the mock data generator"""
        logger.info("Stopping mock data generation")
        self.running = False
