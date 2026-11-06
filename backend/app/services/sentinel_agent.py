import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings, mask_secret
from app.core.audit_logger import audit_logger
from app.domain.audit_engine import audit_engine
from app.domain.guardrail_engine import guardrail_engine
from app.domain.strategies import ActionStrategyFactory
from app.infrastructure.gemini_provider import gemini_provider
from app.infrastructure.paypal_client import paypal_client
from app.infrastructure.state_store import state_store
from app.schemas.dto import (
    ActionType,
    AgentActionProposalDTO,
    AgentChatCommandDTO,
    ApprovalStatus,
    AutonomousPurchaseRequestDTO,
    BudgetPolicyDTO,
    GuardrailEvaluationDTO,
    SubscriptionDTO,
    SubscriptionStatus,
)


class SentinelAgentOrchestrator:
    """
    Core Orchestrator for SentinelPay AI.
    Coordinates the 4-stage Agentic Commerce loop:
    1. Telemetry & Subscription Audit (Waste Score & ROI calculation)
    2. Gemini AI Reasoning & Negotiation Strategy
    3. Deterministic Budget Guardrail Verification
    4. PayPal Sandbox API Execution (/v1/billing/subscriptions & /v2/checkout/orders)
    """

    def __init__(self) -> None:
        self._last_executive_brief: dict[str, Any] | None = None
        self._tx_lock = asyncio.Lock()

    def synchronize_audit_and_proposals(self) -> list[SubscriptionDTO]:
        """Audits all subscriptions and ensures action proposals exist for flagged items."""
        audited = audit_engine.audit_all(state_store.subscriptions)

        existing_sub_Targets = {
            p.target_subscription_id
            for p in state_store.proposals
            if p.target_subscription_id is not None
        }

        for sub in audited:
            if (
                sub.status == SubscriptionStatus.ACTIVE
                and sub.recommended_action != ActionType.KEEP_ACTIVE
                and sub.id not in existing_sub_Targets
            ):
                proposal = self._build_subscription_proposal(sub)
                state_store.proposals.append(proposal)

        return audited

    def _build_subscription_proposal(
        self, sub: SubscriptionDTO
    ) -> AgentActionProposalDTO:
        guardrail = guardrail_engine.evaluate_action(
            action_type=sub.recommended_action,
            amount_usd=0.0,
            category=sub.category,
            policy=state_store.budget_policy,
        )

        if sub.recommended_action == ActionType.DOWNGRADE_PLAN and sub.downgrade_option:
            title = f"Downgrade to {sub.downgrade_option.target_plan_name}"
            monthly_save = sub.downgrade_option.monthly_savings
            annual_save = sub.downgrade_option.annual_savings
            negotiation_msg = (
                f"Automated seat utilization audit (2/{sub.telemetry.provisioned_seats} active seats). "
                f"Revising PayPal Billing Plan to {sub.downgrade_option.target_plan_id} (${sub.downgrade_option.new_monthly_cost:.2f}/mo)."
            )
        elif sub.recommended_action == ActionType.SUSPEND_SUBSCRIPTION:
            title = f"Suspend Recurring Billing ({sub.vendor_name})"
            monthly_save = sub.monthly_cost
            annual_save = sub.estimated_annual_savings
            negotiation_msg = (
                f"Suspended by SentinelPay AI: +{sub.telemetry.price_change_pct_last_90d:.0f}% price hike "
                f"detected with 0 active telemetry events in {sub.telemetry.days_since_last_login} days."
            )
        else:
            title = f"Cancel Zombie Subscription ({sub.vendor_name})"
            monthly_save = sub.monthly_cost
            annual_save = sub.estimated_annual_savings
            negotiation_msg = (
                f"Cancelled by SentinelPay AI: dormant SaaS ({sub.telemetry.days_since_last_login} days inactive "
                f"or redundant overlap). Recovering ${annual_save:,.2f}/yr."
            )

        return AgentActionProposalDTO(
            proposal_id=f"PROP-{sub.id.split('-')[1]}-{uuid.uuid4().hex[:4].upper()}",
            action_type=sub.recommended_action,
            target_subscription_id=sub.id,
            vendor_name=sub.vendor_name,
            title=title,
            description=sub.ai_audit_rationale,
            amount_usd=0.0,
            monthly_savings_usd=round(monthly_save, 2),
            annual_savings_usd=round(annual_save, 2),
            confidence_score=0.97,
            ai_reasoning=sub.ai_audit_rationale,
            negotiation_message=negotiation_msg,
            guardrail=guardrail,
            paypal_receipt=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    async def get_dashboard_overview(self, refresh_ai_brief: bool = False) -> dict[str, Any]:
        subscriptions = self.synchronize_audit_and_proposals()
        if refresh_ai_brief or self._last_executive_brief is None:
            self._last_executive_brief = (
                await gemini_provider.generate_portfolio_executive_brief(
                    subscriptions, state_store.budget_policy
                )
            )

        active_subs = [
            s for s in subscriptions if s.status in (SubscriptionStatus.ACTIVE, SubscriptionStatus.DOWNGRADED)
        ]
        monthly_active_spend = round(sum(s.monthly_cost for s in active_subs), 2)
        potential_annual_savings = round(
            sum(
                s.estimated_annual_savings
                for s in subscriptions
                if s.status == SubscriptionStatus.ACTIVE
            ),
            2,
        )
        flagged_count = sum(
            1
            for s in subscriptions
            if s.status == SubscriptionStatus.ACTIVE
            and s.recommended_action != ActionType.KEEP_ACTIVE
        )

        paypal_status = await paypal_client.verify_connection()
        baseline_monthly_spend = 301.50
        if flagged_count == 0:
            financial_health_score = 98
        else:
            financial_health_score = max(
                38, min(98, int(98 - (potential_annual_savings / 2682.0) * 60))
            )

        return {
            "system_status": {
                "paypal_sandbox_mode": paypal_status["execution_mode"],
                "paypal_configured": paypal_status["configured"],
                "paypal_oauth_verified": paypal_status["oauth_authenticated"],
                "gemini_configured": settings.is_gemini_configured,
                "gemini_model": settings.gemini_model,
                "audit_chain_verified": audit_logger.verify_chain_integrity(),
                "paypal_client_id_masked": mask_secret(settings.paypal_client_id),
            },
            "kpis": {
                "monthly_active_spend_usd": monthly_active_spend,
                "baseline_monthly_spend_usd": baseline_monthly_spend,
                "annual_projected_spend_usd": round(monthly_active_spend * 12, 2),
                "potential_annual_savings_usd": potential_annual_savings,
                "realized_annual_savings_usd": round(
                    state_store.total_realized_annual_savings, 2
                ),
                "active_subscriptions_count": len(active_subs),
                "flagged_subscriptions_count": flagged_count,
                "financial_health_score": financial_health_score,
                "autonomous_budget_limit_usd": state_store.budget_policy.monthly_autonomous_limit,
                "autonomous_budget_spent_usd": state_store.budget_policy.current_month_autonomous_spend,
                "autonomous_budget_remaining_usd": round(
                    max(
                        0.0,
                        state_store.budget_policy.monthly_autonomous_limit
                        - state_store.budget_policy.current_month_autonomous_spend,
                    ),
                    2,
                ),
            },
            "executive_ai_brief": self._last_executive_brief,
            "budget_policy": state_store.budget_policy.model_dump(),
            "subscriptions": [s.model_dump() for s in subscriptions],
            "proposals": [p.model_dump() for p in state_store.proposals],
            "audit_trail": [e.model_dump() for e in audit_logger.list_events(limit=40)],
        }

    async def execute_proposal_by_id(self, proposal_id: str) -> AgentActionProposalDTO:
        self.synchronize_audit_and_proposals()
        proposal = state_store.get_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal '{proposal_id}' not found.")

        if proposal.guardrail.approval_status == ApprovalStatus.EXECUTED and proposal.paypal_receipt:
            return proposal

        if proposal.guardrail.approval_status == ApprovalStatus.REJECTED_BY_GUARDRAIL:
            raise ValueError(
                f"Cannot execute proposal '{proposal_id}': blocked by Budget Guardrail ({proposal.guardrail.reason})"
            )

        if proposal.guardrail.approval_status == ApprovalStatus.PENDING_1CLICK_APPROVAL:
            audit_logger.record(
                stage="GUARDRAIL_CHECK",
                actor="HumanInTheLoop (1-Click Approval)",
                summary=f"User approved proposal {proposal.proposal_id} ({proposal.title})",
                details={"proposal_id": proposal.proposal_id, "amount_usd": proposal.amount_usd},
            )
            proposal.guardrail.approval_status = ApprovalStatus.APPROVED_BY_USER

        strategy = ActionStrategyFactory.get_strategy(proposal.action_type)
        await strategy.execute(proposal, state_store)
        self.synchronize_audit_and_proposals()
        self._last_executive_brief = None
        return proposal

    async def execute_subscription_remediation(
        self, subscription_id: str
    ) -> AgentActionProposalDTO:
        """Finds or creates the remediation proposal for a subscription and executes it on PayPal Sandbox."""
        self.synchronize_audit_and_proposals()
        for prop in state_store.proposals:
            if prop.target_subscription_id == subscription_id:
                return await self.execute_proposal_by_id(prop.proposal_id)

        sub = state_store.get_subscription(subscription_id)
        if not sub:
            raise ValueError(f"Subscription '{subscription_id}' not found.")
        if sub.recommended_action == ActionType.KEEP_ACTIVE:
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
        new_prop = self._build_subscription_proposal(sub)
        state_store.proposals.append(new_prop)
        return await self.execute_proposal_by_id(new_prop.proposal_id)

    async def execute_autonomous_sweep(self) -> dict[str, Any]:
        """
        Executes all flagged subscription remediations (Cancel, Suspend, Downgrade)
        across the portfolio in a single autonomous sweep.
        """
        self.synchronize_audit_and_proposals()
        executed_proposals: list[AgentActionProposalDTO] = []

        for prop in state_store.proposals:
            if (
                prop.action_type
                in (
                    ActionType.CANCEL_SUBSCRIPTION,
                    ActionType.SUSPEND_SUBSCRIPTION,
                    ActionType.DOWNGRADE_PLAN,
                )
                and prop.guardrail.approval_status != ApprovalStatus.EXECUTED
            ):
                res = await self.execute_proposal_by_id(prop.proposal_id)
                executed_proposals.append(res)

        total_saved = round(sum(p.annual_savings_usd for p in executed_proposals), 2)
        audit_logger.record(
            stage="AGENT_REASONING",
            actor="SentinelAgentOrchestrator",
            summary=f"Completed Autonomous Sweep: {len(executed_proposals)} PayPal subscriptions optimized (${total_saved:,.2f}/yr saved)",
            details={"executed_count": len(executed_proposals), "annual_savings_usd": total_saved},
        )
        return {
            "executed_count": len(executed_proposals),
            "annual_savings_unlocked_usd": total_saved,
            "executed_proposals": [p.model_dump() for p in executed_proposals],
        }

    async def process_autonomous_purchase(
        self, req: AutonomousPurchaseRequestDTO
    ) -> AgentActionProposalDTO:
        """
        Evaluates an Agentic Commerce purchase request against the BudgetGuardrailEngine:
        - Auto-executes via PayPal Orders v2 (/v2/checkout/orders) if <= threshold and within monthly limit.
        - Queues for 1-Click Human Approval if > threshold and within monthly limit.
        - Blocks if over monthly budget or non-whitelisted category.
        """
        guardrail = guardrail_engine.evaluate_action(
            action_type=ActionType.AUTONOMOUS_PURCHASE,
            amount_usd=req.amount_usd,
            category=req.category,
            policy=state_store.budget_policy,
        )

        proposal = AgentActionProposalDTO(
            proposal_id=f"ORD-PROP-{uuid.uuid4().hex[:6].upper()}",
            action_type=ActionType.AUTONOMOUS_PURCHASE,
            target_subscription_id=None,
            vendor_name=req.vendor_name,
            title=req.item_name,
            description=req.justification,
            amount_usd=round(req.amount_usd, 2),
            monthly_savings_usd=0.0,
            annual_savings_usd=0.0,
            confidence_score=0.96,
            ai_reasoning=(
                f"Autonomous procurement request for {req.vendor_name} ({req.item_name}) at ${req.amount_usd:.2f}. "
                f"Justification: {req.justification}"
            ),
            negotiation_message=None,
            guardrail=guardrail,
            paypal_receipt=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        state_store.proposals.insert(0, proposal)

        if (
            req.auto_execute_if_allowed
            and guardrail.passed
            and guardrail.approval_status == ApprovalStatus.AUTO_APPROVED
        ):
            strategy = ActionStrategyFactory.get_strategy(ActionType.AUTONOMOUS_PURCHASE)
            await strategy.execute(proposal, state_store)

        return proposal

    async def process_natural_language_command(
        self, cmd: AgentChatCommandDTO
    ) -> dict[str, Any]:
        subscriptions = self.synchronize_audit_and_proposals()
        audit_logger.record(
            stage="AGENT_REASONING",
            actor="SentinelAgentOrchestrator",
            summary=f"Received user command: '{cmd.prompt[:80]}'",
            details={"auto_execute_safe_actions": cmd.auto_execute_safe_actions},
        )

        interpretation = await gemini_provider.interpret_agent_command(
            user_prompt=cmd.prompt,
            subscriptions=subscriptions,
            policy=state_store.budget_policy,
        )

        executed_items: list[dict[str, Any]] = []
        created_proposal: dict[str, Any] | None = None

        intent = interpretation.get("intent", "AUDIT_PORTFOLIO")
        if intent == "AUTONOMOUS_PURCHASE" and interpretation.get("purchase_proposal"):
            pp = interpretation["purchase_proposal"]
            purchase_req = AutonomousPurchaseRequestDTO(
                vendor_name=pp.get("vendor_name", "Cloud Compute Provider"),
                item_name=pp.get("item_name", "API Compute Credits"),
                category=pp.get("category", "Cloud & AI Compute"),
                amount_usd=float(pp.get("amount_usd", 19.0)),
                justification=f"Triggered via SentinelPay AI Copilot: {cmd.prompt}",
                auto_execute_if_allowed=True,
            )
            prop = await self.process_autonomous_purchase(purchase_req)
            created_proposal = prop.model_dump()
        elif intent == "REMEDIATE_WASTE" and cmd.auto_execute_safe_actions:
            sweep = await self.execute_autonomous_sweep()
            executed_items = sweep["executed_proposals"]

        return {
            "reply": interpretation.get("reply", ""),
            "intent": intent,
            "provider": interpretation.get("provider", "SENTINEL_NEURAL_ENGINE"),
            "executed_items": executed_items,
            "created_proposal": created_proposal,
        }

    async def execute_subscription_auto_switch(
        self, subscription_id: str
    ) -> dict[str, Any]:
        """
        Executes an atomic 2-step PayPal SaaS Arbitrage Switch:
        1. Cancels the overpriced/zombie subscription via /v1/billing/subscriptions/{id}/cancel
        2. Provisions the cheaper alternative via /v2/checkout/orders
        """
        async with self._tx_lock:
            self.synchronize_audit_and_proposals()
            sub = state_store.get_subscription(subscription_id)
            if not sub or not sub.switch_alternative:
                raise ValueError(
                    f"Subscription '{subscription_id}' not found or has no switch_alternative configured."
                )

            alt = sub.switch_alternative
            original_vendor = sub.vendor_name

            cancel_receipt = await paypal_client.cancel_subscription(
                sub.paypal_subscription_id,
                reason=alt.migration_rationale,
                idempotency_key=f"SWITCH-CANCEL-{sub.id}",
            )
            order_receipt = await paypal_client.create_autonomous_order(
                vendor_name=alt.alternative_vendor,
                item_name=alt.alternative_plan,
                amount_usd=alt.new_monthly_cost,
                idempotency_key=f"SWITCH-ORDER-{sub.id}",
            )

            old_cost = sub.monthly_cost
            sub.status = SubscriptionStatus.DOWNGRADED
            sub.vendor_name = f"{alt.alternative_vendor} (replaces {original_vendor})"
            sub.plan_name = alt.alternative_plan
            sub.monthly_cost = alt.new_monthly_cost
            sub.telemetry.previous_monthly_cost = old_cost
            if old_cost > 0:
                sub.telemetry.price_change_pct_last_90d = round(
                    ((sub.monthly_cost - old_cost) / old_cost) * 100, 1
                )
            sub.telemetry.price_history_6m = (
                sub.telemetry.price_history_6m + [sub.monthly_cost]
            )[-6:]

            state_store.total_realized_annual_savings = round(
                state_store.total_realized_annual_savings + alt.annual_net_savings, 2
            )

            for prop in state_store.proposals:
                if prop.target_subscription_id == sub.id:
                    prop.action_type = ActionType.AUTONOMOUS_SWITCH
                    prop.guardrail.approval_status = ApprovalStatus.EXECUTED
                    prop.paypal_receipt = order_receipt
                    prop.annual_savings_usd = alt.annual_net_savings
                    prop.monthly_savings_usd = round(old_cost - alt.new_monthly_cost, 2)

            audit_logger.record(
                stage="EXECUTION_RECEIPT",
                actor="SaaSArbitrageAutoSwitch",
                summary=f"Step 1/2: Cancelled {original_vendor} ({sub.paypal_subscription_id}) via PayPal /cancel",
                details=cancel_receipt.model_dump(),
            )
            audit_logger.record(
                stage="EXECUTION_RECEIPT",
                actor="SaaSArbitrageAutoSwitch",
                summary=(
                    f"Step 2/2: Switched to {alt.alternative_vendor} ({alt.alternative_plan}) "
                    f"at ${alt.new_monthly_cost:.2f}/mo via PayPal Orders v2 — net savings ${alt.annual_net_savings:,.2f}/yr"
                ),
                details=order_receipt.model_dump(),
            )

            self.synchronize_audit_and_proposals()
            self._last_executive_brief = None
            return {
                "cancel_receipt": cancel_receipt.model_dump(),
                "order_receipt": order_receipt.model_dump(),
                "annual_net_savings_usd": alt.annual_net_savings,
                "subscription": sub.model_dump(),
            }

    async def simulate_incoming_paypal_webhook_trap(
        self, scenario: str = "TRIAL_CONVERSION"
    ) -> dict[str, Any]:
        """
        Simulates an incoming signed PayPal Webhook event (PAYMENT.SALE.COMPLETED)
        for an unauthorized trial-to-paid conversion or silent price hike, and
        executes real-time Zero-Trust interception (/suspend + /v2/payments/captures/{id}/refund).
        """
        async with self._tx_lock:
            if scenario == "PRICE_HIKE":
                merchant_name = "PulseMetrics Micro-Alerts"
                descriptor = "PP*PLSMTRCS-BILL"
                amount = 39.00
                trap_description = (
                    "Unauthorized recurring charge of $39.00 (+169% silent price hike from $14.50/mo) "
                    "with 0 active telemetry sessions."
                )
            else:
                merchant_name = "VideoGen AI Studio"
                descriptor = "PP*VIDEOGEN-TRIAL99"
                amount = 49.00
                trap_description = (
                    "Unauthorized $1.00 7-day trial conversion into a $49.00/mo recurring charge "
                    "(Capture ID: CAP-99812345X) with 0 active user sessions."
                )

            annual_saved = round(amount * 12, 2)

            audit_logger.record(
                stage="PAYPAL_API",
                actor="PayPalWebhookVerifier",
                summary=(
                    f"Intercepted signed PayPal Webhook PAYMENT.SALE.COMPLETED from {merchant_name} "
                    f"(${amount:.2f}) — PAYPAL-TRANSMISSION-SIG: SHA256withRSA-VERIFIED"
                ),
                details={
                    "webhook_event_type": "PAYMENT.SALE.COMPLETED",
                    "transmission_sig": "SHA256withRSA-VERIFIED",
                    "merchant": merchant_name,
                    "descriptor": descriptor,
                    "capture_id": "CAP-99812345X",
                    "subscription_id": "I-TRAP99812V",
                    "amount_usd": amount,
                },
            )

            suspend_receipt = await paypal_client.suspend_subscription(
                "I-TRAP99812V",
                reason="Blocked unauthorized trial-to-paid conversion by SentinelPay Zero-Trust Firewall",
            )
            refund_receipt = await paypal_client.refund_captured_payment(
                capture_id="CAP-99812345X",
                amount_usd=amount,
                reason="Instant PayPal refund of unauthorized trial conversion / price hike",
            )

            state_store.total_realized_annual_savings = round(
                state_store.total_realized_annual_savings + annual_saved, 2
            )

            remaining_budget = round(
                max(
                    0.0,
                    state_store.budget_policy.monthly_autonomous_limit
                    - state_store.budget_policy.current_month_autonomous_spend,
                ),
                2,
            )
            proposal = AgentActionProposalDTO(
                proposal_id=f"WH-INT-{uuid.uuid4().hex[:6].upper()}",
                action_type=ActionType.WEBHOOK_REFUND_INTERCEPT,
                target_subscription_id="I-TRAP99812V",
                vendor_name=merchant_name,
                title=f"Zero-Trust Webhook Clawback & Suspend ({merchant_name})",
                description=trap_description,
                amount_usd=amount,
                monthly_savings_usd=amount,
                annual_savings_usd=annual_saved,
                confidence_score=0.99,
                ai_reasoning=(
                    f"Real-time PayPal Webhook Firewall intercepted {descriptor} (${amount:.2f}). "
                    f"Suspended billing agreement I-TRAP99812V and refunded capture CAP-99812345X."
                ),
                negotiation_message="Instant statutory refund & billing suspension enforced via PayPal Captures Refund API v2.",
                guardrail=GuardrailEvaluationDTO(
                    passed=True,
                    approval_status=ApprovalStatus.EXECUTED,
                    policy_rule_triggered="RULE_ZERO_TRUST_WEBHOOK_FIREWALL_CLAWBACK",
                    reason="Unauthorized trial-to-paid conversion intercepted and refunded automatically.",
                    remaining_monthly_budget=remaining_budget,
                ),
                paypal_receipt=refund_receipt,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            state_store.proposals.insert(0, proposal)

            audit_logger.record(
                stage="EXECUTION_RECEIPT",
                actor="ZeroTrustWebhookFirewall",
                summary=f"Suspended billing agreement I-TRAP99812V for {merchant_name}",
                details=suspend_receipt.model_dump(),
            )
            audit_logger.record(
                stage="EXECUTION_RECEIPT",
                actor="ZeroTrustWebhookFirewall",
                summary=f"Refunded ${amount:.2f} USD on capture CAP-99812345X ({annual_saved:,.2f}/yr protected)",
                details=refund_receipt.model_dump(),
            )

            self._last_executive_brief = None
            return {
                "webhook_event_type": "PAYMENT.SALE.COMPLETED",
                "transmission_sig": "SHA256withRSA-VERIFIED",
                "merchant": merchant_name,
                "descriptor": descriptor,
                "intercepted_amount_usd": amount,
                "annual_saved_usd": annual_saved,
                "suspend_receipt": suspend_receipt.model_dump(),
                "refund_receipt": refund_receipt.model_dump(),
            }

    async def execute_b2b_negotiation(
        self, subscription_id: str, apply_discount: bool = False
    ) -> dict[str, Any]:
        """
        Executes active AI-powered B2B retention negotiation with vendor.
        Generates an ultimatum letter referencing real telemetry & PayPal agreement,
        simulates vendor retention discount counter-offer, and optionally applies it via PayPal /revise.
        """
        async with self._tx_lock:
            sub = state_store.get_subscription(subscription_id)
            if not sub:
                raise ValueError(f"Subscription '{subscription_id}' not found.")

            vendor_slug = sub.vendor_name.lower().replace(" ", "").replace("&", "")
            telemetry = sub.telemetry

            # Calculate tailored discount counter-offer
            discount_pct = 40.0
            discounted_cost = round(sub.monthly_cost * (1.0 - discount_pct / 100.0), 2)
            monthly_savings = round(sub.monthly_cost - discounted_cost, 2)
            annual_savings = round(monthly_savings * 12.0, 2)

            ultimatum_letter = (
                f"To: enterprise-retention@{vendor_slug}.com\n"
                f"Subject: [URGENT] SentinelPay Treasury Audit: Billing Agreement #{sub.paypal_subscription_id} Termination Notice\n\n"
                f"Dear {sub.vendor_name} Enterprise Accounts Team,\n\n"
                f"SentinelPay AI has completed an automated telemetry audit on our organization's account "
                f"(PayPal Agreement ID: {sub.paypal_subscription_id}, Plan: {sub.plan_name}).\n\n"
                f"Key Telemetry Findings:\n"
                f"- Active Days in last 30d: {telemetry.active_days_last_30d}/30 days\n"
                f"- Days since last login: {telemetry.days_since_last_login} days\n"
                f"- Seat Utilization: {telemetry.active_seats} of {telemetry.provisioned_seats} provisioned seats active ({int((telemetry.active_seats/max(telemetry.provisioned_seats,1))*100)}% efficiency)\n"
                f"- Recent Price Variation: +{telemetry.price_change_pct_last_90d:.1f}% surge detected\n\n"
                f"Due to severe cost-per-active-day inefficiency (${sub.cost_per_active_day:.2f}/active day), our Budget Guardrails "
                f"have scheduled immediate revocation of PayPal recurring billing mandate {sub.paypal_subscription_id}.\n\n"
                f"We are prepared to retain the agreement if a {discount_pct:.0f}% retention discount is applied (${discounted_cost:.2f}/mo "
                f"instead of ${sub.monthly_cost:.2f}/mo) within 48 hours.\n\n"
                f"Sincerely,\n"
                f"SentinelPay Autonomous Treasury Copilot\n"
                f"Cryptographic Audit Reference: EVT-{uuid.uuid4().hex[:8].upper()}"
            )

            vendor_counter_offer = {
                "vendor_name": sub.vendor_name,
                "status": "OFFER_ACCEPTED",
                "proposed_monthly_cost": discounted_cost,
                "discount_percentage": discount_pct,
                "monthly_savings_usd": monthly_savings,
                "annual_savings_usd": annual_savings,
                "vendor_response_message": (
                    f"Dear SentinelPay Team, we reviewed your telemetry notice. To preserve our partnership, "
                    f"we have authorized a special {discount_pct:.0f}% enterprise retention discount on plan {sub.plan_name}, "
                    f"reducing your recurring fee from ${sub.monthly_cost:.2f} to ${discounted_cost:.2f}/month."
                ),
            }

            applied_receipt = None
            if apply_discount:
                applied_receipt = await paypal_client.revise_subscription_plan(
                    subscription_id=sub.paypal_subscription_id,
                    new_plan_id=f"P-RETENTION-{uuid.uuid4().hex[:6].upper()}",
                    new_plan_name=f"{sub.plan_name} (Enterprise Retention -{discount_pct:.0f}%)",
                    new_monthly_cost=discounted_cost,
                    reason=f"Applied {discount_pct:.0f}% B2B retention discount via SentinelPay Negotiation Engine.",
                    idempotency_key=f"NEGOTIATE-REVISE-{sub.id}",
                )
                old_cost = sub.monthly_cost
                sub.status = SubscriptionStatus.DOWNGRADED
                sub.monthly_cost = discounted_cost
                sub.telemetry.previous_monthly_cost = old_cost
                sub.telemetry.price_change_pct_last_90d = round(((discounted_cost - old_cost) / old_cost) * 100, 1)
                sub.telemetry.price_history_6m = (sub.telemetry.price_history_6m + [discounted_cost])[-6:]
                state_store.total_realized_annual_savings = round(
                    state_store.total_realized_annual_savings + annual_savings, 2
                )
                audit_logger.record(
                    stage="EXECUTION_RECEIPT",
                    actor="B2BRetentionNegotiator",
                    summary=f"Applied {discount_pct:.0f}% retention discount on {sub.vendor_name} (${discounted_cost:.2f}/mo, saved ${annual_savings:,.2f}/yr)",
                    details=applied_receipt.model_dump(),
                )
                self._last_executive_brief = None

            return {
                "subscription_id": sub.id,
                "vendor_name": sub.vendor_name,
                "ultimatum_letter": ultimatum_letter,
                "counter_offer": vendor_counter_offer,
                "discount_applied_on_paypal": apply_discount,
                "paypal_receipt": applied_receipt.model_dump() if applied_receipt else None,
                "current_subscription": sub.model_dump(),
            }

    async def generate_cfo_boardpack(self) -> dict[str, Any]:
        """
        Generates the formal corporate CFO Audit Boardpack with before/after benchmarks,
        category distribution, and SHA-256 cryptographic verification ledger.
        """
        overview = await self.get_dashboard_overview(refresh_ai_brief=False)
        kpis = overview["kpis"]
        subs = overview["subscriptions"]
        trail = overview["audit_trail"]

        baseline_monthly = 301.50
        baseline_annual = round(baseline_monthly * 12.0, 2)
        current_monthly = kpis["monthly_active_spend_usd"]
        current_annual = round(current_monthly * 12.0, 2)
        total_realized_savings = kpis["realized_annual_savings_usd"]
        reduction_pct = round(((baseline_annual - current_annual) / baseline_annual) * 100.0, 1) if baseline_annual > 0 else 0.0

        return {
            "report_id": f"CFO-SENTINEL-{uuid.uuid4().hex[:8].upper()}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "organization": "Enterprise FinOps & Treasury Division",
            "certification": "Certified by SentinelPay AI & PayPal Sandbox REST API v1/v2",
            "executive_summary": overview["executive_ai_brief"].get("executive_summary", ""),
            "financial_health_score": kpis.get("financial_health_score", 98),
            "kpi_summary": {
                "baseline_monthly_spend_usd": baseline_monthly,
                "baseline_annual_spend_usd": baseline_annual,
                "current_monthly_spend_usd": current_monthly,
                "current_annual_spend_usd": current_annual,
                "realized_annual_savings_usd": total_realized_savings,
                "percentage_spend_reduction": reduction_pct,
                "active_subscriptions_count": kpis["active_subscriptions_count"],
                "flagged_subscriptions_count": kpis["flagged_subscriptions_count"],
            },
            "subscriptions_matrix": [
                {
                    "vendor": s["vendor_name"],
                    "plan": s["plan_name"],
                    "status": s["status"],
                    "monthly_cost": s["monthly_cost"],
                    "waste_score": s["waste_score"],
                    "annual_savings": s["estimated_annual_savings"],
                    "paypal_agreement_id": s["paypal_subscription_id"],
                }
                for s in subs
            ],
            "cryptographic_proof": {
                "chain_verified": audit_logger.verify_chain_integrity(),
                "latest_sha256_hash": trail[0]["sha256_hash"] if trail else "0" * 64,
                "total_events_logged": len(trail),
            },
            "cfo_signoff": {
                "status": "APPROVED_FOR_BOARD_PRESENTATION",
                "auditor_role": "SentinelPay Autonomous CFO Agent",
                "paypal_sandbox_environment": "https://api-m.sandbox.paypal.com",
            },
        }

    def update_budget_policy(self, new_policy: BudgetPolicyDTO) -> BudgetPolicyDTO:
        new_policy.current_month_autonomous_spend = (
            state_store.budget_policy.current_month_autonomous_spend
        )
        state_store.budget_policy = new_policy
        audit_logger.record(
            stage="GUARDRAIL_CHECK",
            actor="BudgetGuardrailEngine",
            summary=(
                f"Updated Budget Guardrails: Monthly Cap=${new_policy.monthly_autonomous_limit:.2f}, "
                f"Auto-Approve Threshold=${new_policy.auto_approve_threshold:.2f}"
            ),
            details=new_policy.model_dump(),
        )
        return state_store.budget_policy


sentinel_agent = SentinelAgentOrchestrator()
