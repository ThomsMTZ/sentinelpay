import React, { useEffect, useId, useRef, useState } from 'react';
import {
  CheckCircle2,
  Clock,
  SlidersHorizontal,
  RotateCcw,
  KeyRound,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Send,
  Database,
  XCircle,
  ArrowRightLeft,
  Code2,
  Zap,
  FileText,
  Handshake,
  Printer,
  X,
} from 'lucide-react';
import {
  fetchDashboard,
  remediateSubscription,
  autoSwitchSubscription,
  simulatePayPalWebhookTrap,
  executeProposal,
  runAutonomousSweep,
  submitAutonomousPurchase,
  sendAgentCommand,
  updateBudgetPolicy,
  seedPayPalSandbox,
  saveCredentials,
  resetDemoEnvironment,
  negotiateSubscription,
  fetchCFOBoardpack,
} from './api';
import {
  AgentActionProposal,
  B2BNegotiationResult,
  CFOBoardpack,
  DashboardData,
  PayPalExecutionReceipt,
  SubscriptionItem,
  WebhookInterceptionResult,
} from './types';

function formatUSD(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);
}

function useAnimatedNumber(target: number, durationMs = 520): number {
  const [displayValue, setDisplayValue] = useState<number>(target);
  const prevRef = useRef<number>(target);

  useEffect(() => {
    const startVal = prevRef.current;
    if (Math.abs(target - startVal) < 0.005) {
      setDisplayValue(target);
      prevRef.current = target;
      return;
    }
    const startTime = performance.now();
    let rafId = 0;

    const tick = (now: number) => {
      const progress = Math.min(1, (now - startTime) / durationMs);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = startVal + (target - startVal) * eased;
      setDisplayValue(current);
      if (progress < 1) {
        rafId = requestAnimationFrame(tick);
      } else {
        setDisplayValue(target);
        prevRef.current = target;
      }
    };

    rafId = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(rafId);
      prevRef.current = target;
    };
  }, [target, durationMs]);

  return displayValue;
}

function RevolutSparkline({
  history,
  priceDeltaPct,
}: {
  history: number[];
  priceDeltaPct: number;
}) {
  const rawUid = useId();
  const safeUid = rawUid.replace(/[^a-zA-Z0-9_-]/g, '');
  const pts = history && history.length >= 2 ? history : [1, 1];
  const minVal = Math.min(...pts);
  const maxVal = Math.max(...pts);
  const range = maxVal - minVal;

  const strokeColor =
    priceDeltaPct > 0 ? '#C53030' : priceDeltaPct < 0 ? '#0E7C47' : '#94A3B8';
  const gradId = `revolut-spark-${safeUid}`;

  const coords = pts.map((val, idx) => {
    const x = 2 + (idx / Math.max(pts.length - 1, 1)) * 52;
    const y = range === 0 ? 11 : 18 - ((val - minVal) / range) * 14;
    return { x: Number(x.toFixed(1)), y: Number(y.toFixed(1)) };
  });

  const linePoints = coords.map((c) => `${c.x},${c.y}`).join(' ');
  const areaPoints = `2,21 ${linePoints} 54,21`;
  const lastCoord = coords[coords.length - 1];

  return (
    <svg
      width={56}
      height={22}
      viewBox="0 0 56 22"
      className="shrink-0 overflow-visible"
      aria-label="6-month pricing trajectory"
    >
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={strokeColor} stopOpacity="0.22" />
          <stop offset="100%" stopColor={strokeColor} stopOpacity="0.0" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints} fill={`url(#${gradId})`} />
      <polyline
        points={linePoints}
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {lastCoord && (
        <circle cx={lastCoord.x} cy={lastCoord.y} r="2" fill={strokeColor} />
      )}
    </svg>
  );
}

