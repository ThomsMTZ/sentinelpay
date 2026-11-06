# SentinelPay — Autonomous Subscription Audit & Agentic Commerce for PayPal

> **PayPal AI Hackathon 2026 Submission**  
> Built with **PayPal Developer Sandbox REST APIs** (`Subscriptions v1`, `Catalogs v1`, `Orders v2`), **Google Gemini 2.5 Flash**, **FastAPI**, and **React + Tailwind CSS**.

---

## What SentinelPay Does

Companies and consumers lose thousands of dollars every year to dormant "zombie" SaaS subscriptions, over-provisioned team seats, duplicate tools, and silent recurring price hikes. At the same time, giving an AI agent direct access to a payment method without deterministic controls is a security risk.

**SentinelPay** solves both problems by pairing **PayPal Recurring Billing & Checkout APIs** with a **Zero-Trust Budget Guardrail Engine**:

1. **Telemetry-Driven Subscription Audit:** Continuously correlates PayPal Billing Agreements (`I-...`) with usage telemetry (active days, seat utilization, overlapping tools, 90-day price creep) to compute a `0–100` Waste Score and Cost-per-Active-Day.
2. **1-Click & Autonomous PayPal Remediation:**
   - **Cancel Dormant Subscriptions:** Calls `POST /v1/billing/subscriptions/{id}/cancel` for zombie SaaS tools.
   - **Downgrade Over-Provisioned Plans:** Calls `POST /v1/billing/subscriptions/{id}/revise` to switch an underutilized 10-seat enterprise plan (`$120/mo`) down to a 2-seat starter plan (`$29/mo`), saving `$1,092/yr` without losing service.
   - **Suspend Price-Creep Micro-Charges:** Calls `POST /v1/billing/subscriptions/{id}/suspend` when silent price hikes occur with zero usage.
3. **Policy-Guarded Agentic Commerce (`/v2/checkout/orders`):**
   - **Auto-Approved Micro-Orders (`<= $25`):** Immediately creates and captures a PayPal Order v2 when within the monthly autonomous budget cap (`$150/mo`) and inside whitelisted categories.
   - **1-Click Human-in-the-Loop Approval (`> $25`):** Intercepts medium purchases (`e.g., $65`) and places them in a 1-Click Approval Queue before calling PayPal.
   - **Hard Budget Cap Enforcement:** Automatically blocks any purchase exceeding the remaining monthly budget (`e.g., $450`).
4. **Cryptographic SHA-256 Audit Ledger:** Every AI thought, guardrail check, and PayPal Sandbox API receipt (`PayPal-Request-Id`, HTTP status, resource ID) is hash-chained (`prev_hash -> sha256_hash`) for tamper-evident financial compliance.
5. **1-Click SaaS Arbitrage Auto-Switch:** Atomic cancellation of overpriced services (`/cancel`) and immediate procurement of equivalent cheaper alternatives via PayPal Orders v2.
6. **Live PayPal Webhook Trap Interceptor:** Real-time defense against silent price hikes (+169%) and unauthorized trial conversions with instant refunds via PayPal Captures Refund API v2 (`/v2/payments/captures/{id}/refund`).
7. **Active B2B Retention Negotiation & CFO Boardpack:** Automated ultimatum notices citing telemetry to secure 40% enterprise discounts via PayPal `/revise`, plus certified boardpacks for executive leadership.
8. **Model Context Protocol (MCP) Server (`mcp_server.py`):** Standard JSON-RPC 2.0 stdio server enabling external AI agents (Claude Desktop, Cursor, OpenAI Agents) to inspect and command PayPal under zero-trust budget guardrails.

---

## Architecture

```text
Hackathon/
├── backend/
│   ├── main.py                        # FastAPI Entrypoint & Lifespan
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py              # Hot-reloadable PayPal & Gemini credentials
│   │   │   └── audit_logger.py        # Observer Pattern: SHA-256 Hash-Chained Ledger
│   │   ├── schemas/
│   │   │   └── dto.py                 # Pydantic v2 Data Transfer Objects
│   │   ├── infrastructure/
│   │   │   ├── paypal_client.py       # PayPal Sandbox REST Client (OAuth2, Subscriptions v1, Orders v2)
│   │   │   ├── gemini_provider.py     # Google Gemini 2.5 Flash Adapter + Deterministic Fallback
│   │   │   └── state_store.py         # Portfolio State & 1-Click Demo Reset
│   │   ├── domain/
│   │   │   ├── audit_engine.py        # Waste Score & ROI Calculation Engine
│   │   │   ├── guardrail_engine.py    # Zero-Trust Budget Policy Gatekeeper
│   │   │   └── strategies.py          # Strategy Pattern for PayPal Executions
│   │   ├── services/
│   │   │   └── sentinel_agent.py      # Agentic Commerce Orchestrator
│   │   └── api/
│   │       └── routes.py              # REST API Endpoints
│   └── tests/
│       └── test_sentinel_backend.py   # Automated Pytest Suite (12/12 passing)
└── frontend/
    └── src/
        ├── App.tsx                    # PayPal Institutional UI with Apple Fluid Craft
        ├── api.ts                     # Typed REST Client
        ├── types.ts                   # Shared TypeScript Interfaces
        └── index.css                  # Optical Typography, Tabular Figures & Pressable Physics
```

---

## Quick Start (1 Minute)

### 1. Configure Credentials (Optional at boot — Hot-Reload Supported)
Copy `.env.example` to `.env` and paste your PayPal Developer Sandbox & Gemini keys (or enter them live in the UI via the **Clés API** button):

```env
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_secret
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Start Backend (FastAPI on port `8000`)
```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 3. Start Frontend (Vite + React on port `5173`)
```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Run Automated Tests
```powershell
python -m pytest backend/tests/test_sentinel_backend.py -v
```
