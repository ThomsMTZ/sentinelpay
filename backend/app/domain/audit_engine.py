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
                f" et doublon 100% avec '{t.overlapping_tool_name}'"
                if t.overlapping_tool_name
                else ""
            )
            sub.ai_audit_rationale = (
                f"Piège d'essai détecté ({t.raw_paypal_descriptor}) : conversion automatique de "
                f"${t.previous_monthly_cost:.2f} -> ${sub.monthly_cost:.2f}/mo (+{t.price_change_pct_last_90d:.0f}%) "
                f"dans {days_left} jours ({t.active_days_last_30d}j actif/30j{overlap_note}). "
                f"Résiliation immédiate via PayPal /cancel pour éviter ${sub.estimated_annual_savings:,.2f}/an de perte."
            )
            return sub

        # Case 1: Dormant / Zombie Subscription (0 active days and >=40 days since login)
        if t.active_days_last_30d == 0 and t.days_since_last_login >= 40:
            sub.waste_score = 96
            sub.risk_category = RiskCategory.DORMANT_ZOMBIE
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            hike_note = (
                f" malgré une hausse silencieuse de +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo)"
                if t.price_change_pct_last_90d > 0
                else ""
            )
            sub.ai_audit_rationale = (
                f"SaaS Zombie ({t.raw_paypal_descriptor}) : 0 session active depuis {t.days_since_last_login} jours"
                f"{hike_note}. Aucune rétention critique : coupure définitive via PayPal /cancel (${sub.estimated_annual_savings:,.2f}/an économisés)."
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
                "Protection des actifs/contrats active (has_data_retention_or_contract_lock) : "
                if t.has_data_retention_or_contract_lock
                else ""
            )
            sub.ai_audit_rationale = (
                f"Hausse tarifaire de +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo) "
                f"alors que seuls {t.active_seats}/{t.provisioned_seats} sièges sont actifs ({int(seat_utilization*100)}%). "
                f"{lock_note}Downgrade non-destructif via PayPal /revise vers '{sub.downgrade_option.target_plan_name}' "
                f"(${sub.downgrade_option.new_monthly_cost:.0f}/mo) au lieu de /cancel pour économiser ${sub.downgrade_option.annual_savings:,.2f}/an."
            )
            return sub

        # Case 3: Duplicate / Redundant Tool
        if t.overlapping_tool_name:
            sub.waste_score = 88
            sub.risk_category = RiskCategory.DUPLICATE_SAAS
            sub.recommended_action = ActionType.CANCEL_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            sub.ai_audit_rationale = (
                f"Doublon fonctionnel à 100% avec '{t.overlapping_tool_name}' ({t.active_days_last_30d}j actif/30j). "
                f"Résiliation PayPal /cancel recommandée (${sub.estimated_annual_savings:,.2f}/an)."
            )
            return sub

        # Case 4: Hidden Micro-Transaction / Silent Price Creep
        if t.price_change_pct_last_90d >= 20.0 or (t.active_days_last_30d <= 1 and sub.monthly_cost <= 20.0):
            sub.waste_score = 82
            sub.risk_category = RiskCategory.HIDDEN_MICRO_TX
            sub.recommended_action = ActionType.SUSPEND_SUBSCRIPTION
            sub.estimated_annual_savings = round(sub.monthly_cost * 12, 2)
            sub.ai_audit_rationale = (
                f"Dérive tarifaire furtive de +{t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.2f} -> ${sub.monthly_cost:.2f}/mo) "
                f"sur le descripteur PayPal '{t.raw_paypal_descriptor}' avec 0 événement en {t.days_since_last_login}j. "
                f"Verrou de rétention des logs actif : mise en pause réversible via PayPal /suspend au lieu de /cancel."
            )
            return sub

        # Case 5: Healthy / High ROI Subscription
        sub.waste_score = max(2, 100 - int((t.active_days_last_30d / 30.0) * 95))
        sub.risk_category = RiskCategory.HEALTHY_HIGH_ROI
        sub.recommended_action = ActionType.KEEP_ACTIVE
        sub.estimated_annual_savings = 0.0
        price_note = (
            f", tarif négocié en baisse de {t.price_change_pct_last_90d:.1f}% (${t.previous_monthly_cost:.0f} -> ${sub.monthly_cost:.0f}/mo)"
            if t.price_change_pct_last_90d < 0
            else f", tarif stable (${sub.monthly_cost:.0f}/mo)"
        )
        sub.ai_audit_rationale = (
            f"ROI élevé ({t.raw_paypal_descriptor}) : {t.active_days_last_30d}/30 jours actifs "
            f"({t.monthly_api_or_feature_events} événements/mois, ${sub.cost_per_active_day:.2f}/jour actif{price_note}). "
            f"Maintien de l'accord PayPal."
        )
        return sub

    def audit_all(self, subscriptions: list[SubscriptionDTO]) -> list[SubscriptionDTO]:
        return [self.evaluate_subscription(sub) for sub in subscriptions]


audit_engine = SubscriptionAuditEngine()
