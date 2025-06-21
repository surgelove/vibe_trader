from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json


@dataclass
class PriceData:
    """Data structure for incoming price data"""
    date: datetime
    price: float
    symbol: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PriceData':
        """Create PriceData from dictionary"""
        if isinstance(data['date'], str):
            date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        else:
            date = data['date']
        
        return cls(
            date=date,
            price=float(data['price']),
            symbol=data.get('symbol')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PriceData':
        """Create PriceData from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'date': self.date.isoformat(),
            'price': self.price,
            'symbol': self.symbol
        }
    
    def __str__(self) -> str:
        return f"PriceData(date={self.date}, price={self.price}, symbol={self.symbol})"
