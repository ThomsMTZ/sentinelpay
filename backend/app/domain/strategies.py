from abc import ABC, abstractmethod
from app.core.audit_logger import audit_logger
from app.infrastructure.paypal_client import paypal_client
from app.infrastructure.state_store import InMemoryStateStore
from app.schemas.dto import (
    ActionType,
    AgentActionProposalDTO,
    ApprovalStatus,
    PayPalExecutionReceiptDTO,
    SubscriptionStatus,
)


class ActionExecutionStrategy(ABC):
    """Strategy interface for executing PayPal Sandbox operations."""

    @abstractmethod
    async def execute(
        self, proposal: AgentActionProposalDTO, store: InMemoryStateStore
    ) -> PayPalExecutionReceiptDTO:
        raise NotImplementedError


class CancelSubscriptionStrategy(ActionExecutionStrategy):
    async def execute(
        self, proposal: AgentActionProposalDTO, store: InMemoryStateStore
    ) -> PayPalExecutionReceiptDTO:
        sub = store.get_subscription(proposal.target_subscription_id or "")
        paypal_sub_id = sub.paypal_subscription_id if sub else (proposal.target_subscription_id or "I-SANDBOX")
        reason = proposal.negotiation_message or proposal.ai_reasoning

        receipt = await paypal_client.cancel_subscription(
            paypal_sub_id,
            reason,
            idempotency_key=f"EXEC-{proposal.proposal_id}",
        )
        if sub and sub.status == SubscriptionStatus.ACTIVE:
            sub.status = SubscriptionStatus.CANCELLED
            store.total_realized_annual_savings = round(
                store.total_realized_annual_savings + proposal.annual_savings_usd, 2
            )

        proposal.paypal_receipt = receipt
        proposal.guardrail.approval_status = ApprovalStatus.EXECUTED

        audit_logger.record(
            stage="EXECUTION_RECEIPT",
            actor="CancelSubscriptionStrategy",
            summary=f"Cancelled {proposal.vendor_name} ({paypal_sub_id}) via PayPal Sandbox — saved ${proposal.annual_savings_usd:,.2f}/yr",
            details=receipt.model_dump(),
        )
        return receipt


class SuspendSubscriptionStrategy(ActionExecutionStrategy):
    async def execute(
        self, proposal: AgentActionProposalDTO, store: InMemoryStateStore
    ) -> PayPalExecutionReceiptDTO:
        sub = store.get_subscription(proposal.target_subscription_id or "")
        paypal_sub_id = sub.paypal_subscription_id if sub else (proposal.target_subscription_id or "I-SANDBOX")
        reason = proposal.negotiation_message or proposal.ai_reasoning

        receipt = await paypal_client.suspend_subscription(
            paypal_sub_id,
            reason,
            idempotency_key=f"EXEC-{proposal.proposal_id}",
        )
        if sub and sub.status == SubscriptionStatus.ACTIVE:
            sub.status = SubscriptionStatus.SUSPENDED
            store.total_realized_annual_savings = round(
                store.total_realized_annual_savings + proposal.annual_savings_usd, 2
            )

        proposal.paypal_receipt = receipt
        proposal.guardrail.approval_status = ApprovalStatus.EXECUTED

        audit_logger.record(
            stage="EXECUTION_RECEIPT",
            actor="SuspendSubscriptionStrategy",
            summary=f"Suspended {proposal.vendor_name} ({paypal_sub_id}) via PayPal Sandbox — saved ${proposal.annual_savings_usd:,.2f}/yr",
            details=receipt.model_dump(),
        )
        return receipt


