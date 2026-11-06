"""
SentinelPay AI — Model Context Protocol (MCP) Server for PayPal Agentic Commerce.
Standard: Model Context Protocol (MCP) JSON-RPC 2.0 stdio server.
Enables any autonomous LLM agent (Claude Desktop, Cursor, Gemini CLI, AutoGen, OpenAI Operator)
to safely audit, negotiate, and execute payments through PayPal Sandbox under deterministic Budget Guardrails.
"""

import asyncio
import json
import sys
from typing import Any

# Add parent path so imports work
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.sentinel_agent import sentinel_agent
from app.infrastructure.state_store import state_store
from app.schemas.dto import AutonomousPurchaseRequestDTO, BudgetPolicyDTO


TOOLS_DEFINITIONS = [
    {
        "name": "sentinel_audit_treasury",
        "description": "Audits active PayPal recurring subscriptions, identifies zombie SaaS, seat waste, price hikes, and computes annual recoverable savings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "refresh_ai": {
                    "type": "boolean",
                    "description": "Whether to regenerate executive analysis via Google Gemini",
                    "default": False
                }
            }
        }
    },
    {
        "name": "sentinel_guarded_purchase",
        "description": "Executes or queues an autonomous PayPal Order v2 purchase under deterministic Zero-Trust Budget Guardrails.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Target vendor name (e.g. RunPod, Anthropic)"},
                "item_name": {"type": "string", "description": "Service or compute pack being purchased"},
                "amount_usd": {"type": "number", "description": "Purchase amount in USD"},
                "category": {"type": "string", "description": "Spend category (must be in whitelisted categories)", "default": "Cloud & AI Compute"},
                "justification": {"type": "string", "description": "Business justification for this autonomous spend"}
            },
            "required": ["vendor_name", "item_name", "amount_usd", "justification"]
        }
    },
    {
        "name": "sentinel_remediate_subscription",
        "description": "Executes a PayPal Subscriptions API remediation (/cancel, /suspend, or /revise downgrade).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string", "description": "Subscription ID (e.g. SUB-DESIGNFLOW-02, SUB-CLOUDGPU-01)"}
            },
            "required": ["subscription_id"]
        }
    },
    {
        "name": "sentinel_auto_switch_arbitrage",
        "description": "Executes a 1-click atomic PayPal SaaS migration: cancels the overpriced subscription and purchases the cheaper replacement via PayPal Orders v2.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subscription_id": {"type": "string", "description": "Subscription ID to switch (e.g. SUB-CLOUDGPU-01, SUB-MEETSCRIBE-03)"}
            },
            "required": ["subscription_id"]
        }
    },
    {
        "name": "sentinel_simulate_webhook_trap",
        "description": "Simulates an incoming PayPal Webhook event (trial-to-paid conversion or stealth price hike) and triggers automatic interception and instant refund.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scenario": {
                    "type": "string",
                    "enum": ["TRIAL_CONVERSION", "PRICE_HIKE"],
                    "description": "The attack scenario to simulate",
                    "default": "TRIAL_CONVERSION"
                }
            }
        }
    }
]


async def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "sentinel_audit_treasury":
        data = await sentinel_agent.get_dashboard_overview(refresh_ai_brief=arguments.get("refresh_ai", False))
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "kpis": data["kpis"],
                        "subscriptions_count": len(data["subscriptions"]),
                        "flagged_count": data["kpis"]["flagged_subscriptions_count"],
                        "potential_annual_savings_usd": data["kpis"]["potential_annual_savings_usd"],
                        "realized_annual_savings_usd": data["kpis"]["realized_annual_savings_usd"],
                        "executive_summary": data["executive_ai_brief"].get("executive_summary", "")
                    }, indent=2)
                }
            ]
        }
    elif name == "sentinel_guarded_purchase":
        req = AutonomousPurchaseRequestDTO(
            vendor_name=arguments["vendor_name"],
            item_name=arguments["item_name"],
            amount_usd=float(arguments["amount_usd"]),
            category=arguments.get("category", "Cloud & AI Compute"),
            justification=arguments["justification"],
            auto_execute_if_allowed=True
        )
        proposal = await sentinel_agent.process_autonomous_purchase(req)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "proposal_id": proposal.proposal_id,
                        "approval_status": proposal.guardrail.approval_status,
                        "guardrail_reason": proposal.guardrail.reason,
                        "executed_on_paypal": proposal.paypal_receipt is not None,
                        "paypal_order_id": proposal.paypal_receipt.paypal_resource_id if proposal.paypal_receipt else None,
                        "approval_url": proposal.paypal_receipt.approval_url if proposal.paypal_receipt else None
                    }, indent=2)
                }
            ]
        }
    elif name == "sentinel_remediate_subscription":
        res = await sentinel_agent.execute_subscription_remediation(arguments["subscription_id"])
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "executed_proposal": res.model_dump()
                    }, indent=2)
                }
            ]
        }
    elif name == "sentinel_auto_switch_arbitrage":
        res = await sentinel_agent.execute_subscription_auto_switch(arguments["subscription_id"])
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res, indent=2)
                }
            ]
        }
    elif name == "sentinel_simulate_webhook_trap":
        res = await sentinel_agent.simulate_incoming_paypal_webhook_trap(arguments.get("scenario", "TRIAL_CONVERSION"))
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res, indent=2)
                }
            ]
        }
    else:
        raise ValueError(f"Unknown tool: {name}")


async def process_jsonrpc_request(req_line: str) -> str | None:
    try:
        req = json.loads(req_line)
    except Exception:
        return None

    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "sentinelpay-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
        return json.dumps(res)

    elif method == "tools/list":
        res = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS_DEFINITIONS
            }
        }
        return json.dumps(res)

    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            call_res = await handle_tool_call(name, arguments)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": call_res
            })
        except Exception as exc:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32000,
                    "message": str(exc)
                }
            })

    elif method == "ping":
        return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {}})

    return None


async def run_stdio_server():
    """Runs standard input/output loop for Model Context Protocol (MCP)."""
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line_bytes = await reader.readline()
        if not line_bytes:
            break
        line = line_bytes.decode("utf-8").strip()
        if not line:
            continue
        reply = await process_jsonrpc_request(line)
        if reply:
            sys.stdout.write(reply + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(run_stdio_server())
