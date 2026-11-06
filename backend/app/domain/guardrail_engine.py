from app.core.audit_logger import audit_logger
from app.schemas.dto import (
    ActionType,
    ApprovalStatus,
    BudgetPolicyDTO,
    GuardrailEvaluationDTO,
)


class BudgetGuardrailEngine:
    """
    Deterministic Policy Gatekeeper for Zero-Trust Agentic Commerce.
    Every AI-proposed financial operation is validated against hard budget
    constraints before any PayPal Sandbox API call can be executed.
    """

    def evaluate_action(
        self,
        action_type: ActionType,
        amount_usd: float,
        category: str,
        policy: BudgetPolicyDTO,
    ) -> GuardrailEvaluationDTO:
        remaining = round(
            max(0.0, policy.monthly_autonomous_limit - policy.current_month_autonomous_spend),
            2,
        )

        # Cost-saving operations (Cancel, Suspend, Downgrade) generate positive cashflow
        if action_type in (
            ActionType.CANCEL_SUBSCRIPTION,
            ActionType.SUSPEND_SUBSCRIPTION,
            ActionType.DOWNGRADE_PLAN,
        ):
            if action_type == ActionType.DOWNGRADE_PLAN and not policy.allow_autonomous_downgrades:
                res = GuardrailEvaluationDTO(
                    passed=True,
                    approval_status=ApprovalStatus.PENDING_1CLICK_APPROVAL,
                    policy_rule_triggered="RULE_DOWNGRADE_REQUIRES_CONFIRMATION",
                    reason="Policy requires 1-click human confirmation before revising PayPal billing plans.",
                    remaining_monthly_budget=remaining,
                )
            elif action_type in (ActionType.CANCEL_SUBSCRIPTION, ActionType.SUSPEND_SUBSCRIPTION) and not policy.allow_autonomous_cancellations:
                res = GuardrailEvaluationDTO(
                    passed=True,
                    approval_status=ApprovalStatus.PENDING_1CLICK_APPROVAL,
                    policy_rule_triggered="RULE_CANCEL_REQUIRES_CONFIRMATION",
                    reason="Policy requires 1-click human confirmation before cancelling subscriptions.",
                    remaining_monthly_budget=remaining,
                )
            else:
                res = GuardrailEvaluationDTO(
                    passed=True,
                    approval_status=ApprovalStatus.AUTO_APPROVED,
                    policy_rule_triggered="RULE_POSITIVE_SAVINGS_AUTO_AUTHORIZED",
                    reason="Zero-spend remediation action increases net cashflow; authorized for autonomous PayPal execution.",
                    remaining_monthly_budget=remaining,
                )

            audit_logger.record(
                stage="GUARDRAIL_CHECK",
                actor="BudgetGuardrailEngine",
                summary=f"Guardrail evaluated {action_type}: {res.approval_status}",
                details=res.model_dump(),
            )
            return res

        # Autonomous Purchase / Re-subscription via PayPal Orders API v2
        if category not in policy.whitelisted_categories:
            res = GuardrailEvaluationDTO(
                passed=False,
                approval_status=ApprovalStatus.REJECTED_BY_GUARDRAIL,
                policy_rule_triggered="RULE_CATEGORY_NOT_WHITELISTED",
                reason=f"Category '{category}' is not in whitelisted categories: {policy.whitelisted_categories}.",
                remaining_monthly_budget=remaining,
            )
            audit_logger.record(
                stage="GUARDRAIL_CHECK",
                actor="BudgetGuardrailEngine",
                summary=f"Blocked purchase (${amount_usd:.2f}) — category '{category}' not whitelisted",
                details=res.model_dump(),
            )
            return res

        if amount_usd > remaining:
            res = GuardrailEvaluationDTO(
                passed=False,
                approval_status=ApprovalStatus.REJECTED_BY_GUARDRAIL,
                policy_rule_triggered="RULE_MONTHLY_BUDGET_CAP_EXCEEDED",
                reason=(
                    f"Requested spend (${amount_usd:.2f}) exceeds remaining monthly autonomous budget "
                    f"(${remaining:.2f} left of ${policy.monthly_autonomous_limit:.2f})."
                ),
                remaining_monthly_budget=remaining,
            )
            audit_logger.record(
                stage="GUARDRAIL_CHECK",
                actor="BudgetGuardrailEngine",
                summary=f"Blocked purchase (${amount_usd:.2f}) — exceeds monthly cap (${remaining:.2f} left)",
                details=res.model_dump(),
            )
            return res

        if policy.require_1click_above_threshold and amount_usd > policy.auto_approve_threshold:
            res = GuardrailEvaluationDTO(
                passed=True,
                approval_status=ApprovalStatus.PENDING_1CLICK_APPROVAL,
                policy_rule_triggered="RULE_1CLICK_HUMAN_IN_THE_LOOP_THRESHOLD",
                reason=(
                    f"Spend (${amount_usd:.2f}) is within monthly cap (${remaining:.2f} left) "
                    f"but exceeds autonomous single-tx limit (${policy.auto_approve_threshold:.2f}). "
                    "Routed to 1-Click Human Approval Queue."
                ),
                remaining_monthly_budget=remaining,
            )
            audit_logger.record(
                stage="GUARDRAIL_CHECK",
                actor="BudgetGuardrailEngine",
                summary=f"Routed purchase (${amount_usd:.2f}) to 1-Click Human Approval Queue (> ${policy.auto_approve_threshold:.2f})",
                details=res.model_dump(),
            )
            return res

        res = GuardrailEvaluationDTO(
            passed=True,
            approval_status=ApprovalStatus.AUTO_APPROVED,
            policy_rule_triggered="RULE_AUTONOMOUS_MICRO_CHECKOUT_ALLOWED",
            reason=(
                f"Spend (${amount_usd:.2f}) <= auto-approve threshold (${policy.auto_approve_threshold:.2f}) "
                f"and within monthly budget (${remaining - amount_usd:.2f} remaining after tx)."
            ),
            remaining_monthly_budget=round(remaining - amount_usd, 2),
        )
        audit_logger.record(
            stage="GUARDRAIL_CHECK",
            actor="BudgetGuardrailEngine",
            summary=f"Auto-approved autonomous PayPal Order (${amount_usd:.2f})",
            details=res.model_dump(),
        )
        return res


guardrail_engine = BudgetGuardrailEngine()
