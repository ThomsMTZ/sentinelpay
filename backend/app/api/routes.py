from typing import Any
from fastapi import APIRouter, Body, HTTPException

from app.core.config import settings
from app.core.audit_logger import audit_logger
from app.infrastructure.paypal_client import paypal_client
from app.infrastructure.state_store import state_store
from app.schemas.dto import (
    AgentChatCommandDTO,
    AutonomousPurchaseRequestDTO,
    BudgetPolicyDTO,
    CredentialsUpdateDTO,
)
from app.services.sentinel_agent import sentinel_agent

router = APIRouter(prefix="/api/v1", tags=["SentinelPay AI"])


@router.get("/dashboard")
async def get_dashboard(refresh_ai: bool = False) -> dict[str, Any]:
    """
    Returns the complete SentinelPay AI Command Center state:
    KPIs, audited PayPal subscriptions, AI executive brief, action proposals,
    budget guardrails, and cryptographic SHA-256 audit trail.
    """
    return await sentinel_agent.get_dashboard_overview(refresh_ai_brief=refresh_ai)


@router.post("/audit/run")
async def trigger_full_audit() -> dict[str, Any]:
    """Triggers a fresh AI & telemetry audit across all PayPal subscriptions."""
    audit_logger.record(
        stage="AGENT_REASONING",
        actor="SentinelAgentOrchestrator",
        summary="Full portfolio telemetry & PayPal billing audit triggered",
        details={"subscriptions_count": len(state_store.subscriptions)},
    )
    return await sentinel_agent.get_dashboard_overview(refresh_ai_brief=True)


