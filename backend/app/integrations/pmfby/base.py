from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePMFBYAdapter(ABC):
    """Abstract interface for PMFBY national portal & PFMS disbursement integration"""

    @abstractmethod
    def verify_farmer_policy(self, farmer_id_or_phone: str, policy_number: str) -> Dict[str, Any]:
        """Verify farmer enrollment in PMFBY scheme"""
        pass

    @abstractmethod
    def calculate_estimated_payout(
        self,
        sum_insured_per_ha: float,
        farm_area_ha: float,
        damage_percentage: float,
        loss_category: str
    ) -> Dict[str, Any]:
        """Compute estimated claim assistance based on PMFBY guidelines"""
        pass

    @abstractmethod
    def submit_claim_intimation(self, claim_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit claim docket to insurer gateway"""
        pass
