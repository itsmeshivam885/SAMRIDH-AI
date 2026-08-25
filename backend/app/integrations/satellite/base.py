from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseSatelliteProvider(ABC):
    """Interface for Sentinel-2 / ISRO Bhuvan multispectral imagery & indices"""

    @abstractmethod
    def get_latest_observation(self, farm_id: str, lat: float, lon: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_historical_ndvi_series(self, farm_id: str, weeks: int = 8) -> List[Dict[str, Any]]:
        pass