@router.post("/subscriptions/{subscription_id}/remediate")
async def remediate_single_subscription(subscription_id: str) -> dict[str, Any]:
    """
    Executes the recommended PayPal Sandbox action (/cancel, /suspend, or /revise downgrade)
    for a specific subscription.
    """
    try:
        proposal = await sentinel_agent.execute_subscription_remediation(subscription_id)
        dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
        return {
            "executed_proposal": proposal.model_dump(),
            "dashboard": dashboard,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/subscriptions/{subscription_id}/auto-switch")
async def auto_switch_subscription(subscription_id: str) -> dict[str, Any]:
    """
    Executes 1-Click SaaS Arbitrage Auto-Switch: cancels the overpriced subscription
    and provisions the cheaper alternative via PayPal Orders API v2.
    """
    try:
        res = await sentinel_agent.execute_subscription_auto_switch(subscription_id)
        dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
        return {
            "switch_result": res,
            "dashboard": dashboard,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/subscriptions/{subscription_id}/negotiate")
async def negotiate_subscription_b2b(
    subscription_id: str,
    payload: dict[str, Any] | None = Body(default=None),
) -> dict[str, Any]:
    """
    Executes active AI-powered B2B retention negotiation with vendor.
    Generates an ultimatum letter referencing real telemetry & PayPal agreement,
    simulates vendor retention discount counter-offer, and optionally applies it via PayPal /revise.
    """
    try:
        apply_discount = bool((payload or {}).get("apply_discount", False))
        res = await sentinel_agent.execute_b2b_negotiation(
            subscription_id, apply_discount=apply_discount
        )
        dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
        return {
            "negotiation": res,
            "dashboard": dashboard,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/reports/cfo-boardpack")
async def get_cfo_boardpack() -> dict[str, Any]:
    """
    Generates the formal corporate CFO Audit Boardpack with before/after benchmarks,
    category distribution, and SHA-256 cryptographic verification ledger.
    """
    return await sentinel_agent.generate_cfo_boardpack()


@router.post("/paypal/webhook-simulate")
async def simulate_paypal_webhook_trap(
    payload: dict[str, Any] | None = Body(default=None),
) -> dict[str, Any]:
    """
    Simulates an incoming signed PayPal Webhook event (PAYMENT.SALE.COMPLETED)
    and triggers real-time Zero-Trust interception (/suspend + /v2/payments/captures/{id}/refund).
    """
    scenario = (payload or {}).get("scenario", "TRIAL_CONVERSION")
    res = await sentinel_agent.simulate_incoming_paypal_webhook_trap(scenario=scenario)
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
    return {
        "interception": res,
        "dashboard": dashboard,
    }


@router.post("/proposals/{proposal_id}/execute")
async def execute_or_approve_proposal(proposal_id: str) -> dict[str, Any]:
    """
    1-Click Human-in-the-Loop approval & execution endpoint for any pending
    subscription action or autonomous PayPal Order v2 purchase.
    """
    try:
        proposal = await sentinel_agent.execute_proposal_by_id(proposal_id)
        dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
        return {
            "executed_proposal": proposal.model_dump(),
            "dashboard": dashboard,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/agent/autonomous-sweep")
async def run_autonomous_sweep() -> dict[str, Any]:
    """
    Executes all flagged subscription remediations (Cancel zombies, Suspend price creep,
    Downgrade overprovisioned plans) in a single autonomous batch operation on PayPal Sandbox.
    """
    sweep_result = await sentinel_agent.execute_autonomous_sweep()
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=True)
    return {
        "sweep": sweep_result,
        "dashboard": dashboard,
    }


@router.post("/commerce/purchase")
async def create_autonomous_purchase(req: AutonomousPurchaseRequestDTO) -> dict[str, Any]:
    """
    Submits an Agentic Commerce purchase request through the BudgetGuardrailEngine:
    - Auto-executes via PayPal Orders API v2 (/v2/checkout/orders) if <= threshold.
    - Queues for 1-Click Approval if > threshold.
    - Rejects if exceeding monthly cap or outside whitelisted categories.
    """
    proposal = await sentinel_agent.process_autonomous_purchase(req)
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
    return {
        "proposal": proposal.model_dump(),
        "dashboard": dashboard,
    }


@router.post("/agent/chat")
async def chat_with_sentinel_agent(cmd: AgentChatCommandDTO) -> dict[str, Any]:
    """
    Natural-language interface to SentinelPay AI powered by Google Gemini.
    Can audit subscriptions, execute remediations, or initiate autonomous PayPal purchases.
    """
    result = await sentinel_agent.process_natural_language_command(cmd)
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
    return {
        "agent_response": result,
        "dashboard": dashboard,
    }


@router.put("/guardrails/policy")
async def update_guardrail_policy(policy: BudgetPolicyDTO) -> dict[str, Any]:
    """Updates the deterministic Budget Guardrail policy in real time."""
    updated = sentinel_agent.update_budget_policy(policy)
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
    return {
        "policy": updated.model_dump(),
        "dashboard": dashboard,
    }


@router.post("/paypal/seed-sandbox")
async def seed_paypal_sandbox() -> dict[str, Any]:
    """
    Seeds real Catalog Products (/v1/catalogs/products) and Billing Plans (/v1/billing/plans)
    into the connected PayPal Developer Sandbox account.
    """
    items = [s.model_dump() for s in state_store.subscriptions]
    seed_result = await paypal_client.seed_live_sandbox_billing_plans(items)
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=False)
    return {
        "seed_result": seed_result,
        "dashboard": dashboard,
    }


@router.post("/config/credentials")
async def update_runtime_credentials(creds: CredentialsUpdateDTO) -> dict[str, Any]:
    """
    Hot-reloads PayPal Sandbox (Client ID / Secret) and Google Gemini API Key
    without restarting the server, persisting them to .env.
    """
    try:
        settings.update_credentials(
            paypal_client_id=creds.paypal_client_id,
            paypal_client_secret=creds.paypal_client_secret,
            gemini_api_key=creds.gemini_api_key,
            gemini_model=creds.gemini_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    paypal_client.invalidate_token()
    status = await paypal_client.verify_connection()
    dashboard = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=True)
    return {
        "connection_status": status,
        "gemini_configured": settings.is_gemini_configured,
        "dashboard": dashboard,
    }


@router.post("/demo/reset")
async def reset_demo_environment() -> dict[str, Any]:
    """Resets subscriptions, budget counters, and audit trail for a clean demo take."""
    state_store.reset()
    audit_logger.clear()
    audit_logger.record(
        stage="AGENT_REASONING",
        actor="System",
        summary="SentinelPay AI Sandbox environment initialized and telemetry loaded",
        details={"subscriptions_loaded": len(state_store.subscriptions)},
    )
    return await sentinel_agent.get_dashboard_overview(refresh_ai_brief=True)
