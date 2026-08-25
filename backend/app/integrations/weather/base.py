from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseWeatherProvider(ABC):
    """Interface for meteorological telemetry (IMD, Open-Meteo, AWS networks)"""

    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, Any]]:
        pass
