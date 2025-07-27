from enum import Enum
from typing import Any


class PaymentPlanType(Enum):
    """결제 플랜 타입"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class PaymentPlan:
    """결제 플랜 값 객체"""
    
    def __init__(self, plan: str):
        try:
            self.plan_type = PaymentPlanType(plan.lower())
        except ValueError:
            raise ValueError(f"Invalid payment plan: {plan}. Must be one of: free, pro, enterprise")
    
    @property
    def value(self) -> str:
        return self.plan_type.value
    
    def is_free(self) -> bool:
        return self.plan_type == PaymentPlanType.FREE
    
    def is_pro(self) -> bool:
        return self.plan_type == PaymentPlanType.PRO
    
    def is_enterprise(self) -> bool:
        return self.plan_type == PaymentPlanType.ENTERPRISE
    
    def is_paid(self) -> bool:
        """유료 플랜인지 확인"""
        return self.plan_type in [PaymentPlanType.PRO, PaymentPlanType.ENTERPRISE]
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, PaymentPlan):
            return False
        return self.plan_type == other.plan_type
    
    def __hash__(self) -> int:
        return hash(self.plan_type) 