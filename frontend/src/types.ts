export type SubscriptionStatus = 'ACTIVE' | 'SUSPENDED' | 'CANCELLED' | 'DOWNGRADED';

export type RiskCategory =
  | 'DORMANT_ZOMBIE'
  | 'OVERPROVISIONED_SEATS'
  | 'DUPLICATE_SAAS'
  | 'HIDDEN_MICRO_TX'
  | 'TRIAL_TRAP_CONVERSION'
  | 'HEALTHY_HIGH_ROI';

export type ActionType =
  | 'CANCEL_SUBSCRIPTION'
  | 'SUSPEND_SUBSCRIPTION'
  | 'DOWNGRADE_PLAN'
  | 'AUTONOMOUS_PURCHASE'
  | 'AUTONOMOUS_SWITCH'
  | 'WEBHOOK_REFUND_INTERCEPT'
  | 'KEEP_ACTIVE';

export type ApprovalStatus =
  | 'AUTO_APPROVED'
  | 'PENDING_1CLICK_APPROVAL'
  | 'APPROVED_BY_USER'
  | 'REJECTED_BY_GUARDRAIL'
  | 'EXECUTED';

export interface UsageTelemetry {
  active_days_last_30d: number;
  days_since_last_login: number;
  provisioned_seats: number;
  active_seats: number;
  monthly_api_or_feature_events: number;
  overlapping_tool_name: string | null;
  price_change_pct_last_90d: number;
  previous_monthly_cost: number;
  price_history_6m: number[];
  raw_paypal_descriptor: string;
  is_trial_converting: boolean;
  trial_days_remaining: number | null;
  has_data_retention_or_contract_lock: boolean;
}

export interface DowngradeOption {
  target_plan_id: string;
  target_plan_name: string;
  new_monthly_cost: number;
  monthly_savings: number;
  annual_savings: number;
}

export interface SwitchAlternative {
  alternative_vendor: string;
  alternative_plan: string;
  new_monthly_cost: number;
  annual_net_savings: number;
  migration_rationale: string;
}

export interface SubscriptionItem {
  id: string;
  paypal_subscription_id: string;
  paypal_plan_id: string;
  vendor_name: string;
  plan_name: string;
  category: string;
  monthly_cost: number;
  currency: string;
  billing_cycle: string;
  next_billing_date: string;
  status: SubscriptionStatus;
  logo_text: string;
  telemetry: UsageTelemetry;
  downgrade_option: DowngradeOption | null;
  switch_alternative: SwitchAlternative | null;
  waste_score: number;
  risk_category: RiskCategory;
  recommended_action: ActionType;
  estimated_annual_savings: number;
  ai_audit_rationale: string;
  cost_per_active_day: number;
}

export interface BudgetPolicy {
  monthly_autonomous_limit: number;
  current_month_autonomous_spend: number;
  auto_approve_threshold: number;
  require_1click_above_threshold: boolean;
  allow_autonomous_cancellations: boolean;
  allow_autonomous_downgrades: boolean;
  whitelisted_categories: string[];
}

export interface GuardrailEvaluation {
  passed: boolean;
  approval_status: ApprovalStatus;
  policy_rule_triggered: string;
  reason: string;
  remaining_monthly_budget: number;
}

export interface PayPalExecutionReceipt {
  paypal_request_id: string;
  paypal_resource_id: string;
  endpoint: string;
  http_method: string;
  http_status: number;
  execution_mode: string;
  status_text: string;
  approval_url: string | null;
  raw_response: Record<string, unknown>;
  executed_at: string;
}

export interface AgentActionProposal {
  proposal_id: string;
  action_type: ActionType;
  target_subscription_id: string | null;
  vendor_name: string;
  title: string;
  description: string;
  amount_usd: number;
  monthly_savings_usd: number;
  annual_savings_usd: number;
  confidence_score: number;
  ai_reasoning: string;
  negotiation_message: string | null;
  guardrail: GuardrailEvaluation;
  paypal_receipt: PayPalExecutionReceipt | null;
  created_at: string;
}

export interface AuditTraceEvent {
  event_id: string;
  timestamp: string;
  stage: string;
  actor: string;
  summary: string;
  details: Record<string, unknown>;
  sha256_hash: string;
  prev_hash: string;
}

export interface WebhookInterceptionResult {
  webhook_event_type: string;
  transmission_sig: string;
  merchant: string;
  descriptor: string;
  intercepted_amount_usd: number;
  annual_saved_usd: number;
  suspend_receipt: PayPalExecutionReceipt;
  refund_receipt: PayPalExecutionReceipt;
}

export interface DashboardData {
  system_status: {
    paypal_sandbox_mode: string;
    paypal_configured: boolean;
    paypal_oauth_verified: boolean;
    gemini_configured: boolean;
    gemini_model: string;
    audit_chain_verified?: boolean;
    paypal_client_id_masked?: string | null;
  };
  kpis: {
    monthly_active_spend_usd: number;
    annual_projected_spend_usd: number;
    potential_annual_savings_usd: number;
    realized_annual_savings_usd: number;
    active_subscriptions_count: number;
    flagged_subscriptions_count: number;
    autonomous_budget_limit_usd: number;
    autonomous_budget_spent_usd: number;
    autonomous_budget_remaining_usd: number;
    financial_health_score?: number;
    baseline_monthly_spend_usd?: number;
  };
  executive_ai_brief: {
    provider: string;
    executive_summary: string;
    top_priority_vendor: string;
    negotiation_strategy: string;
  };
  budget_policy: BudgetPolicy;
  subscriptions: SubscriptionItem[];
  proposals: AgentActionProposal[];
  audit_trail: AuditTraceEvent[];
}

export interface B2BNegotiationResult {
  subscription_id: string;
  vendor_name: string;
  ultimatum_letter: string;
  counter_offer: {
    vendor_name: string;
    status: string;
    proposed_monthly_cost: number;
    discount_percentage: number;
    monthly_savings_usd: number;
    annual_savings_usd: number;
    vendor_response_message: string;
  };
  discount_applied_on_paypal: boolean;
  paypal_receipt: PayPalExecutionReceipt | null;
  current_subscription: SubscriptionItem;
}

export interface CFOBoardpack {
  report_id: string;
  generated_at: string;
  organization: string;
  certification: string;
  executive_summary: string;
  financial_health_score: number;
  kpi_summary: {
    baseline_monthly_spend_usd: number;
    baseline_annual_spend_usd: number;
    current_monthly_spend_usd: number;
    current_annual_spend_usd: number;
    realized_annual_savings_usd: number;
    percentage_spend_reduction: number;
    active_subscriptions_count: number;
    flagged_subscriptions_count: number;
  };
  subscriptions_matrix: Array<{
    vendor: string;
    plan: string;
    status: string;
    monthly_cost: number;
    waste_score: number;
    annual_savings: number;
    paypal_agreement_id: string;
  }>;
  cryptographic_proof: {
    chain_verified: boolean;
    latest_sha256_hash: string;
    total_events_logged: number;
  };
  cfo_signoff: {
    status: string;
    auditor_role: string;
    paypal_sandbox_environment: string;
  };
}

