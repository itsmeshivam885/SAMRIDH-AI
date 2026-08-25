import uuid
from typing import Dict, Any
from app.integrations.pmfby.base import BasePMFBYAdapter


class MockPMFBYAdapter(BasePMFBYAdapter):
    """
    Realistic mock implementation for PMFBY integration.
    Clearly marked as DEMO / SIMULATED DATA per system rules.
    """

    def verify_farmer_policy(self, farmer_id_or_phone: str, policy_number: str) -> Dict[str, Any]:
        return {
            "is_valid": True,
            "policy_number": policy_number or "PMFBY-2026-MP-984210",
            "scheme_name": "Pradhan Mantri Fasal Bima Yojana (Kharif 2026)",
            "insurer_name": "Agriculture Insurance Company of India (AIC)",
            "premium_paid_by_farmer_inr": 1200.0,
            "government_subsidy_inr": 4800.0,
            "total_coverage_sum_insured_inr": 120000.0,
            "status": "ACTIVE_ENROLLED",
            "is_mock_demo": True,
        }

    def calculate_estimated_payout(
        self,
        sum_insured_per_ha: float,
        farm_area_ha: float,
        damage_percentage: float,
        loss_category: str
    ) -> Dict[str, Any]:
        # Theoretical loss formula: Total Sum Insured * (Damage Percentage / 100)
        total_sum_insured = sum_insured_per_ha * farm_area_ha
        raw_payout = total_sum_insured * (damage_percentage / 100.0)

        # Standard PMFBY deductible / threshold rule consideration
        # If damage is below 15%, localized claim threshold is not met
        eligible = damage_percentage >= 15.0
        payable_amount = round(raw_payout, 2) if eligible else 0.0

        return {
            "total_sum_insured_inr": round(total_sum_insured, 2),
            "damage_percentage": round(damage_percentage, 1),
            "estimated_payout_inr": payable_amount,
            "is_eligible_for_claim": eligible,
            "disclaimer": "DEMO ONLY: Official PMFBY settlement requires field officer survey & district committee sanction.",
            "is_mock_demo": True,
        }

    def submit_claim_intimation(self, claim_payload: Dict[str, Any]) -> Dict[str, Any]:
        docket_no = f"PMFBY-INT-{uuid.uuid4().hex[:8].upper()}"
        return {
            "success": True,
            "intimation_docket_number": docket_no,
            "status": "ACCEPTED_FOR_SURVEY",
            "message": "Claim intimation registered with National PMFBY Loss Intimation Gateway (DEMO).",
            "is_mock_demo": True,
        }


pmfby_adapter = MockPMFBYAdapter()