class DowngradePlanStrategy(ActionExecutionStrategy):
    async def execute(
        self, proposal: AgentActionProposalDTO, store: InMemoryStateStore
    ) -> PayPalExecutionReceiptDTO:
        sub = store.get_subscription(proposal.target_subscription_id or "")
        paypal_sub_id = sub.paypal_subscription_id if sub else (proposal.target_subscription_id or "I-SANDBOX")
        target_plan_id = (
            sub.downgrade_option.target_plan_id
            if sub and sub.downgrade_option
            else "P-STARTER-DOWNGRADE"
        )
        target_plan_name = (
            sub.downgrade_option.target_plan_name
            if sub and sub.downgrade_option
            else "Starter Plan"
        )
        new_cost = (
            sub.downgrade_option.new_monthly_cost
            if sub and sub.downgrade_option
            else proposal.amount_usd
        )

        receipt = await paypal_client.revise_subscription_plan(
            subscription_id=paypal_sub_id,
            new_plan_id=target_plan_id,
            new_plan_name=target_plan_name,
            new_monthly_cost=new_cost,
            reason=proposal.ai_reasoning,
            idempotency_key=f"EXEC-{proposal.proposal_id}",
        )

        if sub and sub.status == SubscriptionStatus.ACTIVE:
            old_cost = sub.monthly_cost
            sub.status = SubscriptionStatus.DOWNGRADED
            sub.plan_name = target_plan_name
            sub.paypal_plan_id = target_plan_id
            sub.monthly_cost = new_cost
            sub.telemetry.previous_monthly_cost = old_cost
            if old_cost > 0:
                sub.telemetry.price_change_pct_last_90d = round(
                    ((new_cost - old_cost) / old_cost) * 100, 1
                )
            sub.telemetry.price_history_6m = (
                sub.telemetry.price_history_6m + [new_cost]
            )[-6:]
            if sub.downgrade_option:
                sub.telemetry.provisioned_seats = sub.telemetry.active_seats
            store.total_realized_annual_savings = round(
                store.total_realized_annual_savings + proposal.annual_savings_usd, 2
            )

        proposal.paypal_receipt = receipt
        proposal.guardrail.approval_status = ApprovalStatus.EXECUTED

        audit_logger.record(
            stage="EXECUTION_RECEIPT",
            actor="DowngradePlanStrategy",
            summary=f"Revised {proposal.vendor_name} plan to '{target_plan_name}' via PayPal /revise — saved ${proposal.annual_savings_usd:,.2f}/yr",
            details=receipt.model_dump(),
        )
        return receipt


class AutonomousOrderStrategy(ActionExecutionStrategy):
    async def execute(
        self, proposal: AgentActionProposalDTO, store: InMemoryStateStore
    ) -> PayPalExecutionReceiptDTO:
        receipt = await paypal_client.create_autonomous_order(
            vendor_name=proposal.vendor_name,
            item_name=proposal.title,
            amount_usd=proposal.amount_usd,
            currency="USD",
            idempotency_key=f"EXEC-{proposal.proposal_id}",
        )
        store.budget_policy.current_month_autonomous_spend = round(
            store.budget_policy.current_month_autonomous_spend + proposal.amount_usd,
            2,
        )
        proposal.paypal_receipt = receipt
        proposal.guardrail.approval_status = ApprovalStatus.EXECUTED
        proposal.guardrail.remaining_monthly_budget = round(
            max(
                0.0,
                store.budget_policy.monthly_autonomous_limit
                - store.budget_policy.current_month_autonomous_spend,
            ),
            2,
        )

        audit_logger.record(
            stage="EXECUTION_RECEIPT",
            actor="AutonomousOrderStrategy",
            summary=f"Executed PayPal Order v2 ({receipt.paypal_resource_id}) for {proposal.vendor_name} (${proposal.amount_usd:.2f})",
            details=receipt.model_dump(),
        )
        return receipt


class ActionStrategyFactory:
    """Factory Pattern resolving the right PayPal execution strategy."""

    _strategies: dict[ActionType, ActionExecutionStrategy] = {
        ActionType.CANCEL_SUBSCRIPTION: CancelSubscriptionStrategy(),
        ActionType.SUSPEND_SUBSCRIPTION: SuspendSubscriptionStrategy(),
        ActionType.DOWNGRADE_PLAN: DowngradePlanStrategy(),
        ActionType.AUTONOMOUS_PURCHASE: AutonomousOrderStrategy(),
    }

    @classmethod
    def get_strategy(cls, action_type: ActionType) -> ActionExecutionStrategy:
        strategy = cls._strategies.get(action_type)
        if not strategy:
            raise ValueError(f"Unsupported action type for execution: {action_type}")
        return strategy
