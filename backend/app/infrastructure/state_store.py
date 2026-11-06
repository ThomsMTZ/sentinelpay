from app.core.config import settings
from app.schemas.dto import (
    AgentActionProposalDTO,
    BudgetPolicyDTO,
    DowngradeOptionDTO,
    SubscriptionDTO,
    SubscriptionStatus,
    SwitchAlternativeDTO,
    UsageTelemetryDTO,
)


def build_initial_subscriptions() -> list[SubscriptionDTO]:
    """
    Returns a realistic SaaS & recurring micro-transaction portfolio linked to
    PayPal Sandbox billing agreement IDs for immediate auditing and live remediation.
    """
    return [
        SubscriptionDTO(
            id="SUB-CLOUDGPU-01",
            paypal_subscription_id="I-BW452GLLEP1G",
            paypal_plan_id="P-5ML4271244454362WXNWU5NQ",
            vendor_name="CloudGPU Studio Pro",
            plan_name="Dedicated A100 Interactive Workspace",
            category="Cloud & AI Compute",
            monthly_cost=89.00,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-14",
            status=SubscriptionStatus.ACTIVE,
            logo_text="CG",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=0,
                days_since_last_login=52,
                provisioned_seats=1,
                active_seats=0,
                monthly_api_or_feature_events=0,
                overlapping_tool_name=None,
                price_change_pct_last_90d=18.7,
                previous_monthly_cost=75.00,
                price_history_6m=[75.0, 75.0, 75.0, 82.0, 89.0, 89.0],
                raw_paypal_descriptor="PP*FASTSPRG-CGPU88",
                is_trial_converting=False,
                has_data_retention_or_contract_lock=False,
            ),
            switch_alternative=SwitchAlternativeDTO(
                alternative_vendor="RunPod Serverless GPU",
                alternative_plan="Pay-As-You-Go Spot A100",
                new_monthly_cost=19.00,
                annual_net_savings=840.00,
                migration_rationale="Remplace le workspace A100 dédié inactif à 89 $/mois par du GPU Serverless à la demande (19 $/mois), économisant 840 $/an sans perdre la capacité IA.",
            ),
        ),
        SubscriptionDTO(
            id="SUB-DESIGNFLOW-02",
            paypal_subscription_id="I-9X821KLLQP9M",
            paypal_plan_id="P-8ENT992100454362WXNWU9LP",
            vendor_name="DesignFlow Enterprise",
            plan_name="Enterprise Team Plan (10 Seats)",
            category="Productivity SaaS",
            monthly_cost=120.00,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-18",
            status=SubscriptionStatus.ACTIVE,
            logo_text="DF",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=12,
                days_since_last_login=3,
                provisioned_seats=10,
                active_seats=2,
                monthly_api_or_feature_events=34,
                overlapping_tool_name=None,
                price_change_pct_last_90d=20.0,
                previous_monthly_cost=100.00,
                price_history_6m=[100.0, 100.0, 100.0, 100.0, 120.0, 120.0],
                raw_paypal_descriptor="PP*DSGNFLW-ENT10",
                is_trial_converting=False,
                has_data_retention_or_contract_lock=True,
            ),
            downgrade_option=DowngradeOptionDTO(
                target_plan_id="P-2STR290000454362WXNWU1ST",
                target_plan_name="Starter Duo Plan (2 Seats)",
                new_monthly_cost=29.00,
                monthly_savings=91.00,
                annual_savings=1092.00,
            ),
        ),
        SubscriptionDTO(
            id="SUB-MEETSCRIBE-03",
            paypal_subscription_id="I-4M773PLKJH2W",
            paypal_plan_id="P-3MS2900000454362WXNWU2MS",
            vendor_name="MeetScribe AI NoteTaker",
            plan_name="Unlimited Meeting Bot Pro",
            category="Productivity SaaS",
            monthly_cost=29.00,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-11",
            status=SubscriptionStatus.ACTIVE,
            logo_text="MS",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=1,
                days_since_last_login=38,
                provisioned_seats=1,
                active_seats=1,
                monthly_api_or_feature_events=1,
                overlapping_tool_name="Google Workspace Gemini Notes",
                price_change_pct_last_90d=2800.0,
                previous_monthly_cost=1.00,
                price_history_6m=[0.0, 0.0, 0.0, 0.0, 1.0, 29.0],
                raw_paypal_descriptor="PP*PADDLE-MSCRB88",
                is_trial_converting=True,
                trial_days_remaining=2,
                has_data_retention_or_contract_lock=False,
            ),
            switch_alternative=SwitchAlternativeDTO(
                alternative_vendor="Whisper Cloud API",
                alternative_plan="Transcription API Pack",
                new_monthly_cost=6.00,
                annual_net_savings=276.00,
                migration_rationale="Remplace l'abonnement MeetScribe (29 $/mois) par un pack API de transcription à 6 $/mois (79 % moins cher).",
            ),
        ),
        SubscriptionDTO(
            id="SUB-PULSEMETRICS-04",
            paypal_subscription_id="I-7P119ZXCVB8N",
            paypal_plan_id="P-1PM1450000454362WXNWU7PM",
            vendor_name="PulseMetrics Micro-Alerts",
            plan_name="Recurring Telemetry Add-on",
            category="Developer Tools",
            monthly_cost=14.50,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-09",
            status=SubscriptionStatus.ACTIVE,
            logo_text="PM",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=0,
                days_since_last_login=34,
                provisioned_seats=1,
                active_seats=0,
                monthly_api_or_feature_events=0,
                overlapping_tool_name=None,
                price_change_pct_last_90d=45.0,
                previous_monthly_cost=10.00,
                price_history_6m=[10.0, 10.0, 10.0, 12.0, 14.5, 14.5],
                raw_paypal_descriptor="PP*PLSMTRCS-BILL",
                is_trial_converting=False,
                has_data_retention_or_contract_lock=True,
            ),
        ),
        SubscriptionDTO(
            id="SUB-COPILOT-05",
            paypal_subscription_id="I-2G990GHJKL5Q",
            paypal_plan_id="P-9GH1900000454362WXNWU5CP",
            vendor_name="GitHub Copilot Business",
            plan_name="AI Pair Programmer Seat",
            category="Developer Tools",
            monthly_cost=19.00,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-24",
            status=SubscriptionStatus.ACTIVE,
            logo_text="GH",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=28,
                days_since_last_login=0,
                provisioned_seats=1,
                active_seats=1,
                monthly_api_or_feature_events=482,
                overlapping_tool_name=None,
                price_change_pct_last_90d=-13.6,
                previous_monthly_cost=22.00,
                price_history_6m=[22.0, 22.0, 22.0, 19.0, 19.0, 19.0],
                raw_paypal_descriptor="PP*GITHUB-CPLT",
                is_trial_converting=False,
                has_data_retention_or_contract_lock=False,
            ),
        ),
        SubscriptionDTO(
            id="SUB-VERCEL-06",
            paypal_subscription_id="I-8V441BNMKL3R",
            paypal_plan_id="P-6VR2000000454362WXNWU8VR",
            vendor_name="Vercel Pro Cloud",
            plan_name="Edge Network & CI/CD Production",
            category="Security & Infra",
            monthly_cost=20.00,
            currency="USD",
            billing_cycle="MONTHLY",
            next_billing_date="2026-11-28",
            status=SubscriptionStatus.ACTIVE,
            logo_text="VC",
            telemetry=UsageTelemetryDTO(
                active_days_last_30d=30,
                days_since_last_login=0,
                provisioned_seats=1,
                active_seats=1,
                monthly_api_or_feature_events=620,
                overlapping_tool_name=None,
                price_change_pct_last_90d=0.0,
                previous_monthly_cost=20.00,
                price_history_6m=[20.0, 20.0, 20.0, 20.0, 20.0, 20.0],
                raw_paypal_descriptor="PP*VERCEL-INC",
                is_trial_converting=False,
                has_data_retention_or_contract_lock=True,
            ),
        ),
    ]


