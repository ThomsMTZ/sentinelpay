from app.schemas.dto import (
    ActionType,
    RiskCategory,
    SubscriptionDTO,
    SubscriptionStatus,
)


class SubscriptionAuditEngine:
    """
    Domain service responsible for evaluating SaaS telemetry, computing Waste Scores (0-100),
    classifying risk categories, and recommending optimal PayPal API actions.
    """

    def evaluate_subscription(self, sub: SubscriptionDTO) -> SubscriptionDTO:
        if sub.status != SubscriptionStatus.ACTIVE:
            sub.waste_score = 0
            sub.recommended_action = ActionType.KEEP_ACTIVE
            sub.estimated_annual_savings = 0.0
            return sub

        t = sub.telemetry
        active_days = max(t.active_days_last_30d, 0)
        sub.cost_per_active_day = (
            round(sub.monthly_cost / active_days, 2)
            if active_days > 0
            else round(sub.monthly_cost, 2)
        )

        # Case 0: Free Trial / $1 Trial Trap Auto-Renewal Conversion
        if t.is_trial_converting:
            sub.waste_score = 94
            sub.risk_category = RiskCategory.TRIAL_TRAP_CONVERSION
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            days_left = t.trial_days_remaining if t.trial_days_remaining is not None else 2
            overlap_note = (
                f" and 100% functional overlap with '{t.overlapping_tool_name}'"
                if t.overlapping_tool_name
                else ""
            )
            sub.ai_audit_rationale = (
                f"Predatory trial trap detected ({t.raw_paypal_descriptor}): automatic conversion from "
                f"${t.previous_monthly_cost:.2f} -> ${sub.monthly_cost:.2f}/mo (+{t.price_change_pct_last_90d:.0f}%) "
                f"in {days_left} days ({t.active_days_last_30d} active days/30d{overlap_note}). "
                f"Immediate termination via PayPal /cancel to protect ${sub.estimated_annual_savings:,.2f}/yr."
            )
            return sub

        # Case 1: Dormant / Zombie Subscription (0 active days and >=40 days since login)
        if t.active_days_last_30d == 0 and t.days_since_last_login >= 40:
            sub.waste_score = 96
            sub.risk_category = RiskCategory.DORMANT_ZOMBIE
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            hike_note = (
                f" despite silent price surge of +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo)"
                if t.price_change_pct_last_90d > 0
                else ""
            )
            sub.ai_audit_rationale = (
                f"Zombie SaaS ({t.raw_paypal_descriptor}): 0 active sessions for {t.days_since_last_login} days"
                f"{hike_note}. No critical retention lock: permanent cancellation via PayPal /cancel (${sub.estimated_annual_savings:,.2f}/yr saved)."
            )
            return sub

        # Case 2: Overprovisioned Multi-Seat Plan with Downgrade Option
        seat_utilization = t.active_seats / max(t.provisioned_seats, 1)
        if t.provisioned_seats >= 5 and seat_utilization <= 0.35 and sub.downgrade_option:
            sub.waste_score = 78
            sub.risk_category = RiskCategory.OVERPROVISIONED_SEATS
            sub.recommended_action = ActionType.DOWNGRADE_PLAN
            sub.estimated_annual_savings = round(sub.downgrade_option.annual_savings, 2)
            lock_note = (
                "Data retention protection active (has_data_retention_or_contract_lock): "
                if t.has_data_retention_or_contract_lock
                else ""
            )
            sub.ai_audit_rationale = (
                f"Price creep of +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo) "
                f"while only {t.active_seats}/{t.provisioned_seats} provisioned seats are active ({int(seat_utilization*100)}%). "
                f"{lock_note}Non-destructive downgrade via PayPal /revise to '{sub.downgrade_option.target_plan_name}' "
                f"(${sub.downgrade_option.new_monthly_cost:.0f}/mo) instead of cancelling, preserving workflow and saving ${sub.downgrade_option.annual_savings:,.2f}/yr."
            )
            return sub

        # Case 3: Duplicate / Redundant Tool
        if t.overlapping_tool_name:
            sub.waste_score = 88
            sub.risk_category = RiskCategory.DUPLICATE_SAAS
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            sub.ai_audit_rationale = (
                f"100% functional overlap with '{t.overlapping_tool_name}' ({t.active_days_last_30d} active days/30d). "
                f"PayPal /cancel recommended (${sub.estimated_annual_savings:,.2f}/yr saved)."
            )
            return sub

        # Case 4: Hidden Micro-Transaction / Silent Price Creep
        if t.price_change_pct_last_90d >= 20.0 or (t.active_days_last_30d <= 1 and sub.monthly_cost <= 20.0):
            sub.waste_score = 82
            sub.risk_category = RiskCategory.HIDDEN_MICRO_TX
            sub.recommended_action = ActionType.SUSPEND_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            sub.ai_audit_rationale = (
                f"Silent price creep of +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.2f} -> ${sub.monthly_cost:.2f}/mo) "
                f"on PayPal descriptor '{t.raw_paypal_descriptor}' with 0 feature events in {t.days_since_last_login}d. "
                f"Telemetry lock active: reversible pause via PayPal /suspend instead of cancellation."
            )
            return sub

        # Case 5: Healthy / High ROI Subscription
        sub.waste_score = max(2, 100 - int((t.active_days_last_30d / 30.0) * 95))
        sub.risk_category = RiskCategory.HEALTHY_HIGH_ROI
        sub.recommended_action = ActionType.KEEP_ACTIVE
        sub.estimated_annual_savings = 0.0
        price_note = (
            f", negotiated fee reduced by {t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo)"
            if t.price_change_pct_last_90d < 0
            else f", price stable (${sub.monthly_cost:.0f}/mo)"
        )
        sub.ai_audit_rationale = (
            f"High ROI ({t.raw_paypal_descriptor}): {t.active_days_last_30d}/30 active days "
            f"({t.monthly_api_or_feature_events} feature events/mo, ${sub.cost_per_active_day:.2f}/active day{price_note}). "
            f"Retaining active PayPal billing mandate."
        )
        return sub

    def audit_all(self, subscriptions: list[SubscriptionDTO]) -> list[SubscriptionDTO]:
        return [self.evaluate_subscription(sub) for sub in subscriptions]


audit_engine = SubscriptionAuditEngine()
