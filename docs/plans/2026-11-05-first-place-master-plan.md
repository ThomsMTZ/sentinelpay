# SentinelPay — Master Plan 1ère Place (Security Zero-Trust, Clean Code, Webhook Trap Interceptor, Auto-Switch Arbitrage & UX Polish)

## Global Constraints
- Maintain 100% backward compatibility with all existing 7 pytest tests while adding new tests for the security hardening, SHA-256 chain integrity verification, Live PayPal Webhook Trap Interceptor (with automatic refund `/v2/payments/captures/{id}/refund`), and 1-Click SaaS Auto-Switch Arbitrage (`/cancel` + `/v2/checkout/orders`).
- Preserve the institutional PayPal + Apple + Revolut aesthetic (`#003087`, `#0070BA`, `#F5F7FA`, tabular numerals, zero AI-slop).

---

## Task 1 (Backend): Zero-Trust Security Hardening, Clean Code, Webhook Trap Interceptor & 1-Click SaaS Auto-Switch
- **Files:**
  - `backend/app/core/config.py`
  - `backend/app/core/audit_logger.py`
  - `backend/main.py`
  - `backend/app/schemas/dto.py`
  - `backend/app/infrastructure/paypal_client.py`
  - `backend/app/infrastructure/gemini_provider.py`
  - `backend/app/infrastructure/state_store.py`
  - `backend/app/domain/strategies.py`
  - `backend/app/services/sentinel_agent.py`
  - `backend/app/api/routes.py`
  - `backend/tests/test_sentinel_backend.py`

## Task 2 (Frontend): Apple Number Ticker, Health Score Before/After, 1:1 Sliders, Live Webhook Simulator, 1-Click Auto-Switch & PayPal JSON X-Ray
- **Files:**
  - `frontend/src/types.ts`
  - `frontend/src/api.ts`
  - `frontend/src/App.tsx`