class InMemoryStateStore:
    """
    Repository managing subscriptions, budget policy, and action proposals.
    Supports instant 1-click reset for live video demos and judge testing.
    """

    def __init__(self) -> None:
        self.subscriptions: list[SubscriptionDTO] = []
        self.budget_policy: BudgetPolicyDTO = BudgetPolicyDTO(
            monthly_autonomous_limit=settings.default_monthly_budget_limit,
            current_month_autonomous_spend=18.00,
            auto_approve_threshold=settings.default_auto_approve_threshold,
            require_1click_above_threshold=True,
        )
        self.proposals: list[AgentActionProposalDTO] = []
        self.total_realized_annual_savings: float = 0.0
        self.reset()

    def reset(self) -> None:
        self.subscriptions = build_initial_subscriptions()
        self.budget_policy = BudgetPolicyDTO(
            monthly_autonomous_limit=settings.default_monthly_budget_limit,
            current_month_autonomous_spend=18.00,
            auto_approve_threshold=settings.default_auto_approve_threshold,
            require_1click_above_threshold=True,
        )
        self.proposals = []
        self.total_realized_annual_savings = 0.0

    def get_subscription(self, sub_id: str) -> SubscriptionDTO | None:
        for sub in self.subscriptions:
            if sub.id == sub_id or sub.paypal_subscription_id == sub_id:
                return sub
        return None

    def get_proposal(self, proposal_id: str) -> AgentActionProposalDTO | None:
        for prop in self.proposals:
            if prop.proposal_id == proposal_id:
                return prop
        return None


state_store = InMemoryStateStore()
