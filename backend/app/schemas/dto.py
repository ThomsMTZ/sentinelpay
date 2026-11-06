from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    DOWNGRADED = "DOWNGRADED"


class RiskCategory(str, Enum):
    DORMANT_ZOMBIE = "DORMANT_ZOMBIE"
    OVERPROVISIONED_SEATS = "OVERPROVISIONED_SEATS"
    DUPLICATE_SAAS = "DUPLICATE_SAAS"
    TRIAL_TRAP_CONVERSION = "TRIAL_TRAP_CONVERSION"
    HIDDEN_MICRO_TX = "HIDDEN_MICRO_TX"
    HEALTHY_HIGH_ROI = "HEALTHY_HIGH_ROI"


class ActionType(str, Enum):
    CANCEL_SUBSCRIPTION = "CANCEL_SUBSCRIPTION"
    SUSPEND_SUBSCRIPTION = "SUSPEND_SUBSCRIPTION"
    DOWNGRADE_PLAN = "DOWNGRADE_PLAN"
    AUTONOMOUS_PURCHASE = "AUTONOMOUS_PURCHASE"
    AUTONOMOUS_SWITCH = "AUTONOMOUS_SWITCH"
    WEBHOOK_REFUND_INTERCEPT = "WEBHOOK_REFUND_INTERCEPT"
    KEEP_ACTIVE = "KEEP_ACTIVE"


class ApprovalStatus(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    PENDING_1CLICK_APPROVAL = "PENDING_1CLICK_APPROVAL"
    APPROVED_BY_USER = "APPROVED_BY_USER"
    REJECTED_BY_GUARDRAIL = "REJECTED_BY_GUARDRAIL"
    EXECUTED = "EXECUTED"


class UsageTelemetryDTO(BaseModel):
    active_days_last_30d: int = Field(..., ge=0, le=30)
    days_since_last_login: int = Field(..., ge=0)
    provisioned_seats: int = Field(default=1, ge=1)
    active_seats: int = Field(default=1, ge=0)
    monthly_api_or_feature_events: int = Field(default=0, ge=0)
    overlapping_tool_name: str | None = None
    price_change_pct_last_90d: float = 0.0
    previous_monthly_cost: float = 0.0
    price_history_6m: list[float] = Field(default_factory=list)
    raw_paypal_descriptor: str = ""
    is_trial_converting: bool = False
    trial_days_remaining: int | None = None
    has_data_retention_or_contract_lock: bool = False


class DowngradeOptionDTO(BaseModel):
    target_plan_id: str
    target_plan_name: str
    new_monthly_cost: float
    monthly_savings: float
    annual_savings: float


class SwitchAlternativeDTO(BaseModel):
    alternative_vendor: str
    alternative_plan: str
    new_monthly_cost: float
    annual_net_savings: float
    migration_rationale: str


class SubscriptionDTO(BaseModel):
    id: str = Field(..., description="Internal or PayPal Subscription ID (e.g., I-BW452GLLEP1G)")
    paypal_subscription_id: str
    paypal_plan_id: str
    vendor_name: str
    plan_name: str
    category: str
    monthly_cost: float
    currency: str = "USD"
    billing_cycle: str = "MONTHLY"
    next_billing_date: str
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    logo_text: str
    telemetry: UsageTelemetryDTO
    downgrade_option: DowngradeOptionDTO | None = None
    switch_alternative: SwitchAlternativeDTO | None = None
    # Computed by Audit Engine
    waste_score: int = Field(default=0, ge=0, le=100)
    risk_category: RiskCategory = RiskCategory.HEALTHY_HIGH_ROI
    recommended_action: ActionType = ActionType.KEEP_ACTIVE
    estimated_annual_savings: float = 0.0
    ai_audit_rationale: str = ""
    cost_per_active_day: float = 0.0


class BudgetPolicyDTO(BaseModel):
    monthly_autonomous_limit: float = Field(default=150.0, ge=0.0)
    current_month_autonomous_spend: float = Field(default=18.0, ge=0.0)
    auto_approve_threshold: float = Field(default=25.0, ge=0.0)
    require_1click_above_threshold: bool = True
    allow_autonomous_cancellations: bool = True
    allow_autonomous_downgrades: bool = True
    whitelisted_categories: list[str] = Field(
        default_factory=lambda: ["Cloud & AI Compute", "Developer Tools", "Security & Infra", "Productivity SaaS"]
    )


class GuardrailEvaluationDTO(BaseModel):
    passed: bool
    approval_status: ApprovalStatus
    policy_rule_triggered: str
    reason: str
    remaining_monthly_budget: float


class PayPalExecutionReceiptDTO(BaseModel):
    paypal_request_id: str
    paypal_resource_id: str
    endpoint: str
    http_method: str
    http_status: int
    execution_mode: str = Field(description="SANDBOX_LIVE or SANDBOX_SIMULATED")
    status_text: str
    approval_url: str | None = None
    raw_response: dict[str, Any] = Field(default_factory=dict)
    executed_at: str


class AgentActionProposalDTO(BaseModel):
    proposal_id: str
    action_type: ActionType
    target_subscription_id: str | None = None
    vendor_name: str
    title: str
    description: str
    amount_usd: float = 0.0
    monthly_savings_usd: float = 0.0
    annual_savings_usd: float = 0.0
    confidence_score: float = Field(default=0.95, ge=0.0, le=1.0)
    ai_reasoning: str
    negotiation_message: str | None = None
    guardrail: GuardrailEvaluationDTO
    paypal_receipt: PayPalExecutionReceiptDTO | None = None
    created_at: str


class AutonomousPurchaseRequestDTO(BaseModel):
    vendor_name: str = Field(..., min_length=2)
    item_name: str = Field(..., min_length=2)
    category: str = Field(default="Cloud & AI Compute")
    amount_usd: float = Field(..., gt=0.0)
    justification: str = Field(..., min_length=5)
    auto_execute_if_allowed: bool = True


class AgentChatCommandDTO(BaseModel):
    prompt: str = Field(..., min_length=2)
    auto_execute_safe_actions: bool = False


class CredentialsUpdateDTO(BaseModel):
    paypal_client_id: str | None = None
    paypal_client_secret: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str | None = None


class AuditTraceEventDTO(BaseModel):
    event_id: str
    timestamp: str
    stage: str = Field(description="AGENT_REASONING | GUARDRAIL_CHECK | PAYPAL_API | EXECUTION_RECEIPT")
    actor: str
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)
    sha256_hash: str
    prev_hash: str
