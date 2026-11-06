# Revolut Price Ticker & PayPal Anti-Trap AI Intelligence Plan

## Global Constraints
- Preserve all existing endpoints and test cases while adding the 4 new PayPal/Revolut capabilities:
  1. Revolut-style Price Delta (`price_change_pct_last_90d`), previous monthly cost (`previous_monthly_cost`), and 6-month price history (`price_history_6m: list[float]`).
  2. Cryptic PayPal Merchant Descriptor decoding (`raw_paypal_descriptor: str`).
  3. Trial-to-Paid Conversion Shield (`is_trial_converting: bool`, `trial_days_remaining: int | None`, `RiskCategory.TRIAL_TRAP_CONVERSION`).
  4. Data-retention / Contract-lock awareness (`has_data_retention_or_contract_lock: bool`) so the AI chooses `/suspend` or `/revise` instead of destructive `/cancel` when appropriate, and dynamically flips `price_change_pct_last_90d` from positive (Red) to negative (Green) upon executing a PayPal `/revise` plan downgrade.

---

## Task 1: Backend DTOs, Portfolio Telemetry, Multi-Criteria AI Audit Engine & Dynamic Downgrade Price Flip
- **Files:**
  - `backend/app/schemas/dto.py`
  - `backend/app/infrastructure/state_store.py`
  - `backend/app/domain/audit_engine.py`
  - `backend/app/domain/strategies.py`
  - `backend/app/infrastructure/gemini_provider.py`
  - `backend/tests/test_sentinel_backend.py`
- **Requirements:**
  1. In `backend/app/schemas/dto.py`:
     - Add `TRIAL_TRAP_CONVERSION = "TRIAL_TRAP_CONVERSION"` to `RiskCategory`.
     - Extend `UsageTelemetryDTO` with:
       - `previous_monthly_cost: float = 0.0`
       - `price_history_6m: list[float] = Field(default_factory=list)`
       - `raw_paypal_descriptor: str = ""`
       - `is_trial_converting: bool = False`
       - `trial_days_remaining: int | None = None`
       - `has_data_retention_or_contract_lock: bool = False`
  2. In `backend/app/infrastructure/state_store.py`:
     - Populate all 6 subscriptions in `build_initial_subscriptions()` with realistic `previous_monthly_cost`, `price_change_pct_last_90d`, `price_history_6m` (6 floats), `raw_paypal_descriptor`, trial conversion flags, and contract lock flags:
       - `SUB-CLOUDGPU-01` (`CloudGPU Studio Pro`, `$89.00`): `previous_monthly_cost=75.00`, `price_change_pct_last_90d=18.7`, `price_history_6m=[75.0, 75.0, 75.0, 82.0, 89.0, 89.0]`, `raw_paypal_descriptor="PP*FASTSPRG-CGPU88"`.
       - `SUB-DESIGNFLOW-02` (`DesignFlow Enterprise`, `$120.00`): `previous_monthly_cost=100.00`, `price_change_pct_last_90d=20.0`, `price_history_6m=[100.0, 100.0, 100.0, 100.0, 120.0, 120.0]`, `raw_paypal_descriptor="PP*DSGNFLW-ENT10"`, `has_data_retention_or_contract_lock=True`.
       - `SUB-MEETSCRIBE-03` (`MeetScribe AI NoteTaker`, `$29.00`): `previous_monthly_cost=1.00`, `price_change_pct_last_90d=2800.0`, `price_history_6m=[0.0, 0.0, 0.0, 0.0, 1.0, 29.0]`, `raw_paypal_descriptor="PP*PADDLE-MSCRB"`, `is_trial_converting=True`, `trial_days_remaining=2`.
       - `SUB-PULSEMETRICS-04` (`PulseMetrics Micro-Alerts`, `$14.50`): `previous_monthly_cost=10.00`, `price_change_pct_last_90d=45.0`, `price_history_6m=[10.0, 10.0, 10.0, 12.0, 14.5, 14.5]`, `raw_paypal_descriptor="PP*PLSMTRCS-BILL"`, `has_data_retention_or_contract_lock=True`.
       - `SUB-COPILOT-05` (`GitHub Copilot Business`, `$19.00`): `previous_monthly_cost=22.00`, `price_change_pct_last_90d=-13.6`, `price_history_6m=[22.0, 22.0, 22.0, 19.0, 19.0, 19.0]`, `raw_paypal_descriptor="PP*GITHUB-CPLT"`.
       - `SUB-VERCEL-06` (`Vercel Pro Cloud`, `$20.00`): `previous_monthly_cost=20.00`, `price_change_pct_last_90d=0.0`, `price_history_6m=[20.0, 20.0, 20.0, 20.0, 20.0, 20.0]`, `raw_paypal_descriptor="PP*VERCEL-INC"`.
  3. In `backend/app/domain/audit_engine.py`:
     - Factor in `is_trial_converting` (sets `RiskCategory.TRIAL_TRAP_CONVERSION`, `recommended_action = ActionType.CANCEL_SUBSCRIPTION`, `waste_score = 94`, and mentions the `$1.00 -> $29.00` trial conversion in `trial_days_remaining` days + decoded descriptor in `ai_audit_rationale`).
     - Factor in `has_data_retention_or_contract_lock` and `price_change_pct_last_90d` in rationale explanations.
     - Ensure total `potential_annual_savings_usd` across the 4 flagged subscriptions remains `$2682.0`.
  4. In `backend/app/domain/strategies.py`:
     - In `DowngradePlanStrategy.execute()`, when a subscription is downgraded (e.g. `$120.00 -> $29.00`), update `sub.telemetry.previous_monthly_cost = old_cost`, `sub.telemetry.price_change_pct_last_90d = round(((new_cost - old_cost) / old_cost) * 100, 1)` (e.g. `-75.8`), and append `new_cost` to `sub.telemetry.price_history_6m` (keeping 6 items) so the UI badge flips from Red (`+20%`) to Green (`-75.8%`)!
  5. Add unit test `test_revolut_price_delta_and_downgrade_flip` in `backend/tests/test_sentinel_backend.py` and verify all tests pass.