function RevolutPriceDeltaBadge({ priceDeltaPct }: { priceDeltaPct: number }) {
  if (priceDeltaPct > 0) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[11px] font-semibold tabular-figure bg-[#FFF0F0] text-[#C53030] border border-[#C53030]/20">
        ▲ +{priceDeltaPct.toFixed(1)}%
      </span>
    );
  }
  if (priceDeltaPct < 0) {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[11px] font-semibold tabular-figure bg-[#EAF7F0] text-[#0E7C47] border border-[#0E7C47]/20">
        ▼ {priceDeltaPct.toFixed(1)}%
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-[11px] font-medium tabular-figure bg-[#F1F5F9] text-[#64748B]">
      0,0 %
    </span>
  );
}

function PayPalJsonInspectorButton({
  receipt,
  auditChainVerified = true,
}: {
  receipt: PayPalExecutionReceipt;
  auditChainVerified?: boolean;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-1.5">
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setOpen((prev) => !prev);
        }}
        className="pressable inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-white border border-[#CBD5E1] hover:border-[#0070BA] text-[11px] font-medium text-[#003087]"
      >
        <Code2 className="w-3 h-3 text-[#0070BA]" />
        <span>{open ? 'Hide PayPal JSON' : 'Inspect PayPal JSON'}</span>
      </button>

      {open && (
        <div
          onClick={(e) => e.stopPropagation()}
          className="mt-2 rounded-xl bg-[#0C121D] text-[#E2E8F0] p-3 text-[11px] font-mono space-y-2 border border-[#1E293B]"
        >
          <div className="flex flex-wrap items-center justify-between gap-2 pb-1.5 border-b border-white/10 text-[10px]">
            <span className="text-[#93C5FD]">
              PayPal-Request-Id: {receipt.paypal_request_id}
            </span>
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-[#0E7C47]/30 text-[#6EE7B7]">
              {auditChainVerified ? 'SHA-256 Chain Verified' : 'SHA-256 Audit Active'}
            </span>
          </div>
          <pre className="overflow-x-auto text-[10px] leading-relaxed text-[#E2E8F0] max-h-48">
            {JSON.stringify(receipt.raw_response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [filterTab, setFilterTab] = useState<'all' | 'flagged' | 'resolved'>('all');
  const [expandedSubId, setExpandedSubId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Live Webhook Trap Interception state
  const [webhookInterception, setWebhookInterception] =
    useState<WebhookInterceptionResult | null>(null);

  // Command & natural language input
  const [commandInput, setCommandInput] = useState<string>('');
  const [commandReply, setCommandReply] = useState<string | null>(null);
  const [commandBusy, setCommandBusy] = useState<boolean>(false);

  // Custom order form & collapsible toggle
  const [showCustomOrderForm, setShowCustomOrderForm] = useState<boolean>(false);
  const [vendorName, setVendorName] = useState<string>('RunPod Serverless GPU');
  const [itemName, setItemName] = useState<string>('Crédits de calcul A100');
  const [orderAmount, setOrderAmount] = useState<string>('19.50');
  const [orderCategory, setOrderCategory] = useState<string>('Cloud & AI Compute');

  // Modals
  const [showCredentialsModal, setShowCredentialsModal] = useState<boolean>(false);
  const [paypalClientId, setPaypalClientId] = useState<string>('');
  const [paypalClientSecret, setPaypalClientSecret] = useState<string>('');
  const [geminiApiKey, setGeminiApiKey] = useState<string>('');

  // CFO Boardpack Modal state
  const [showCFOModal, setShowCFOModal] = useState<boolean>(false);
  const [cfoBoardpack, setCFOBoardpack] = useState<CFOBoardpack | null>(null);
  const [cfoLoading, setCFOLoading] = useState<boolean>(false);

  // B2B Negotiation Modal state
  const [negotiatingSub, setNegotiatingSub] = useState<SubscriptionItem | null>(null);
  const [negotiationResult, setNegotiationResult] = useState<B2BNegotiationResult | null>(null);
  const [negotiationLoading, setNegotiationLoading] = useState<boolean>(false);

  // Editable policy sliders (1:1 60fps direct manipulation)
  const [monthlyLimit, setMonthlyLimit] = useState<number>(150);
  const [autoThreshold, setAutoThreshold] = useState<number>(25);

  // Apple 60fps Number Ticker values (must be called unconditionally before early return)
  const rawPotentialSavings = data?.kpis.potential_annual_savings_usd ?? 0;
  const rawMonthlySpend = data?.kpis.monthly_active_spend_usd ?? 0;
  const rawRealizedSavings = data?.kpis.realized_annual_savings_usd ?? 0;
  const rawHealthScore =
    data?.kpis.financial_health_score ??
    (data && data.kpis.flagged_subscriptions_count === 0
      ? 98
      : Math.max(38, Math.min(98, Math.round(98 - (rawPotentialSavings / 2682.0) * 60))));

  const animatedPotentialSavings = useAnimatedNumber(rawPotentialSavings);
  const animatedMonthlySpend = useAnimatedNumber(rawMonthlySpend);
  const animatedRealizedSavings = useAnimatedNumber(rawRealizedSavings);
  const animatedHealthScore = Math.round(useAnimatedNumber(rawHealthScore));

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    window.setTimeout(() => {
      setToastMessage((prev) => (prev === msg ? null : prev));
    }, 4200);
  };

  const loadData = async (refreshAi = false) => {
    try {
      const res = await fetchDashboard(refreshAi);
      setData(res);
      setMonthlyLimit(res.budget_policy.monthly_autonomous_limit);
      setAutoThreshold(res.budget_policy.auto_approve_threshold);
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur réseau');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData(false);
  }, []);

  const handleSingleRemediate = async (sub: SubscriptionItem) => {
    setBusyId(sub.id);
    try {
      const res = await remediateSubscription(sub.id);
      setData(res.dashboard);
      triggerToast(
        `${sub.vendor_name} mis à jour via PayPal (${formatUSD(
          res.executed_proposal.annual_savings_usd
        )}/an économisés)`
      );
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur PayPal');
    } finally {
      setBusyId(null);
    }
  };

  const handleAutoSwitch = async (sub: SubscriptionItem) => {
    if (!sub.switch_alternative) return;
    setBusyId(`SWITCH-${sub.id}`);
    try {
      const res = await autoSwitchSubscription(sub.id);
      setData(res.dashboard);
      triggerToast(
        `Arbitrage PayPal exécuté : remplacement par ${
          sub.switch_alternative.alternative_vendor
        } (${formatUSD(res.switch_result.annual_net_savings_usd)}/an économisés)`
      );
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur lors du remplacement PayPal');
    } finally {
      setBusyId(null);
    }
  };

  const handleSimulateWebhookTrap = async (
    scenario: 'TRIAL_CONVERSION' | 'PRICE_HIKE'
  ) => {
    setBusyId(`WEBHOOK-${scenario}`);
    try {
      const res = await simulatePayPalWebhookTrap(scenario);
      setData(res.dashboard);
      setWebhookInterception(res.interception);
      triggerToast(
        `Webhook PayPal intercepté : remboursement instantané de ${formatUSD(
          res.interception.intercepted_amount_usd
        )} (${res.interception.descriptor})`
      );
    } catch (err) {
      triggerToast(
        err instanceof Error ? err.message : 'Erreur lors de la simulation du webhook'
      );
    } finally {
      setBusyId(null);
    }
  };

  const handleBatchSweep = async () => {
    setBusyId('SWEEP');
    try {
      const res = await runAutonomousSweep();
      setData(res.dashboard);
      triggerToast(
        `${res.sweep.executed_count} abonnements optimisés sur PayPal (${formatUSD(
          res.sweep.annual_savings_unlocked_usd
        )}/an récupérés)`
      );
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur lors de l’optimisation');
    } finally {
      setBusyId(null);
    }
  };

  const handleOpenCFOBoardpack = async () => {
    setCFOLoading(true);
    try {
      const report = await fetchCFOBoardpack();
      setCFOBoardpack(report);
      setShowCFOModal(true);
    } catch (err) {
      triggerToast(
        err instanceof Error
          ? err.message
          : 'Erreur lors de la génération du rapport CFO'
      );
    } finally {
      setCFOLoading(false);
    }
  };

  const handleOpenNegotiation = async (sub: SubscriptionItem) => {
    setNegotiatingSub(sub);
    setNegotiationResult(null);
    setNegotiationLoading(true);
    try {
      const res = await negotiateSubscription(sub.id, false);
      setNegotiationResult(res.negotiation);
    } catch (err) {
      triggerToast(
        err instanceof Error ? err.message : 'Erreur lors de la négociation B2B'
      );
      setNegotiatingSub(null);
    } finally {
      setNegotiationLoading(false);
    }
  };

  const handleApplyNegotiationDiscount = async () => {
    if (!negotiatingSub) return;
    setBusyId(`APPLY-NEG-${negotiatingSub.id}`);
    try {
      const res = await negotiateSubscription(negotiatingSub.id, true);
      setData(res.dashboard);
      setNegotiationResult(res.negotiation);
      triggerToast(
        `Remise B2B de 40% appliquée via PayPal /revise (${formatUSD(
          res.negotiation.counter_offer.annual_savings_usd
        )}/an économisés)`
      );
    } catch (err) {
      triggerToast(
        err instanceof Error
          ? err.message
          : 'Erreur lors de l’application de la remise PayPal'
      );
    } finally {
      setBusyId(null);
    }
  };

  const handleApproveProposal = async (prop: AgentActionProposal) => {
    setBusyId(prop.proposal_id);
    try {
      const res = await executeProposal(prop.proposal_id);
      setData(res.dashboard);
      triggerToast(
        `Transaction ${prop.vendor_name} exécutée sur PayPal (${res.executed_proposal.paypal_receipt?.paypal_resource_id})`
      );
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Approbation refusée');
    } finally {
      setBusyId(null);
    }
  };

  const handleQuickPurchaseScenario = async (
    vendor: string,
    item: string,
    amount: number,
    justification: string,
    category = 'Cloud & AI Compute'
  ) => {
    setBusyId(`PURCHASE-${amount}`);
    try {
      const res = await submitAutonomousPurchase({
        vendor_name: vendor,
        item_name: item,
        category,
        amount_usd: amount,
        justification,
        auto_execute_if_allowed: true,
      });
      setData(res.dashboard);
      const status = res.proposal.guardrail.approval_status;
      if (status === 'EXECUTED') {
        triggerToast(
          `Ordre PayPal exécuté automatiquement (${formatUSD(amount)}) — Réf. ${
            res.proposal.paypal_receipt?.paypal_resource_id
          }`
        );
      } else if (status === 'PENDING_1CLICK_APPROVAL') {
        triggerToast(
          `Montant supérieur au seuil automatique (${formatUSD(
            autoThreshold
          )}) : placé en attente d’approbation 1 clic`
        );
      } else {
        triggerToast(`Ordre refusé par le plafond budgétaire : ${res.proposal.guardrail.reason}`);
      }
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur de paiement');
    } finally {
      setBusyId(null);
    }
  };

  const handleCustomPurchaseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const parsedAmount = parseFloat(orderAmount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) return;
    await handleQuickPurchaseScenario(
      vendorName,
      itemName,
      parsedAmount,
      `Achat initié depuis le terminal de commande (${itemName})`,
      orderCategory
    );
  };

  const handleSendCommand = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commandInput.trim()) return;
    setCommandBusy(true);
    try {
      const res = await sendAgentCommand(commandInput, true);
      setData(res.dashboard);
      setCommandReply(res.agent_response.reply);
      setCommandInput('');
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur lors de l’analyse');
    } finally {
      setCommandBusy(false);
    }
  };

  const handlePolicySave = async (newLimit: number, newThreshold: number) => {
    if (!data) return;
    setMonthlyLimit(newLimit);
    setAutoThreshold(newThreshold);
    try {
      const res = await updateBudgetPolicy({
        ...data.budget_policy,
        monthly_autonomous_limit: newLimit,
        auto_approve_threshold: newThreshold,
      });
      setData(res.dashboard);
      triggerToast('Règles budgétaires mises à jour');
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur de sauvegarde');
    }
  };

  const handleSeedSandbox = async () => {
    setBusyId('SEED');
    try {
      const res = await seedPayPalSandbox();
      setData(res.dashboard);
      triggerToast(res.seed_result.message);
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur Sandbox');
    } finally {
      setBusyId(null);
    }
  };

  const handleResetDemo = async () => {
    setBusyId('RESET');
    try {
      const fresh = await resetDemoEnvironment();
      setData(fresh);
      setMonthlyLimit(fresh.budget_policy.monthly_autonomous_limit);
      setAutoThreshold(fresh.budget_policy.auto_approve_threshold);
      setWebhookInterception(null);
      setCommandReply(null);
      triggerToast('Données de démonstration réinitialisées');
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur de réinitialisation');
    } finally {
      setBusyId(null);
    }
  };

  const handleCredentialsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusyId('CREDS');
    try {
      const res = await saveCredentials({
        paypal_client_id: paypalClientId || undefined,
        paypal_client_secret: paypalClientSecret || undefined,
        gemini_api_key: geminiApiKey || undefined,
      });
      setData(res.dashboard);
      setPaypalClientId('');
      setPaypalClientSecret('');
      setGeminiApiKey('');
      setShowCredentialsModal(false);
      triggerToast(
        res.connection_status.oauth_authenticated
          ? 'Connecté en direct à PayPal Developer Sandbox (OAuth 2.0 vérifié)'
          : 'Configuration enregistrée'
      );
    } catch (err) {
      triggerToast(err instanceof Error ? err.message : 'Erreur d’enregistrement');
    } finally {
      setBusyId(null);
    }
  };

  if (loading || !data) {
    return (
      <div className="min-h-screen bg-[#F5F7FA] flex items-center justify-center p-6">
        <div className="bg-white border border-[#E2E8F0] rounded-2xl px-8 py-6 shadow-sm flex items-center gap-4">
          <div className="w-5 h-5 rounded-full border-2 border-[#003087] border-t-transparent animate-spin" />
          <span className="text-[15px] font-medium text-[#0C121D]">
            Synchronizing PayPal Billing Agreements & Gemini Treasury Engine…
          </span>
        </div>
      </div>
    );
  }

  const { kpis, subscriptions, proposals, audit_trail, system_status, executive_ai_brief } = data;
  const baselineMonthlySpend = kpis.baseline_monthly_spend_usd ?? 301.5;
  const auditChainVerified = system_status.audit_chain_verified ?? true;

  const filteredSubscriptions = subscriptions.filter((sub) => {
    if (filterTab === 'flagged') {
      return sub.status === 'ACTIVE' && sub.recommended_action !== 'KEEP_ACTIVE';
    }
    if (filterTab === 'resolved') {
      return sub.status !== 'ACTIVE';
    }
    return true;
  });

  const pendingApprovals = proposals.filter(
    (p) => p.guardrail.approval_status === 'PENDING_1CLICK_APPROVAL'
  );
  const executedProposals = proposals.filter(
    (p) =>
      p.guardrail.approval_status === 'EXECUTED' ||
      p.guardrail.approval_status === 'REJECTED_BY_GUARDRAIL'
  );

  const liveRemainingBudget = Math.max(0, monthlyLimit - kpis.autonomous_budget_spent_usd);
  const budgetPercent = Math.min(
    100,
    Math.round((kpis.autonomous_budget_spent_usd / Math.max(monthlyLimit, 1)) * 100)
  );

  const getPresetBadge = (amount: number) => {
    if (amount > liveRemainingBudget) {
      return {
        amountClass: 'text-[#C53030]',
        borderHoverClass: 'hover:border-[#C53030]',
        statusLabel: 'Blocked by Cap',
        ruleLabel: `Hors plafond (${formatUSD(monthlyLimit)})`,
      };
    }
    if (amount <= autoThreshold) {
      return {
        amountClass: 'text-[#0E7C47]',
        borderHoverClass: 'hover:border-[#0E7C47]',
        statusLabel: 'Auto-Approved',
        ruleLabel: `≤ seuil ${formatUSD(autoThreshold)}`,
      };
    }
    return {
      amountClass: 'text-[#B45309]',
      borderHoverClass: 'hover:border-[#0070BA]',
      statusLabel: 'Requires 1-Click',
      ruleLabel: `> seuil ${formatUSD(autoThreshold)}`,
    };
  };

  const preset19 = getPresetBadge(19.5);
  const preset65 = getPresetBadge(65.0);
  const preset450 = getPresetBadge(450.0);

  const getActionButtonLabel = (sub: SubscriptionItem): string => {
    if (sub.recommended_action === 'DOWNGRADE_PLAN' && sub.downgrade_option) {
      return `Downgrade to ${sub.downgrade_option.target_plan_name.split(' ')[0]} (${formatUSD(
        sub.downgrade_option.new_monthly_cost
      )}/mo)`;
    }
    if (sub.recommended_action === 'SUSPEND_SUBSCRIPTION') {
      return 'Suspendre le prélèvement';
    }
    return 'Résilier l’abonnement';
  };

  const getStatusBadge = (sub: SubscriptionItem) => {
    if (sub.status === 'CANCELLED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#F1F5F9] text-[#475569]">
          Résilié sur PayPal
        </span>
      );
    }
    if (sub.status === 'SUSPENDED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#FEF5E7] text-[#B45309]">
          Suspendu sur PayPal
        </span>
      );
    }
    if (sub.status === 'DOWNGRADED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#EAF7F0] text-[#0E7C47]">
          Forfait optimisé
        </span>
      );
    }
    if (sub.risk_category === 'DORMANT_ZOMBIE') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#FFF0F0] text-[#C53030]">
          Inactif depuis {sub.telemetry.days_since_last_login} j
        </span>
      );
    }
    if (sub.risk_category === 'OVERPROVISIONED_SEATS') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#FEF5E7] text-[#B45309]">
          {sub.telemetry.active_seats}/{sub.telemetry.provisioned_seats} sièges utilisés
        </span>
      );
    }
    if (sub.risk_category === 'DUPLICATE_SAAS') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#FFF0F0] text-[#C53030]">
          Doublon détecté
        </span>
      );
    }
    if (sub.risk_category === 'TRIAL_TRAP_CONVERSION') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#FFF0F0] text-[#C53030] border border-[#C53030]/25">
          Fin d’essai 1 $ → {formatUSD(sub.monthly_cost)} dans {sub.telemetry.trial_days_remaining} j
        </span>
      );
    }
    if (sub.risk_category === 'HIDDEN_MICRO_TX') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#FEF5E7] text-[#B45309]">
          Hausse +{sub.telemetry.price_change_pct_last_90d}% sans usage
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-[#EAF7F0] text-[#0E7C47]">
        Usage optimal ({sub.telemetry.active_days_last_30d}/30 j)
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA] text-[#0C121D] pb-16">
      {/* Sticky Translucent Navigation Header (Apple Material & PayPal Identity) */}
      <header className="sticky top-0 z-30 surface-translucent border-b border-[#E2E8F0]">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#003087] flex items-center justify-center text-white font-bold text-base tracking-tight shadow-sm">
              P
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-[17px] tracking-tight text-[#003087]">
                  SentinelPay
                </span>
                <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-[#E8F3FF] text-[#003087]">
                  PayPal Treasury & Agentic Commerce
                </span>
              </div>
              <p className="text-xs text-[#718096] hidden sm:block">
                Autonomous Recurring SaaS Audit, 1-Click Arbitrage & PayPal Webhook Firewall
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            {/* Live Connection Status Pill */}
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-[#E2E8F0] text-xs font-medium text-[#4A5568]">
              <span
                className={`w-2 h-2 rounded-full ${
                  system_status.paypal_oauth_verified ? 'bg-[#0E7C47]' : 'bg-[#0070BA]'
                }`}
              />
              <span>
                {system_status.paypal_oauth_verified
                  ? 'PayPal Sandbox Connected (Live OAuth2)'
                  : 'PayPal Sandbox (Simulator Active)'}
              </span>
            </div>

            {system_status.paypal_configured && (
              <button
                type="button"
                onClick={handleSeedSandbox}
                disabled={busyId === 'SEED'}
                className="pressable inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E2E8F0] hover:border-[#CBD5E1] text-xs font-medium text-[#0C121D]"
              >
                <Database className="w-3.5 h-3.5 text-[#0070BA]" />
                <span>Seed Sandbox</span>
              </button>
            )}

            <button
              type="button"
              onClick={handleOpenCFOBoardpack}
              disabled={cfoLoading}
              className="pressable inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#003087] hover:bg-[#001C64] text-xs font-semibold text-white shadow-sm"
              title="Générer le rapport d'audit CFO certifié"
            >
              <FileText className="w-3.5 h-3.5 text-white" />
              <span>{cfoLoading ? 'Generating…' : 'CFO Boardpack'}</span>
            </button>

            <button
              type="button"
              onClick={() => setShowCredentialsModal(true)}
              className="pressable inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E2E8F0] hover:border-[#CBD5E1] text-xs font-medium text-[#0C121D]"
            >
              <KeyRound className="w-3.5 h-3.5 text-[#003087]" />
              <span>API Keys</span>
            </button>

            <button
              type="button"
              onClick={handleResetDemo}
              disabled={busyId === 'RESET'}
              className="pressable inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#E2E8F0] hover:border-[#CBD5E1] text-xs font-medium text-[#4A5568]"
              title="Reset Demo la démonstration"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Reset Demo</span>
            </button>
          </div>
        </div>
      </header>

      {/* Floating Feedback Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 max-w-md surface-translucent border border-[#003087]/20 shadow-lg rounded-xl px-4 py-3 flex items-center gap-3 spring-settle">
          <CheckCircle2 className="w-4 h-4 text-[#003087] shrink-0" />
          <span className="text-sm font-medium text-[#0C121D]">{toastMessage}</span>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 pt-7 space-y-6">
        {/* Primary Focal Point: PayPal Capital Recovery Banner (with 60fps Apple Number Ticker & Financial Health Score) */}
        <section id="kpi-banner" className="rounded-2xl bg-[#003087] text-white p-6 sm:p-8 shadow-sm space-y-5">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div className="lg:col-span-7 space-y-2.5">
              <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-white/10 text-xs font-medium text-[#D6ECFF]">
                <span>PayPal Portfolio Financial Synthesis</span>
                <span>•</span>
                <span>{executive_ai_brief.provider}</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-semibold heading-tight tabular-figure">
                {kpis.potential_annual_savings_usd > 0
                  ? `${formatUSD(animatedPotentialSavings)} annual savings identified across ${kpis.flagged_subscriptions_count} subscriptions`
                  : `Optimized Portfolio: ${formatUSD(animatedRealizedSavings)} saved this year`}
              </h1>
              <p className="text-sm text-[#D6ECFF]/90 max-w-2xl leading-relaxed">
                {executive_ai_brief.executive_summary}
              </p>
            </div>

            <div className="lg:col-span-5 flex flex-col sm:flex-row lg:flex-col xl:flex-row items-stretch sm:items-center justify-end gap-3">
              <div className="bg-white/10 rounded-xl px-4 py-3 border border-white/10 flex-1">
                <div className="text-xs text-[#D6ECFF]">Active Monthly Commitments</div>
                <div className="text-xl font-semibold tabular-figure mt-0.5">
                  {formatUSD(animatedMonthlySpend)}
                  <span className="text-xs font-normal text-[#D6ECFF]"> / mo</span>
                </div>
                <div className="text-xs text-[#9AE6B4] mt-1 tabular-figure">
                  Realized Savings: {formatUSD(animatedRealizedSavings)}/yr
                </div>
              </div>

              {kpis.flagged_subscriptions_count > 0 ? (
                <button
                  type="button"
                  onClick={handleBatchSweep}
                  disabled={busyId === 'SWEEP'}
                  className="pressable px-5 py-3.5 rounded-xl bg-white text-[#003087] hover:bg-[#F8FAFC] font-semibold text-sm shadow-sm shrink-0 tabular-figure"
                >
                  {busyId === 'SWEEP'
                    ? 'Executing PayPal Sweep…'
                    : `Optimize ${kpis.flagged_subscriptions_count} Subscriptions (${formatUSD(animatedPotentialSavings)}/yr)`}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleResetDemo}
                  className="pressable px-5 py-3.5 rounded-xl bg-white/15 hover:bg-white/25 text-white font-medium text-sm shrink-0"
                >
                  Reset Demo State
                </button>
              )}
            </div>
          </div>

          {/* Before / After & Financial Health Score Bar */}
          <div className="pt-4 border-t border-white/15 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            <div className="md:col-span-5 flex items-center gap-3">
              <div className="flex-1">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="text-[#D6ECFF] font-medium">
                    PayPal Financial Health Score
                  </span>
                  <span className="font-semibold tabular-figure text-white">
                    Health Score: {animatedHealthScore}/100
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-white/15 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      animatedHealthScore >= 80
                        ? 'bg-[#34D399]'
                        : animatedHealthScore >= 55
                        ? 'bg-[#60A5FA]'
                        : 'bg-[#FBBF24]'
                    }`}
                    style={{ width: `${animatedHealthScore}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="md:col-span-7 flex flex-wrap items-center justify-between md:justify-end gap-3 text-xs tabular-figure">
              <span className="px-3 py-1.5 rounded-lg bg-white/10 text-[#D6ECFF]">
                Before: <strong>{formatUSD(baselineMonthlySpend)}/mo</strong> → Current:{' '}
                <strong className="text-[#9AE6B4]">{formatUSD(animatedMonthlySpend)}/mo</strong>
              </span>
              <span className="px-3 py-1.5 rounded-lg bg-white/10 text-[#9AE6B4] font-medium">
                Net Gain: +{formatUSD(animatedRealizedSavings)}/yr
              </span>
            </div>
          </div>
        </section>

        {/* Live PayPal Webhook Trap Firewall Bar (The 30-Second Jaw-Drop Demo Moment) */}
        <section id="webhook-firewall" className="bg-white border border-[#E2E8F0] rounded-2xl p-4 sm:p-5 shadow-[0_1px_2px_rgba(12,18,29,0.03)] space-y-3.5">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3.5">
            <div className="flex items-start sm:items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#FFF0F0] border border-[#C53030]/20 flex items-center justify-center text-[#C53030] shrink-0">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-sm font-semibold text-[#0C121D]">
                    Real-Time PayPal Webhook Firewall (
                    <code className="font-mono text-xs text-[#003087]">PAYMENT.SALE.COMPLETED</code>{' '}
                    &{' '}
                    <code className="font-mono text-xs text-[#003087]">
                      BILLING.SUBSCRIPTION.RENEWED
                    </code>
                    )
                  </h2>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#EAF7F0] text-[#0E7C47]">
                    <Zap className="w-3 h-3" /> Zero-Trust Monitoring Active
                  </span>
                </div>
                <p className="text-xs text-[#718096] mt-0.5">
                  Intercepts free trial traps and stealth price hikes upon receiving cryptographically signed PayPal webhooks, suspends the billing agreement, and triggers instant capture refund.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => handleSimulateWebhookTrap('TRIAL_CONVERSION')}
                disabled={busyId === 'WEBHOOK-TRIAL_CONVERSION'}
                className="pressable px-3.5 py-2 rounded-xl bg-[#FFF0F0] hover:bg-[#FEE2E2] text-[#C53030] border border-[#C53030]/25 text-xs font-semibold tabular-figure"
              >
                {busyId === 'WEBHOOK-TRIAL_CONVERSION'
                  ? 'Intercepting Webhook…'
                  : 'Simulate Trial Trap $1 → $49'}
              </button>
              <button
                type="button"
                onClick={() => handleSimulateWebhookTrap('PRICE_HIKE')}
                disabled={busyId === 'WEBHOOK-PRICE_HIKE'}
                className="pressable px-3.5 py-2 rounded-xl bg-[#FEF5E7] hover:bg-[#FDE68A]/50 text-[#B45309] border border-[#B45309]/25 text-xs font-semibold tabular-figure"
              >
                {busyId === 'WEBHOOK-PRICE_HIKE'
                  ? 'Intercepting Webhook…'
                  : 'Simulate Stealth Hike +169% ($39)'}
              </button>
            </div>
          </div>

          {webhookInterception && (
            <div className="rounded-xl bg-[#EAF7F0] border border-[#0E7C47]/30 p-4 space-y-2.5 spring-settle">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#0E7C47] shrink-0" />
                  <span className="text-xs font-semibold text-[#0E7C47]">
                    Instant PayPal Refund Executed: +
                    {formatUSD(webhookInterception.intercepted_amount_usd)} refunded •{' '}
                    {formatUSD(webhookInterception.annual_saved_usd)}/yr saved
                  </span>
                </div>
                <span className="font-mono text-[11px] px-2 py-0.5 rounded bg-white border border-[#0E7C47]/20 text-[#0E7C47]">
                  PAYPAL-TRANSMISSION-SIG: {webhookInterception.transmission_sig}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-[#0C121D]">
                <div className="bg-white/90 rounded-lg p-2.5 border border-[#0E7C47]/15">
                  <div className="text-[11px] text-[#718096]">
                    1. Immediate PayPal Agreement Suspension (/suspend)
                  </div>
                  <div className="font-mono text-[11px] text-[#0C121D] mt-0.5">
                    {webhookInterception.suspend_receipt.http_method}{' '}
                    {webhookInterception.suspend_receipt.endpoint} (HTTP{' '}
                    {webhookInterception.suspend_receipt.http_status})
                  </div>
                </div>
                <div className="bg-white/90 rounded-lg p-2.5 border border-[#0E7C47]/15">
                  <div className="text-[11px] text-[#718096]">
                    2. Automated Capture Refund ({webhookInterception.descriptor})
                  </div>
                  <div className="font-mono text-[11px] text-[#0E7C47] font-semibold mt-0.5">
                    {webhookInterception.refund_receipt.http_method}{' '}
                    {webhookInterception.refund_receipt.endpoint} → Ref.{' '}
                    {webhookInterception.refund_receipt.paypal_resource_id}
                  </div>
                </div>
              </div>

              <PayPalJsonInspectorButton
                receipt={webhookInterception.refund_receipt}
                auditChainVerified={auditChainVerified}
              />
            </div>
          )}
        </section>

        {/* Main 2-Column Asymmetric Financial Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
          {/* LEFT COLUMN (7 cols): Recurring PayPal Subscriptions Ledger */}
          <div id="subscriptions-ledger" className="lg:col-span-7 space-y-5">
            <div className="bg-white border border-[#E2E8F0] rounded-2xl overflow-hidden shadow-[0_1px_2px_rgba(12,18,29,0.03)]">
              {/* Header + Apple Segmented Filter Control */}
              <div className="px-6 py-4 border-b border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h2 className="text-[17px] font-semibold heading-tight text-[#0C121D]">
                    PayPal Recurring Subscriptions
                  </h2>
                  <p className="text-xs text-[#718096]">
                    Click any row to inspect telemetry, AI arbitrage, and cryptographic PayPal receipts
                  </p>
                </div>

                {/* Segmented Pill Control */}
                <div className="inline-flex p-1 rounded-xl bg-[#F1F5F9] self-start">
                  <button
                    type="button"
                    onClick={() => setFilterTab('all')}
                    className={`pressable px-3 py-1 rounded-lg text-xs font-medium ${
                      filterTab === 'all'
                        ? 'bg-white text-[#0C121D] shadow-sm'
                        : 'text-[#4A5568] hover:text-[#0C121D]'
                    }`}
                  >
                    All ({subscriptions.length})
                  </button>
                  <button
                    type="button"
                    onClick={() => setFilterTab('flagged')}
                    className={`pressable px-3 py-1 rounded-lg text-xs font-medium ${
                      filterTab === 'flagged'
                        ? 'bg-white text-[#003087] shadow-sm'
                        : 'text-[#4A5568] hover:text-[#0C121D]'
                    }`}
                  >
                    Actionable ({kpis.flagged_subscriptions_count})
                  </button>
                  <button
                    type="button"
                    onClick={() => setFilterTab('resolved')}
                    className={`pressable px-3 py-1 rounded-lg text-xs font-medium ${
                      filterTab === 'resolved'
                        ? 'bg-white text-[#0E7C47] shadow-sm'
                        : 'text-[#4A5568] hover:text-[#0C121D]'
                    }`}
                  >
                    Optimized ({subscriptions.filter((s) => s.status !== 'ACTIVE').length})
                  </button>
                </div>
              </div>

              {/* Subscription Rows */}
              <div className="divide-y divide-[#E2E8F0]">
                {filteredSubscriptions.map((sub) => {
                  const isExpanded = expandedSubId === sub.id;
                  const matchingProposal = proposals.find(
                    (p) => p.target_subscription_id === sub.id
                  );
                  const canOptimize =
                    sub.status === 'ACTIVE' && sub.recommended_action !== 'KEEP_ACTIVE';
                  const rowBorderClass =
                    sub.status === 'ACTIVE' && sub.telemetry.price_change_pct_last_90d > 0
                      ? 'border-l-4 border-l-[#C53030]'
                      : sub.telemetry.price_change_pct_last_90d < 0
                      ? 'border-l-4 border-l-[#0E7C47]'
                      : 'border-l-4 border-l-transparent';

                  return (
                    <div
                      key={sub.id}
                      className={`transition-colors ${rowBorderClass} ${
                        isExpanded ? 'bg-[#F8FAFC]' : 'bg-white hover:bg-[#FAFBFD]'
                      }`}
                    >
                      {/* Main Scannable Row */}
                      <div
                        onClick={() => setExpandedSubId(isExpanded ? null : sub.id)}
                        className="px-6 py-4 flex items-center justify-between gap-4 cursor-pointer"
                      >
                        <div className="flex items-center gap-3.5 min-w-0">
                          <div
                            className={`w-10 h-10 rounded-xl flex items-center justify-center font-semibold text-xs shrink-0 ${
                              sub.status !== 'ACTIVE'
                                ? 'bg-[#F1F5F9] text-[#64748B]'
                                : canOptimize
                                ? 'bg-[#E8F3FF] text-[#003087]'
                                : 'bg-[#F1F5F9] text-[#0C121D]'
                            }`}
                          >
                            {sub.logo_text}
                          </div>

                          <div className="min-w-0">
                            <div className="flex items-center gap-2 flex-wrap">
                              <span
                                className={`font-semibold text-[15px] ${
                                  sub.status === 'CANCELLED'
                                    ? 'line-through text-[#718096]'
                                    : 'text-[#0C121D]'
                                }`}
                              >
                                {sub.vendor_name}
                              </span>
                              {getStatusBadge(sub)}
                            </div>
                            <div className="text-xs text-[#718096] mt-0.5 truncate">
                              {sub.plan_name} • PayPal Agreement{' '}
                              <code className="font-mono text-[11px] text-[#4A5568]">
                                {sub.paypal_subscription_id}
                              </code>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-3.5 shrink-0">
                          <div className="hidden sm:flex items-center">
                            <RevolutSparkline
                              history={sub.telemetry.price_history_6m}
                              priceDeltaPct={sub.telemetry.price_change_pct_last_90d}
                            />
                          </div>

                          <div className="text-right">
                            <div className="flex items-baseline justify-end gap-1.5">
                              {sub.telemetry.previous_monthly_cost > 0 &&
                                sub.telemetry.previous_monthly_cost !== sub.monthly_cost && (
                                  <span className="line-through text-xs text-[#94A3B8] tabular-figure">
                                    {formatUSD(sub.telemetry.previous_monthly_cost)}
                                  </span>
                                )}
                              <div className="font-semibold text-[15px] tabular-figure text-[#0C121D]">
                                {formatUSD(sub.monthly_cost)}
                                <span className="text-xs font-normal text-[#718096]">/mo</span>
                              </div>
                            </div>
                            <div className="mt-1 flex items-center justify-end gap-2">
                              <RevolutPriceDeltaBadge
                                priceDeltaPct={sub.telemetry.price_change_pct_last_90d}
                              />
                              {canOptimize && (
                                <span className="text-xs font-medium text-[#0070BA] tabular-figure">
                                  Savings: {formatUSD(sub.estimated_annual_savings)}/yr
                                </span>
                              )}
                            </div>
                          </div>

                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-[#718096]" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-[#718096]" />
                          )}
                        </div>
                      </div>

                      {/* Expanded Telemetry & Direct PayPal Action Sheet */}
                      {isExpanded && (
                        <div className="px-6 pb-5 pt-1 border-t border-[#E2E8F0]/60 space-y-4">
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
                            <div className="bg-white border border-[#E2E8F0] rounded-xl p-3">
                              <div className="text-[11px] text-[#718096]">Active Days (30d)</div>
                              <div className="text-sm font-semibold tabular-figure mt-0.5">
                                {sub.telemetry.active_days_last_30d} / 30 days
                              </div>
                            </div>
                            <div className="bg-white border border-[#E2E8F0] rounded-xl p-3">
                              <div className="text-[11px] text-[#718096]">Active Seats</div>
                              <div className="text-sm font-semibold tabular-figure mt-0.5">
                                {sub.telemetry.active_seats} / {sub.telemetry.provisioned_seats}{' '}
                                seat(s)
                              </div>
                            </div>
                            <div className="bg-white border border-[#E2E8F0] rounded-xl p-3">
                              <div className="text-[11px] text-[#718096]">Cost per Active Day</div>
                              <div className="text-sm font-semibold tabular-figure mt-0.5">
                                {formatUSD(sub.cost_per_active_day)}
                              </div>
                            </div>
                            <div className="bg-white border border-[#E2E8F0] rounded-xl p-3">
                              <div className="text-[11px] text-[#718096]">Waste Score</div>
                              <div className="text-sm font-semibold tabular-figure mt-0.5">
                                {sub.waste_score} / 100
                              </div>
                            </div>

                            {/* 5th Info Pill / Banner: 6-month Revolut Price Trajectory, Descriptor & Data-Retention Lock */}
                            <div className="col-span-2 sm:col-span-4 bg-white border border-[#E2E8F0] rounded-xl p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                              <div className="flex items-center gap-3 flex-wrap">
                                <RevolutSparkline
                                  history={sub.telemetry.price_history_6m}
                                  priceDeltaPct={sub.telemetry.price_change_pct_last_90d}
                                />
                                <div>
                                  <div className="text-xs font-semibold text-[#0C121D] tabular-figure flex items-center gap-2 flex-wrap">
                                    <span>
                                      Previous Rate: {formatUSD(sub.telemetry.previous_monthly_cost)}{' '}
                                      → Current Rate: {formatUSD(sub.monthly_cost)}
                                    </span>
                                    <RevolutPriceDeltaBadge
                                      priceDeltaPct={sub.telemetry.price_change_pct_last_90d}
                                    />
                                  </div>
                                  <div className="text-[11px] text-[#718096] mt-0.5 font-mono">
                                    Descriptor: {sub.telemetry.raw_paypal_descriptor} • 6-Month Trend:{' '}
                                    {sub.telemetry.price_history_6m
                                      .map((p) => formatUSD(p))
                                      .join(' → ')}
                                  </div>
                                </div>
                              </div>

                              <div className="flex items-center gap-1.5 shrink-0">
                                {sub.telemetry.has_data_retention_or_contract_lock ? (
                                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-[#FEF5E7] text-[#B45309] border border-[#B45309]/20">
                                    Data Retention / Contract Lock Active (/suspend preferred)
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-[#EAF7F0] text-[#0E7C47] border border-[#0E7C47]/20">
                                    No Data Lock (Safe Direct /cancel)
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="bg-white border border-[#E2E8F0] rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                            <div className="space-y-1">
                              <div className="text-xs font-semibold text-[#003087]">
                                Usage Telemetry & Rationale
                              </div>
                              <p className="text-xs text-[#4A5568] leading-relaxed">
                                {sub.ai_audit_rationale}
                              </p>
                            </div>

                            {canOptimize && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSingleRemediate(sub);
                                }}
                                disabled={busyId === sub.id}
                                className="pressable px-4 py-2.5 rounded-xl bg-[#0070BA] hover:bg-[#003087] text-white text-xs font-semibold shrink-0 shadow-sm"
                              >
                                {busyId === sub.id
                                  ? 'Calling PayPal API…'
                                  : getActionButtonLabel(sub)}
                              </button>
                            )}
                          </div>

                          {/* 1-Click SaaS Auto-Switch Arbitrage Card */}
                          {sub.status === 'ACTIVE' && sub.switch_alternative && (
                            <div className="bg-[#E8F3FF]/70 border border-[#0070BA]/30 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                              <div className="space-y-1">
                                <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#003087]">
                                  <ArrowRightLeft className="w-3.5 h-3.5 text-[#0070BA]" />
                                  <span>
                                    AI Arbitrage / Recommended Alternative:{' '}
                                    {sub.switch_alternative.alternative_vendor} (
                                    {sub.switch_alternative.alternative_plan})
                                  </span>
                                </div>
                                <p className="text-xs text-[#4A5568] leading-relaxed">
                                  {sub.switch_alternative.migration_rationale} •{' '}
                                  <strong className="text-[#0E7C47] tabular-figure">
                                    Net Savings:{' '}
                                    {formatUSD(sub.switch_alternative.annual_net_savings)}/yr
                                  </strong>
                                </p>
                              </div>

                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleAutoSwitch(sub);
                                }}
                                disabled={busyId === `SWITCH-${sub.id}`}
                                className="pressable px-4 py-2.5 rounded-xl bg-[#003087] hover:bg-[#001C64] text-white text-xs font-semibold shrink-0 shadow-sm tabular-figure"
                              >
                                {busyId === `SWITCH-${sub.id}`
                                  ? 'Executing PayPal Arbitrage…'
                                  : `Switch to ${
                                      sub.switch_alternative.alternative_vendor
                                    } (${formatUSD(
                                      sub.switch_alternative.new_monthly_cost
                                    )}/mo)`}
                              </button>
                            </div>
                          )}

                          {/* Active B2B Retention Negotiation Action */}
                          {sub.status === 'ACTIVE' && (
                            <div className="bg-[#FAFBFD] border border-[#CBD5E1]/60 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                              <div className="space-y-1">
                                <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#003087]">
                                  <Handshake className="w-3.5 h-3.5 text-[#003087]" />
                                  <span>Autonomous B2B Retention Negotiation (Gemini AI)</span>
                                </div>
                                <p className="text-xs text-[#4A5568] leading-relaxed">
                                  Generate formal legal notice based on verified telemetry and obtain a 40% enterprise discount via PayPal /revise.
                                </p>
                              </div>
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleOpenNegotiation(sub);
                                }}
                                disabled={negotiationLoading && negotiatingSub?.id === sub.id}
                                className="pressable px-3.5 py-2 rounded-xl bg-white border border-[#003087]/30 hover:border-[#003087] text-[#003087] text-xs font-semibold shrink-0 shadow-xs hover:bg-[#F0F4FF] transition-all"
                              >
                                {negotiationLoading && negotiatingSub?.id === sub.id
                                  ? 'Negotiating…'
                                  : 'Negotiate B2B Discount (-40%)'}
                              </button>
                            </div>
                          )}

                          {/* If executed on PayPal Sandbox, display official REST API receipt + JSON Inspector */}
                          {matchingProposal?.paypal_receipt && (
                            <div className="bg-[#EAF7F0] border border-[#0E7C47]/20 rounded-xl p-3.5 text-xs space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-[#0E7C47] flex items-center gap-1.5">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  PayPal Execution Receipt (
                                  {matchingProposal.paypal_receipt.execution_mode})
                                </span>
                                <code className="font-mono text-[11px] text-[#0E7C47]">
                                  HTTP {matchingProposal.paypal_receipt.http_status}
                                </code>
                              </div>
                              <div className="font-mono text-[11px] text-[#4A5568] break-all">
                                {matchingProposal.paypal_receipt.http_method}{' '}
                                {matchingProposal.paypal_receipt.endpoint} • Request-ID:{' '}
                                {matchingProposal.paypal_receipt.paypal_request_id}
                              </div>
                              <PayPalJsonInspectorButton
                                receipt={matchingProposal.paypal_receipt}
                                auditChainVerified={auditChainVerified}
                              />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Natural Language Financial Instruction Bar (Gemini Integration, Zero AI Cliché) */}
            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 space-y-3 shadow-[0_1px_2px_rgba(12,18,29,0.03)]">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-[#0C121D]">
                  Natural Language Financial Command
                </h3>
                <span className="text-xs text-[#718096]">
                  E.g., "Buy $18 in GPU credits via PayPal" or "Cancel idle SaaS subscriptions"
                </span>
              </div>

              <form onSubmit={handleSendCommand} className="flex gap-2.5">
                <input
                  type="text"
                  value={commandInput}
                  onChange={(e) => setCommandInput(e.target.value)}
                  placeholder="Enter an autonomous treasury instruction or purchase order…"
                  className="flex-1 rounded-xl border border-[#CBD5E1] px-3.5 py-2.5 text-sm text-[#0C121D] placeholder-[#94A3B8] focus:outline-none focus:border-[#0070BA]"
                />
                <button
                  type="submit"
                  disabled={commandBusy}
                  className="pressable px-4 py-2.5 rounded-xl bg-[#003087] hover:bg-[#001C64] text-white text-sm font-medium inline-flex items-center gap-2 shrink-0"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{commandBusy ? 'Analyzing…' : 'Execute'}</span>
                </button>
              </form>

              {commandReply && (
                <div className="p-3.5 rounded-xl bg-[#E8F3FF]/60 border border-[#0070BA]/20 text-xs text-[#0C121D] leading-relaxed">
                  {commandReply}
                </div>
              )}
            </div>
          </div>

          {/* RIGHT COLUMN (5 cols): Budget Guardrails, 1-Click Approval Queue & PayPal Orders v2 */}
          <div id="guardrails-panel" className="lg:col-span-5 space-y-5">
            {/* 1-Click Human Approval Queue (Highlighted when items are waiting) */}
            {pendingApprovals.length > 0 && (
              <div className="bg-white border-2 border-[#0070BA] rounded-2xl p-5 space-y-3.5 shadow-sm">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-[#0070BA]" />
                    <h3 className="text-[15px] font-semibold text-[#0C121D]">
                      Pending 1-Click Approvals ({pendingApprovals.length})
                    </h3>
                  </div>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-md bg-[#E8F3FF] text-[#003087]">
                    Action Required
                  </span>
                </div>

                <div className="space-y-3">
                  {pendingApprovals.map((prop) => (
                    <div
                      key={prop.proposal_id}
                      className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="font-semibold text-sm text-[#0C121D]">
                            {prop.vendor_name} — {prop.title}
                          </div>
                          <p className="text-xs text-[#4A5568] mt-0.5">{prop.guardrail.reason}</p>
                        </div>
                        <span className="font-semibold text-sm tabular-figure text-[#003087]">
                          {formatUSD(prop.amount_usd)}
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() => handleApproveProposal(prop)}
                        disabled={busyId === prop.proposal_id}
                        className="pressable w-full py-2.5 px-4 rounded-xl bg-[#0070BA] hover:bg-[#003087] text-white text-xs font-semibold shadow-sm"
                      >
                        {busyId === prop.proposal_id
                          ? 'Creating PayPal Order v2…'
                          : `Approve PayPal Order (${formatUSD(prop.amount_usd)})`}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Budget Guardrails & Policy Card (Apple 1:1 Direct Manipulation Sliders) */}
            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 space-y-4 shadow-[0_1px_2px_rgba(12,18,29,0.03)]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-[#003087]" />
                  <h3 className="text-[15px] font-semibold text-[#0C121D]">
                    Autonomous Budget Guardrails
                  </h3>
                </div>
                <SlidersHorizontal className="w-4 h-4 text-[#718096]" />
              </div>

              {/* Spend Bar */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-[#4A5568]">
                    Spent this month:{' '}
                    <strong className="text-[#0C121D] tabular-figure">
                      {formatUSD(kpis.autonomous_budget_spent_usd)}
                    </strong>
                  </span>
                  <span className="text-[#4A5568] tabular-figure">
                    Monthly Cap: {formatUSD(monthlyLimit)}
                  </span>
                </div>
                <div className="w-full h-2.5 bg-[#E2E8F0] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#0070BA] rounded-full transition-all duration-300"
                    style={{ width: `${budgetPercent}%` }}
                  />
                </div>
                <div className="text-[11px] text-[#718096] flex justify-between tabular-figure">
                  <span>Remaining: {formatUSD(liveRemainingBudget)}</span>
                  <span>Auto-Approve ≤ {formatUSD(autoThreshold)}</span>
                </div>
              </div>

              {/* Interactive Sliders (1:1 at 60fps onChange, network commit on release) */}
              <div className="pt-2 border-t border-[#E2E8F0] grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-[#4A5568] mb-1 tabular-figure">
                    Monthly Cap ({formatUSD(monthlyLimit)})
                  </label>
                  <input
                    type="range"
                    min={50}
                    max={500}
                    step={10}
                    value={monthlyLimit}
                    onChange={(e) => setMonthlyLimit(Number(e.target.value))}
                    onMouseUp={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    onTouchEnd={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    onKeyUp={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    className="w-full accent-[#003087] cursor-pointer"
                  />
                </div>
                <div>
                  <label className="block text-[#4A5568] mb-1 tabular-figure">
                    Zero-Click Threshold ({formatUSD(autoThreshold)})
                  </label>
                  <input
                    type="range"
                    min={5}
                    max={100}
                    step={5}
                    value={autoThreshold}
                    onChange={(e) => setAutoThreshold(Number(e.target.value))}
                    onMouseUp={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    onTouchEnd={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    onKeyUp={() => handlePolicySave(monthlyLimit, autoThreshold)}
                    className="w-full accent-[#0070BA] cursor-pointer"
                  />
                </div>
              </div>
            </div>

            {/* Agentic Commerce Order Simulator (/v2/checkout/orders) */}
            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 space-y-4 shadow-[0_1px_2px_rgba(12,18,29,0.03)]">
              <div>
                <h3 className="text-[15px] font-semibold text-[#0C121D]">
                  Autonomous Purchases (PayPal Orders v2)
                </h3>
                <p className="text-xs text-[#718096] mt-0.5">
                  Test the 3 policy tiers against the live endpoint{' '}
                  <code className="font-mono text-[11px]">/v2/checkout/orders</code>
                </p>
              </div>

              {/* 3 Quick-Test Presets (Dynamically reactive to live slider positions!) */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() =>
                    handleQuickPurchaseScenario(
                      'RunPod GPU Cloud',
                      'API Credit Top-up',
                      19.5,
                      `Test order (${formatUSD(19.5)}) vs auto-approval threshold ${formatUSD(autoThreshold)}`
                    )
                  }
                  disabled={busyId === 'PURCHASE-19.5'}
                  className={`pressable p-2.5 rounded-xl border border-[#E2E8F0] ${preset19.borderHoverClass} bg-[#F8FAFC] text-left`}
                >
                  <div className={`text-xs font-semibold ${preset19.amountClass} tabular-figure`}>
                    19,50 $
                  </div>
                  <div className="text-[11px] font-medium text-[#0C121D] mt-0.5">
                    {preset19.statusLabel}
                  </div>
                  <div className="text-[10px] text-[#718096] tabular-figure">
                    {preset19.ruleLabel}
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleQuickPurchaseScenario(
                      'Anthropic Enterprise',
                      'Production Token Pack',
                      65.0,
                      `Test order (${formatUSD(65.0)}) vs threshold ${formatUSD(autoThreshold)} (approval required)`
                    )
                  }
                  disabled={busyId === 'PURCHASE-65'}
                  className={`pressable p-2.5 rounded-xl border border-[#E2E8F0] ${preset65.borderHoverClass} bg-[#F8FAFC] text-left`}
                >
                  <div className={`text-xs font-semibold ${preset65.amountClass} tabular-figure`}>
                    65,00 $
                  </div>
                  <div className="text-[11px] font-medium text-[#0C121D] mt-0.5">
                    {preset65.statusLabel}
                  </div>
                  <div className="text-[10px] text-[#718096] tabular-figure">
                    {preset65.ruleLabel}
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleQuickPurchaseScenario(
                      'AWS Dedicated Node',
                      'Dedicated H100 Instance',
                      450.0,
                      `Test order (${formatUSD(450.0)}) vs monthly budget limit ${formatUSD(monthlyLimit)} (blocked)`
                    )
                  }
                  disabled={busyId === 'PURCHASE-450'}
                  className={`pressable p-2.5 rounded-xl border border-[#E2E8F0] ${preset450.borderHoverClass} bg-[#F8FAFC] text-left`}
                >
                  <div className={`text-xs font-semibold ${preset450.amountClass} tabular-figure`}>
                    450,00 $
                  </div>
                  <div className="text-[11px] font-medium text-[#0C121D] mt-0.5">
                    {preset450.statusLabel}
                  </div>
                  <div className="text-[10px] text-[#718096] tabular-figure">
                    {preset450.ruleLabel}
                  </div>
                </button>
              </div>

              {/* Clean Disclosure Toggle for Custom Order Form */}
              <div className="pt-2 border-t border-[#E2E8F0]">
                <button
                  type="button"
                  onClick={() => setShowCustomOrderForm((prev) => !prev)}
                  className="w-full flex items-center justify-between text-xs font-medium text-[#4A5568] hover:text-[#003087] py-1"
                >
                  <span>Customize purchase order…</span>
                  {showCustomOrderForm ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>

                {showCustomOrderForm && (
                  <form onSubmit={handleCustomPurchaseSubmit} className="pt-2.5 space-y-2.5">
                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={vendorName}
                        onChange={(e) => setVendorName(e.target.value)}
                        placeholder="Vendor"
                        className="rounded-lg border border-[#CBD5E1] px-3 py-1.5 text-xs"
                      />
                      <input
                        type="text"
                        value={itemName}
                        onChange={(e) => setItemName(e.target.value)}
                        placeholder="Service / Resource"
                        className="rounded-lg border border-[#CBD5E1] px-3 py-1.5 text-xs"
                      />
                    </div>
                    <div className="flex gap-2">
                      <select
                        value={orderCategory}
                        onChange={(e) => setOrderCategory(e.target.value)}
                        className="rounded-lg border border-[#CBD5E1] px-2.5 py-1.5 text-xs bg-white flex-1"
                      >
                        <option value="Cloud & AI Compute">Cloud & AI Compute</option>
                        <option value="Developer Tools">Developer Tools</option>
                        <option value="Security & Infra">Security & Infra</option>
                        <option value="Non-Whitelisted Gaming">
                          Restricted Category (Policy Violation Test)
                        </option>
                      </select>
                      <input
                        type="number"
                        step="0.50"
                        value={orderAmount}
                        onChange={(e) => setOrderAmount(e.target.value)}
                        className="w-24 rounded-lg border border-[#CBD5E1] px-3 py-1.5 text-xs tabular-figure"
                      />
                      <button
                        type="submit"
                        className="pressable px-3.5 py-1.5 rounded-lg bg-[#003087] hover:bg-[#001C64] text-white text-xs font-semibold shrink-0"
                      >
                        Create Order
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>

            {/* Verified PayPal Receipts & Cryptographic Audit Trail */}
            <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 space-y-3.5 shadow-[0_1px_2px_rgba(12,18,29,0.03)]">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <h3 className="text-[15px] font-semibold text-[#0C121D]">
                    PayPal Audit Trail & SHA-256 Ledger
                  </h3>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#EAF7F0] text-[#0E7C47]">
                    {auditChainVerified ? 'SHA-256 Chain Verified' : 'Audit Active'}
                  </span>
                </div>
                <span className="text-xs text-[#718096]">{audit_trail.length} events</span>
              </div>

              {executedProposals.length > 0 && (
                <div className="space-y-2">
                  {executedProposals.slice(0, 3).map((prop) => (
                    <div
                      key={prop.proposal_id}
                      className={`p-3 rounded-xl border text-xs ${
                        prop.guardrail.approval_status === 'REJECTED_BY_GUARDRAIL'
                          ? 'bg-[#FFF0F0]/60 border-[#C53030]/20'
                          : 'bg-[#F8FAFC] border-[#E2E8F0]'
                      }`}
                    >
                      <div className="flex items-center justify-between font-medium gap-2">
                        <span className="flex items-center gap-1.5 text-[#0C121D]">
                          {prop.guardrail.approval_status === 'REJECTED_BY_GUARDRAIL' ? (
                            <XCircle className="w-3.5 h-3.5 text-[#C53030] shrink-0" />
                          ) : (
                            <CheckCircle2 className="w-3.5 h-3.5 text-[#0E7C47] shrink-0" />
                          )}
                          <span>
                            {prop.vendor_name} ({prop.title})
                          </span>
                        </span>
                        <span className="tabular-figure shrink-0">
                          {prop.amount_usd > 0
                            ? formatUSD(prop.amount_usd)
                            : `-${formatUSD(prop.annual_savings_usd)}/an`}
                        </span>
                      </div>
                      {prop.paypal_receipt ? (
                        <div className="mt-1 space-y-1">
                          <div className="flex items-center justify-between text-[11px] text-[#718096]">
                            <code className="font-mono">
                              PayPal ID: {prop.paypal_receipt.paypal_resource_id}
                            </code>
                            {prop.paypal_receipt.approval_url && (
                              <a
                                href={prop.paypal_receipt.approval_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1 text-[#0070BA] hover:underline font-medium"
                              >
                                <span>Sandbox Checkout Link</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                          <PayPalJsonInspectorButton
                            receipt={prop.paypal_receipt}
                            auditChainVerified={auditChainVerified}
                          />
                        </div>
                      ) : (
                        <div className="mt-1 text-[11px] text-[#C53030]">
                          {prop.guardrail.reason}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <div className="max-h-56 overflow-y-auto divide-y divide-[#E2E8F0] border-t border-[#E2E8F0] pt-2">
                {audit_trail.slice(0, 8).map((evt) => (
                  <div key={evt.event_id} className="py-2.5 text-xs space-y-0.5">
                    <div className="flex items-center justify-between text-[11px] text-[#718096]">
                      <span className="font-medium text-[#003087]">{evt.stage}</span>
                      <code className="font-mono">SHA256: {evt.sha256_hash.slice(0, 12)}…</code>
                    </div>
                    <div className="text-[#0C121D]">{evt.summary}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Credentials Configuration Modal Sheet */}
      {showCredentialsModal && (
        <div className="fixed inset-0 z-50 bg-[#0C121D]/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl spring-settle">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-[#0C121D]">
                PayPal Sandbox & Google Gemini Credentials
              </h3>
              <button
                type="button"
                onClick={() => setShowCredentialsModal(false)}
                className="text-xs text-[#718096] hover:text-[#0C121D]"
              >
                Close
              </button>
            </div>

            <p className="text-xs text-[#4A5568] leading-relaxed">
              Collez vos clés PayPal Developer Sandbox et Gemini pour passer instantanément du
              simulateur local aux appels API PayPal Sandbox en direct (persistés dans{' '}
              <code className="font-mono">.env</code>).
            </p>

            {system_status.paypal_client_id_masked && (
              <div className="px-3 py-2 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-xs text-[#4A5568]">
                Client ID configuré :{' '}
                <code className="font-mono text-[#0C121D]">
                  {system_status.paypal_client_id_masked}
                </code>
              </div>
            )}

            <form onSubmit={handleCredentialsSubmit} className="space-y-3" autoComplete="off">
              <div>
                <label className="block text-xs font-medium text-[#0C121D] mb-1">
                  PayPal Sandbox Client ID
                </label>
                <input
                  type="password"
                  autoComplete="off"
                  value={paypalClientId}
                  onChange={(e) => setPaypalClientId(e.target.value)}
                  placeholder="Ex. Aeb123..."
                  className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#0C121D] mb-1">
                  PayPal Sandbox Secret
                </label>
                <input
                  type="password"
                  autoComplete="off"
                  value={paypalClientSecret}
                  onChange={(e) => setPaypalClientSecret(e.target.value)}
                  placeholder="Ex. EJo987..."
                  className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[#0C121D] mb-1">
                  Clé API Google Gemini (gemini-2.5-flash)
                </label>
                <input
                  type="password"
                  autoComplete="off"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  placeholder="Ex. AIzaSy..."
                  className="w-full rounded-xl border border-[#CBD5E1] px-3 py-2 text-xs font-mono"
                />
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowCredentialsModal(false)}
                  className="pressable px-4 py-2 rounded-xl border border-[#E2E8F0] text-xs font-medium text-[#4A5568]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={busyId === 'CREDS'}
                  className="pressable px-4 py-2 rounded-xl bg-[#003087] hover:bg-[#001C64] text-white text-xs font-semibold"
                >
                  {busyId === 'CREDS' ? 'Verifying OAuth2…' : 'Save & Connect Live'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Corporate CFO Audit Boardpack Modal */}
      {showCFOModal && cfoBoardpack && (
        <div id="cfo-modal" className="fixed inset-0 z-50 bg-[#0C121D]/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl max-w-3xl w-full p-6 space-y-6 shadow-2xl my-8 spring-settle">
            <div className="flex items-start justify-between border-b border-[#E2E8F0] pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#003087]" />
                  <h3 className="text-lg font-bold text-[#003087]">
                    Corporate CFO Audit Boardpack
                  </h3>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#E8F3FF] text-[#003087]">
                    {cfoBoardpack.report_id}
                  </span>
                </div>
                <p className="text-xs text-[#718096]">
                  {cfoBoardpack.organization} • {cfoBoardpack.certification}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="pressable inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-[#CBD5E1] hover:border-[#003087] text-xs font-semibold text-[#0C121D]"
                >
                  <Printer className="w-3.5 h-3.5 text-[#003087]" />
                  <span>Print / Export PDF</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowCFOModal(false)}
                  className="p-1.5 rounded-lg text-[#718096] hover:bg-[#F1F5F9] hover:text-[#0C121D]"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* KPI Benchmarks Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <div className="text-[11px] font-medium text-[#718096]">Baseline Spend</div>
                <div className="text-sm font-bold text-[#4A5568] tabular-figure line-through">
                  {formatUSD(cfoBoardpack.kpi_summary.baseline_monthly_spend_usd)}/mo
                </div>
                <div className="text-[11px] text-[#A0AEC0]">
                  {formatUSD(cfoBoardpack.kpi_summary.baseline_annual_spend_usd)}/yr
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-1">
                <div className="text-[11px] font-medium text-[#718096]">Current Spend</div>
                <div className="text-base font-bold text-[#003087] tabular-figure">
                  {formatUSD(cfoBoardpack.kpi_summary.current_monthly_spend_usd)}/mo
                </div>
                <div className="text-[11px] text-[#718096]">
                  {formatUSD(cfoBoardpack.kpi_summary.current_annual_spend_usd)}/yr
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#EAF7F0] border border-[#0E7C47]/20 space-y-1">
                <div className="text-[11px] font-medium text-[#0E7C47]">Realized Savings</div>
                <div className="text-base font-bold text-[#0E7C47] tabular-figure">
                  {formatUSD(cfoBoardpack.kpi_summary.realized_annual_savings_usd)}/yr
                </div>
                <div className="text-[11px] text-[#0E7C47] font-semibold">
                  -{cfoBoardpack.kpi_summary.percentage_spend_reduction}% reduction
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-[#E8F3FF] border border-[#0070BA]/20 space-y-1">
                <div className="text-[11px] font-medium text-[#003087]">Health Score</div>
                <div className="text-base font-bold text-[#003087] tabular-figure">
                  {cfoBoardpack.financial_health_score}/100
                </div>
                <div className="text-[11px] text-[#0070BA] font-semibold">
                  Treasury Grade A+
                </div>
              </div>
            </div>

            {/* Executive AI Brief Section */}
            <div className="bg-[#FAFBFD] border border-[#E2E8F0] rounded-xl p-4 space-y-2">
              <div className="text-xs font-semibold text-[#003087] flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#003087]" />
                Executive Summary for the Board of Directors
              </div>
              <p className="text-xs text-[#4A5568] leading-relaxed">
                {cfoBoardpack.executive_summary ||
                  "Audit complet des mandats de facturation récurrente PayPal exécuté. Les anomalies de surprovisionnement, les hausses tarifaires furtives et les conversions d'essai gratuit ont été purgées avec succès."}
              </p>
            </div>

            {/* Certified Subscriptions Matrix */}
            <div className="space-y-2">
              <div className="text-xs font-semibold text-[#0C121D]">
                PayPal Subscriptions Matrix ({cfoBoardpack.subscriptions_matrix.length} audited)
              </div>
              <div className="border border-[#E2E8F0] rounded-xl overflow-hidden">
                <table className="w-full text-xs text-left">
                  <thead className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[#718096] font-medium">
                    <tr>
                      <th className="py-2.5 px-3">Vendor & Plan</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Monthly Cost</th>
                      <th className="py-2.5 px-3 text-right">Waste Score</th>
                      <th className="py-2.5 px-3 text-right">Savings Unlocked</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2E8F0]">
                    {cfoBoardpack.subscriptions_matrix.map((row) => (
                      <tr key={row.paypal_agreement_id} className="hover:bg-[#F8FAFC]">
                        <td className="py-2 px-3">
                          <div className="font-semibold text-[#0C121D]">{row.vendor}</div>
                          <div className="text-[11px] text-[#718096] font-mono">
                            {row.paypal_agreement_id} • {row.plan}
                          </div>
                        </td>
                        <td className="py-2 px-3">
                          <span
                            className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                              row.status === 'DOWNGRADED'
                                ? 'bg-[#E8F3FF] text-[#003087]'
                                : row.status === 'CANCELLED'
                                ? 'bg-[#FEE2E2] text-[#991B1B]'
                                : 'bg-[#EAF7F0] text-[#0E7C47]'
                            }`}
                          >
                            {row.status}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-right font-medium text-[#0C121D] tabular-figure">
                          {formatUSD(row.monthly_cost)}
                        </td>
                        <td className="py-2 px-3 text-right tabular-figure">
                          <span
                            className={`font-semibold ${
                              row.waste_score >= 70
                                ? 'text-[#C53030]'
                                : row.waste_score >= 40
                                ? 'text-[#D69E2E]'
                                : 'text-[#0E7C47]'
                            }`}
                          >
                            {row.waste_score}/100
                          </span>
                        </td>
                        <td className="py-2 px-3 text-right font-bold text-[#0E7C47] tabular-figure">
                          +{formatUSD(row.annual_savings)}/yr
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Cryptographic Proof & Signoff */}
            <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="space-y-1">
                <div className="flex items-center gap-1.5 font-semibold text-[#0E7C47]">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Cryptographic SHA-256 Chain Verified
                </div>
                <div className="font-mono text-[11px] text-[#718096] break-all">
                  Block: {cfoBoardpack.cryptographic_proof.latest_sha256_hash}
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="font-semibold text-[#003087]">
                  {cfoBoardpack.cfo_signoff.auditor_role}
                </div>
                <div className="text-[11px] text-[#718096]">
                  {cfoBoardpack.cfo_signoff.status}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* B2B Retention Negotiation Modal */}
      {negotiatingSub && (
        <div id="b2b-modal" className="fixed inset-0 z-50 bg-[#0C121D]/50 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl max-w-2xl w-full p-6 space-y-5 shadow-2xl my-8 spring-settle">
            <div className="flex items-start justify-between border-b border-[#E2E8F0] pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <Handshake className="w-5 h-5 text-[#003087]" />
                  <h3 className="text-base font-bold text-[#0C121D]">
                    B2B Retention Negotiation — {negotiatingSub.vendor_name}
                  </h3>
                </div>
                <p className="text-xs text-[#718096]">
                  PayPal Agreement #{negotiatingSub.paypal_subscription_id} • Current Plan: {negotiatingSub.plan_name} ({formatUSD(negotiatingSub.monthly_cost)}/mo)
                </p>
              </div>
              <button
                type="button"
                onClick={() => setNegotiatingSub(null)}
                className="p-1.5 rounded-lg text-[#718096] hover:bg-[#F1F5F9] hover:text-[#0C121D]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {negotiationLoading ? (
              <div className="py-12 text-center space-y-3">
                <div className="w-7 h-7 border-2 border-[#003087] border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs font-semibold text-[#003087]">
                  SentinelPay AI is auditing telemetry and generating formal legal notice…
                </p>
              </div>
            ) : negotiationResult ? (
              <div className="space-y-4">
                {/* Formal Ultimatum Letter */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-[#0C121D] flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-[#003087]" />
                    AI Notice to Vendor Accounts (Derived from Real Telemetry)
                  </label>
                  <pre className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#CBD5E1] text-[11px] font-mono text-[#334155] whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                    {negotiationResult.ultimatum_letter}
                  </pre>
                </div>

                {/* Vendor Retention Counter-Offer */}
                <div className="p-4 rounded-xl bg-[#EAF7F0] border border-[#0E7C47]/30 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#0E7C47] flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      Retention Counter-Offer Accepted (40% Discount Authorized)
                    </span>
                    <span className="text-xs font-bold text-[#0E7C47] tabular-figure">
                      +{formatUSD(negotiationResult.counter_offer.annual_savings_usd)}/an annual savings
                    </span>
                  </div>
                  <p className="text-xs text-[#2D3748] leading-relaxed italic">
                    « {negotiationResult.counter_offer.vendor_response_message} »
                  </p>
                  <div className="pt-2 flex items-center gap-4 text-xs">
                    <div>
                      <span className="text-[#718096]">Previous price: </span>
                      <span className="font-semibold text-[#A0AEC0] line-through tabular-figure">
                        {formatUSD(negotiatingSub.monthly_cost)}/mois
                      </span>
                    </div>
                    <div>
                      <span className="text-[#718096]">Negotiated new price: </span>
                      <span className="font-bold text-[#003087] tabular-figure">
                        {formatUSD(negotiationResult.counter_offer.proposed_monthly_cost)}/mois
                      </span>
                    </div>
                  </div>
                </div>

                {/* Action CTA */}
                <div className="pt-2 flex items-center justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setNegotiatingSub(null)}
                    className="pressable px-4 py-2.5 rounded-xl border border-[#CBD5E1] text-xs font-medium text-[#4A5568]"
                  >
                    Close
                  </button>

                  {negotiationResult.discount_applied_on_paypal ? (
                    <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0E7C47] text-white text-xs font-semibold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Discount Applied on PayPal via /revise</span>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={handleApplyNegotiationDiscount}
                      disabled={busyId === `APPLY-NEG-${negotiatingSub.id}`}
                      className="pressable inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#003087] hover:bg-[#001C64] text-white text-xs font-bold shadow-md"
                    >
                      <Handshake className="w-4 h-4" />
                      <span>
                        {busyId === `APPLY-NEG-${negotiatingSub.id}`
                          ? 'Updating PayPal Agreement via /revise…'
                          : `Apply 40% Discount on PayPal via /revise (${formatUSD(
                              negotiationResult.counter_offer.proposed_monthly_cost
                            )}/mo)`}
                      </span>
                    </button>
                  )}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}
