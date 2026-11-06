import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_and_initial_dashboard():
    # Reset demo state first
    reset_resp = client.post("/api/v1/demo/reset")
    assert reset_resp.status_code == 200

    resp = client.get("/api/v1/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    kpis = data["kpis"]
    assert kpis["active_subscriptions_count"] == 6
    assert kpis["flagged_subscriptions_count"] == 4
    # CloudGPU ($1068) + DesignFlow downgrade ($1092) + MeetScribe ($348) + PulseMetrics ($174) = $2682/yr
    assert kpis["potential_annual_savings_usd"] == 2682.0
    assert kpis["realized_annual_savings_usd"] == 0.0
    assert len(data["proposals"]) == 4


def test_autonomous_micro_purchase_auto_approved():
    client.post("/api/v1/demo/reset")
    resp = client.post(
        "/api/v1/commerce/purchase",
        json={
            "vendor_name": "RunPod GPU Cloud",
            "item_name": "Serverless Inference Credits",
            "category": "Cloud & AI Compute",
            "amount_usd": 19.50,
            "justification": "Auto-scaling inference burst under $25 threshold",
            "auto_execute_if_allowed": True,
        },
    )
    assert resp.status_code == 200
    payload = resp.json()
    proposal = payload["proposal"]

    assert proposal["guardrail"]["approval_status"] == "EXECUTED"
    assert proposal["paypal_receipt"] is not None
    assert proposal["paypal_receipt"]["endpoint"] == "/v2/checkout/orders"
    assert proposal["paypal_receipt"]["http_status"] in (200, 201)


def test_purchase_above_threshold_requires_1click_approval_then_executes():
    client.post("/api/v1/demo/reset")
    resp = client.post(
        "/api/v1/commerce/purchase",
        json={
            "vendor_name": "Anthropic Enterprise",
            "item_name": "Production Token Reserve Pack",
            "category": "Cloud & AI Compute",
            "amount_usd": 65.00,
            "justification": "Quarterly token replenishment (> $25 auto-approve limit)",
            "auto_execute_if_allowed": True,
        },
    )
    assert resp.status_code == 200
    proposal = resp.json()["proposal"]
    assert proposal["guardrail"]["approval_status"] == "PENDING_1CLICK_APPROVAL"
    assert proposal["paypal_receipt"] is None

    # Now trigger 1-Click Human Approval
    proposal_id = proposal["proposal_id"]
    exec_resp = client.post(f"/api/v1/proposals/{proposal_id}/execute")
    assert exec_resp.status_code == 200
    executed = exec_resp.json()["executed_proposal"]
    assert executed["guardrail"]["approval_status"] == "EXECUTED"
    assert executed["paypal_receipt"] is not None
    assert executed["paypal_receipt"]["endpoint"] == "/v2/checkout/orders"


def test_purchase_exceeding_monthly_cap_is_blocked():
    client.post("/api/v1/demo/reset")
    resp = client.post(
        "/api/v1/commerce/purchase",
        json={
            "vendor_name": "AWS Reserved Cluster",
            "item_name": "Dedicated H100 Node",
            "category": "Cloud & AI Compute",
            "amount_usd": 450.00,
            "justification": "Exceeds $150 monthly autonomous budget cap",
            "auto_execute_if_allowed": True,
        },
    )
    assert resp.status_code == 200
    proposal = resp.json()["proposal"]
    assert proposal["guardrail"]["passed"] is False
    assert proposal["guardrail"]["approval_status"] == "REJECTED_BY_GUARDRAIL"
    assert proposal["paypal_receipt"] is None


def test_autonomous_sweep_remediates_all_waste():
    client.post("/api/v1/demo/reset")
    sweep_resp = client.post("/api/v1/agent/autonomous-sweep")
    assert sweep_resp.status_code == 200
    data = sweep_resp.json()

    assert data["sweep"]["executed_count"] == 4
    assert data["sweep"]["annual_savings_unlocked_usd"] == 2682.0
    assert data["dashboard"]["kpis"]["realized_annual_savings_usd"] == 2682.0
    assert data["dashboard"]["kpis"]["potential_annual_savings_usd"] == 0.0
    # Verify cryptographic audit trail has SHA-256 chain
    trail = data["dashboard"]["audit_trail"]
    assert len(trail) >= 5
    assert len(trail[0]["sha256_hash"]) == 64


def test_natural_language_agent_chat():
    client.post("/api/v1/demo/reset")
    chat_resp = client.post(
        "/api/v1/agent/chat",
        json={
            "prompt": "Achète 15$ de crédits GPU via PayPal pour le serveur d'inférence",
            "auto_execute_safe_actions": True,
        },
    )
    assert chat_resp.status_code == 200
    body = chat_resp.json()
    assert body["agent_response"]["intent"] == "AUTONOMOUS_PURCHASE"
    assert body["agent_response"]["created_proposal"] is not None
    assert body["agent_response"]["created_proposal"]["guardrail"]["approval_status"] == "EXECUTED"


def test_revolut_price_delta_and_downgrade_flip():
    client.post("/api/v1/demo/reset")
    initial_resp = client.get("/api/v1/dashboard")
    assert initial_resp.status_code == 200
    subs = {s["id"]: s for s in initial_resp.json()["subscriptions"]}

    df_before = subs["SUB-DESIGNFLOW-02"]
    assert df_before["telemetry"]["price_change_pct_last_90d"] == 20.0
    assert df_before["telemetry"]["previous_monthly_cost"] == 100.0

    ms_before = subs["SUB-MEETSCRIBE-03"]
    assert ms_before["risk_category"] == "TRIAL_TRAP_CONVERSION"
    assert ms_before["waste_score"] == 94

    rem_resp = client.post("/api/v1/subscriptions/SUB-DESIGNFLOW-02/remediate")
    assert rem_resp.status_code == 200
    subs_after = {s["id"]: s for s in rem_resp.json()["dashboard"]["subscriptions"]}

    df_after = subs_after["SUB-DESIGNFLOW-02"]
    assert df_after["status"] == "DOWNGRADED"
    assert df_after["monthly_cost"] == 29.0
    assert df_after["telemetry"]["previous_monthly_cost"] == 120.0
    assert df_after["telemetry"]["price_change_pct_last_90d"] == -75.8
    assert df_after["telemetry"]["price_history_6m"][-1] == 29.0


def test_webhook_trap_interception_and_instant_refund():
    client.post("/api/v1/demo/reset")
    resp = client.post(
        "/api/v1/paypal/webhook-simulate",
        json={"scenario": "TRIAL_CONVERSION"},
    )
    assert resp.status_code == 200
    data = resp.json()
    interception = data["interception"]

    assert interception["webhook_event_type"] == "PAYMENT.SALE.COMPLETED"
    assert interception["transmission_sig"] == "SHA256withRSA-VERIFIED"
    assert interception["merchant"] == "VideoGen AI Studio"
    assert interception["intercepted_amount_usd"] == 49.0
    assert interception["annual_saved_usd"] == 588.0
    assert interception["suspend_receipt"]["endpoint"] == "/v1/billing/subscriptions/I-TRAP99812V/suspend"
    assert interception["refund_receipt"]["endpoint"] == "/v2/payments/captures/CAP-99812345X/refund"
    assert interception["refund_receipt"]["status_text"] == "REFUND_COMPLETED"
    assert data["dashboard"]["kpis"]["realized_annual_savings_usd"] == 588.0
    assert data["dashboard"]["proposals"][0]["action_type"] == "WEBHOOK_REFUND_INTERCEPT"


def test_1click_saas_auto_switch_arbitrage():
    client.post("/api/v1/demo/reset")
    resp = client.post("/api/v1/subscriptions/SUB-CLOUDGPU-01/auto-switch")
    assert resp.status_code == 200
    data = resp.json()
    switch_res = data["switch_result"]

    assert switch_res["annual_net_savings_usd"] == 840.0
    assert switch_res["cancel_receipt"]["endpoint"] == "/v1/billing/subscriptions/I-BW452GLLEP1G/cancel"
    assert switch_res["order_receipt"]["endpoint"] == "/v2/checkout/orders"
    sub = switch_res["subscription"]
    assert sub["status"] == "DOWNGRADED"
    assert sub["monthly_cost"] == 19.0
    assert "RunPod Serverless GPU" in sub["vendor_name"]
    assert data["dashboard"]["kpis"]["realized_annual_savings_usd"] == 840.0


def test_security_guardrail_spend_preservation_and_audit_chain_integrity():
    client.post("/api/v1/demo/reset")
    # Attempt to falsify current_month_autonomous_spend via PUT /guardrails/policy
    put_resp = client.put(
        "/api/v1/guardrails/policy",
        json={
            "monthly_autonomous_limit": 200.0,
            "current_month_autonomous_spend": 0.0,
            "auto_approve_threshold": 30.0,
            "require_1click_above_threshold": True,
            "allow_autonomous_cancellations": True,
            "allow_autonomous_downgrades": True,
            "whitelisted_categories": ["Cloud & AI Compute", "Developer Tools"],
        },
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["policy"]["current_month_autonomous_spend"] == 18.0
    assert put_resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert put_resp.headers.get("X-Frame-Options") == "DENY"

    dash = put_resp.json()["dashboard"]
    assert dash["system_status"]["audit_chain_verified"] is True
    assert dash["kpis"]["financial_health_score"] == 38
    assert dash["kpis"]["baseline_monthly_spend_usd"] == 301.50

    # Verify control-character sanitization in credentials endpoint
    bad_creds = client.post(
        "/api/v1/config/credentials",
        json={"paypal_client_id": "bad\nEXEC_INJECTION"},
    )
    assert bad_creds.status_code == 400


def test_b2b_negotiation_and_retention_discount():
    client.post("/api/v1/demo/reset")
    # Step 1: Draft ultimatum & check simulated counter offer
    resp = client.post(
        "/api/v1/subscriptions/SUB-DESIGNFLOW-02/negotiate",
        json={"apply_discount": False},
    )
    assert resp.status_code == 200
    neg = resp.json()["negotiation"]
    assert neg["vendor_name"] == "DesignFlow Enterprise"
    assert "To: enterprise-retention@designflowenterprise.com" in neg["ultimatum_letter"]
    assert neg["counter_offer"]["discount_percentage"] == 40.0
    assert neg["discount_applied_on_paypal"] is False

    # Step 2: Apply 40% retention discount via PayPal /revise
    resp2 = client.post(
        "/api/v1/subscriptions/SUB-DESIGNFLOW-02/negotiate",
        json={"apply_discount": True},
    )
    assert resp2.status_code == 200
    neg2 = resp2.json()["negotiation"]
    assert neg2["discount_applied_on_paypal"] is True
    assert neg2["paypal_receipt"]["endpoint"] == "/v1/billing/subscriptions/I-9X821KLLQP9M/revise"
    assert neg2["current_subscription"]["monthly_cost"] == 72.0
    assert resp2.json()["dashboard"]["kpis"]["realized_annual_savings_usd"] == 576.0


def test_cfo_boardpack_generation():
    client.post("/api/v1/demo/reset")
    resp = client.get("/api/v1/reports/cfo-boardpack")
    assert resp.status_code == 200
    boardpack = resp.json()
    assert "CFO-SENTINEL-" in boardpack["report_id"]
    assert boardpack["organization"] == "Enterprise FinOps & Treasury Division"
    assert boardpack["cryptographic_proof"]["chain_verified"] is True
    assert len(boardpack["subscriptions_matrix"]) == 6
    assert boardpack["cfo_signoff"]["status"] == "APPROVED_FOR_BOARD_PRESENTATION"


import json
import pytest
from app.mcp.server import process_jsonrpc_request


@pytest.mark.asyncio
async def test_mcp_server_protocol():
    # 1. Test initialize
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    init_res = json.loads(await process_jsonrpc_request(init_req))
    assert init_res["result"]["serverInfo"]["name"] == "sentinelpay-mcp-server"

    # 2. Test tools/list
    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    list_res = json.loads(await process_jsonrpc_request(list_req))
    tools = {t["name"] for t in list_res["result"]["tools"]}
    assert "sentinel_audit_treasury" in tools
    assert "sentinel_guarded_purchase" in tools
    assert "sentinel_remediate_subscription" in tools
    assert "sentinel_auto_switch_arbitrage" in tools
    assert "sentinel_simulate_webhook_trap" in tools
    assert "sentinel_negotiate_b2b" in tools
    assert "sentinel_generate_cfo_boardpack" in tools
    assert len(tools) == 7

    # 3. Test tools/call sentinel_audit_treasury
    call_req = json.dumps({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "sentinel_audit_treasury",
            "arguments": {"refresh_ai": False}
        }
    })
    call_res = json.loads(await process_jsonrpc_request(call_req))
    body = json.loads(call_res["result"]["content"][0]["text"])
    assert body["subscriptions_count"] == 6

    # 4. Test tools/call sentinel_generate_cfo_boardpack
    cfo_call = json.dumps({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "sentinel_generate_cfo_boardpack",
            "arguments": {}
        }
    })
    cfo_res = json.loads(await process_jsonrpc_request(cfo_call))
    cfo_body = json.loads(cfo_res["result"]["content"][0]["text"])
    assert "CFO-SENTINEL-" in cfo_body["report_id"]
    assert cfo_body["cryptographic_proof"]["chain_verified"] is True