---

## Task 2: Frontend Revolut Stock-Style Price Overlay, SVG Sparkline, Descriptor Decoder & Trial Shield
- **Files:**
  - `frontend/src/types.ts`
  - `frontend/src/App.tsx`
- **Requirements:**
  1. Update `RiskCategory` and `UsageTelemetry` in `frontend/src/types.ts` to match the new backend fields.
  2. In `frontend/src/App.tsx`:
     - Create a clean `SparklineSVG` helper component that renders a crisp 6-point SVG polyline (`width=56, height=20`) colored `#C53030` (Red) when price trend > 0, `#0E7C47` (Green) when price trend < 0, and `#94A3B8` (Slate) when 0%.
     - Next to each subscription's monthly price on the main row, display:
       - The **Revolut Price Delta Pill** (`▲ +45,0 %`, `▲ +20,0 %`, `▼ -13,6 %`, `▼ -75,8 %`) with a red tint (`bg-[#FFF0F0] text-[#C53030] border-[#C53030]/20`) for price increases and a green tint (`bg-[#EAF7F0] text-[#0E7C47] border-[#0E7C47]/20`) for price decreases.
       - The **strikethrough previous price** (`100,00 $` crossed out next to `120,00 $/mois`, or `120,00 $` crossed out next to `29,00 $/mois` after downgrade).
       - The **6-month Sparkline SVG** right beside the price block.
       - Subtle left border accent (`border-l-4 border-l-[#C53030]` on active subscriptions with recent price hikes or trial traps, `border-l-4 border-l-[#0E7C47]` on subscriptions with price drops/downgrades).
     - Show the decoded **PayPal Raw Descriptor** (`Relevé PayPal : PP*FASTSPRG-CGPU88 → CloudGPU Studio Pro`) and the **Trial Trap Shield badge** (`Essai 1 $ → 29 $/mois dans 2 j`).
     - Run `npm run build` in `frontend/` to verify zero TypeScript or build errors.
