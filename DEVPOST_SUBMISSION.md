# SentinelPay — Devpost Submission Package & < 3 Min Video Script

---

## 1. Quick Devpost Form Fields

- **Project Name:** SentinelPay
- **Elevator Pitch (max 200 chars):** Autonomous PayPal Treasury & Agentic Commerce platform that audits recurring SaaS waste, downgrades or cancels dormant subscriptions via PayPal APIs, and executes budget-guarded autonomous purchases.
- **Built With:** `paypal`, `google-gemini`, `python`, `fastapi`, `pydantic`, `react`, `typescript`, `tailwindcss`, `vite`

---

## 2. Full Devpost Project Description (Copy-Paste Ready)

### Inspiration
Organizations and individuals lose over **$135 billion annually** to "zombie" SaaS subscriptions, underutilized multi-seat licenses, duplicate productivity tools, and silent recurring price hikes. Traditional spend tools only send passive alerts—leaving finance teams to manually hunt down billing agreements.

At the same time, **Agentic Commerce** promises AI agents that can buy compute credits, renew infrastructure, and negotiate plans autonomously. Yet a critical barrier remains: **no CFO or consumer will hand an unconstrained LLM raw access to a PayPal account.**

We built **SentinelPay** to bridge that trust gap: combining **Google Gemini 2.5 Flash** financial intelligence with **deterministic, zero-trust Budget Guardrails** and deep **PayPal REST API execution**.

---

### What it does
**SentinelPay** is an autonomous treasury and procurement platform built natively on **PayPal Sandbox REST APIs**:

1. **Telemetry-Driven Subscription Audit:**
   - Correlates active PayPal recurring billing agreements (`I-...`) with product usage telemetry (active days in the last 30 days, seat utilization ratio, functional overlap, and 90-day price creep).
   - Computes a `0–100` **Waste Score**, **Cost-per-Active-Day**, and exact **Annual Recoverable Savings** (`$2,682.00/year` on our benchmark portfolio).

2. **Autonomous & 1-Click PayPal Subscription Remediation (`/v1/billing/subscriptions`):**
   - **Plan Downgrade via `/revise` (`POST /v1/billing/subscriptions/{id}/revise`):** Instead of blindly cancelling a needed tool, when SentinelPay detects that only `2 of 10 seats` are used on *DesignFlow Enterprise ($120/mo)*, it revises the PayPal Billing Plan down to the *Starter Duo Plan ($29/mo)*—saving **$1,092/year** with zero workflow disruption.
   - **Zombie Cancellation via `/cancel` (`POST /v1/billing/subscriptions/{id}/cancel`):** Terminates dormant services (*CloudGPU Studio Pro*, 52 days inactive, saving **$1,068/year**) and duplicate tools (*MeetScribe AI*, saving **$348/year**).
   - **Price-Creep Suspension via `/suspend` (`POST /v1/billing/subscriptions/{id}/suspend`):** Freezes recurring micro-subscriptions (*PulseMetrics*, +45% silent price hike with 0 usage) while preserving account state.

3. **Policy-Guarded Agentic Commerce (`POST /v2/checkout/orders`):**
   - Evaluates every autonomous purchase request against a deterministic **`BudgetGuardrailEngine`** before any PayPal API call can occur:
     - **Tier 1 — Auto-Approved Micro-Checkout (`<= $25.00`):** Immediately creates and captures a PayPal Order v2 (e.g., `$19.50` serverless GPU top-up) when within the monthly autonomous cap (`$150.00`) and inside whitelisted vendor categories.
     - **Tier 2 — 1-Click Human-in-the-Loop Approval (`> $25.00`):** Intercepts medium orders (e.g., `$65.00` production token pack) and places them in a **1-Click Approval Queue**. Once approved by the user, SentinelPay executes `POST /v2/checkout/orders` and returns the live PayPal Sandbox checkout link.
     - **Tier 3 — Hard Cap Rejection:** Immediately blocks orders that exceed the remaining monthly budget (e.g., `$450.00` dedicated cluster) or fall outside whitelisted categories.

4. **Tamper-Evident SHA-256 Audit Trail:**
   - Every AI reasoning step, guardrail evaluation, and PayPal Sandbox receipt (`PayPal-Request-Id`, HTTP status code, resource ID) is recorded in a **SHA-256 hash-chained ledger** (`prev_hash -> sha256_hash`).

---

### How we built it
We engineered SentinelPay using a strict **3-tier modular architecture**:

- **Presentation Layer (React 18 + TypeScript + Vite + Tailwind CSS):**
  - Designed in PayPal's institutional palette (`#003087` Deep Navy, `#0070BA` Cerulean Blue, `#F5F7FA` ledger canvas) with Apple-inspired fluid craft: translucent sticky header (`backdrop-filter: blur(20px)`), tabular financial numerals (`tabular-nums`), and instant `pointer-down` tactile response.
- **Domain & Business Layer (Python 3.13 + FastAPI + Pydantic v2):**
  - **`SubscriptionAuditEngine`:** Deterministic scoring model calculating waste scores and seat utilization efficiency.
  - **`BudgetGuardrailEngine`:** Zero-trust policy gatekeeper enforcing monthly caps, single-transaction auto-approval thresholds, and category whitelists.
  - **Strategy & Factory Design Patterns (`ActionStrategyFactory`):** Cleanly decouples `CancelSubscriptionStrategy`, `SuspendSubscriptionStrategy`, `DowngradePlanStrategy`, and `AutonomousOrderStrategy`.
- **Infrastructure Layer (PayPal Sandbox REST Client + Google Gemini 2.5 Flash):**
  - **`PayPalSandboxClient` (`httpx` Async):** Handles OAuth 2.0 Bearer token caching (`/v1/oauth2/token`), Catalog Products (`/v1/catalogs/products`), Billing Plans (`/v1/billing/plans`), Subscriptions (`/v1/billing/subscriptions`), and Checkout Orders v2 (`/v2/checkout/orders`).
  - **`GeminiReasoningProvider` (`gemini-2.5-flash`):** Generates structured JSON executive briefings and parses natural-language financial commands (in English or French) into typed tool executions, backed by a deterministic financial fallback engine for 100% reliability.

---

### Challenges we ran into
1. **Solving the "Empty PayPal Sandbox" Problem for Judges:**
   - A fresh PayPal Developer Sandbox account has no pre-existing recurring subscriptions or billing plans. To make live testing effortless, we built a **1-Click Live Sandbox Seeder** (`POST /api/v1/paypal/seed-sandbox`) that provisions real Catalog Products (`/v1/catalogs/products`) and Billing Plans (`/v1/billing/plans`) directly inside the connected PayPal Sandbox account, plus a seamless simulator fallback when keys are not yet entered.
2. **Preventing AI Hallucinations from Executing Unintended Payments:**
   - Relying solely on a system prompt to enforce spending limits is unsafe. We decoupled AI intent generation from execution by placing the deterministic `BudgetGuardrailEngine` in the critical path before `ActionStrategyFactory` can invoke `PayPalSandboxClient`.
3. **Intelligent Remediation vs. Blind Cancellation:**
   - Cancelling an active team tool breaks workflows. Implementing PayPal's `/v1/billing/subscriptions/{id}/revise` endpoint allowed SentinelPay to downgrade seat tiers automatically rather than terminating essential software.

---

### Accomplishments that we're proud of
- **End-to-End PayPal API Depth:** Going far beyond a simple checkout button by integrating **OAuth 2.0**, **Catalog Products v1**, **Billing Plans v1**, **Subscriptions v1 (`/cancel`, `/suspend`, `/revise`)**, and **Orders v2 (`/v2/checkout/orders`)**.
- **Zero-Latency Institutional UI:** Building a financial ledger interface that feels like a native PayPal enterprise product rather than a generic AI chat template.
- **Cryptographic Financial Compliance:** Delivering a verifiable SHA-256 hash chain linking every AI recommendation to its exact `PayPal-Request-Id`.

---

### What we learned
- Designing **Agentic Commerce** requires treating the AI as a *proposer* and deterministic code as the *custodian of funds*.
- PayPal's Subscriptions `/revise` API is a powerful, underutilized primitive for automated B2B SaaS seat optimization.

---

### What's next for SentinelPay
- **PayPal Webhooks Integration (`BILLING.SUBSCRIPTION.RENEWED`, `PAYMENT.SALE.COMPLETED`):** Real-time event-driven auditing the millisecond a recurring charge hits PayPal.
- **SSO & Identity Provider Sync (Okta / Google Workspace):** Automatically pulling real seat login logs to trigger PayPal `/revise` seat downgrades across enterprise teams.
- **Automated Vendor Retention Negotiation:** Dispatching structured counter-offers to merchants before executing a PayPal subscription cancellation.

---

## 3. Storyboard & Script Vidéo < 3 Minutes (Chronométré à 2 min 30 s)

> **Conseil de tournage pour viser le Top Cash Prize :**  
> Enregistre ton écran en `1920x1080` (zoom navigateur à `110%` sur `http://127.0.0.1:5173` pour que les chiffres et les reçus PayPal soient parfaitement lisibles). Pas besoin de longs slides théoriques : montre l'application dès les 5 premières secondes !

### Séquence 1 — Le Hook & Le Problème (0:00 – 0:25)
- **À l'écran :** Vue complète de **SentinelPay** (`http://127.0.0.1:5173`) avec la bannière bleue PayPal affichant **2 682,00 $US d'économies annuelles identifiées sur 4 abonnements**.
- **Action souris :** Survole la bannière principale puis descends légèrement sur la liste des 6 abonnements PayPal.
- **Voix-off (Anglais recommandé pour le jury international) :**
  > *"Every year, companies waste over 135 billion dollars on dormant SaaS subscriptions, unused team seats, and silent price hikes. Meanwhile, AI agents want to buy software autonomously—but no one trusts an unconstrained LLM with their PayPal account. Meet SentinelPay: autonomous PayPal subscription management and policy-guarded Agentic Commerce, powered by Google Gemini and PayPal Sandbox APIs."*

### Séquence 2 — Audit Télémétrique & Downgrade Intelligent `/revise` (0:25 – 1:10)
- **À l'écran :** Grand livre des abonnements récurrents PayPal (colonne de gauche).
- **Action souris :**
  1. Clique sur la ligne **DesignFlow Enterprise (120,00 $/mois)** pour déplier sa fiche télémétrique (`2 / 10 sièges utilisés`, économie de `1 092,00 $/an`).
  2. Clique sur le bouton bleu **« Passer au forfait Starter (29,00 $/mois) »**.
  3. Montre le reçu vert PayPal qui apparaît instantanément (`POST /v1/billing/subscriptions/I-9X821KLLQP9M/revise • HTTP 200`).
  4. Clique ensuite en haut sur le bouton blanc de la bannière : **« Optimiser les 3 abonnements »** pour nettoyer d'un seul coup les abonnements zombies restants (`/cancel` et `/suspend`).
- **Voix-off :**
  > *"SentinelPay correlates PayPal Billing Agreements with real usage telemetry. Look at DesignFlow Enterprise: we are paying 120 dollars a month for 10 seats, but only 2 seats are active. Instead of blindly cancelling a tool the team still uses, SentinelPay calls PayPal's Subscriptions Revise API to downgrade the plan to 29 dollars a month—saving 1,092 dollars a year in one click. And with our Autonomous Sweep, we can cancel dormant zombie SaaS and suspend silent price hikes across the entire portfolio, unlocking 2,682 dollars in verified annual savings."*

### Séquence 3 — Agentic Commerce & Les 3 Niveaux de Guardrails PayPal Orders v2 (1:10 – 2:00)
- **À l'écran :** Colonne de droite (**Contrôle budgétaire des achats autonomes** & **Achats autonomes PayPal Orders v2**).
- **Action souris :**
  1. Clique sur la carte **« 19,50 $ — Auto-validé »** (RunPod GPU Cloud). Montre la jauge budgétaire qui monte et le reçu PayPal Order v2 créé avec le **Lien Checkout Sandbox**.
  2. Clique sur la carte **« 65,00 $ — Approbation 1 clic »** (Anthropic Enterprise). Montre que l'encart **« En attente d'approbation en 1 clic »** s'ouvre en haut de la colonne de droite.
  3. Clique sur **« Approuver le paiement PayPal (65,00 $) »** pour valider l'ordre en 1 clic.
  4. Clique sur la carte **« 450,00 $ — Bloqué »** (AWS Dedicated Node) et montre le blocage immédiat dans le journal d'audit.
- **Voix-off :**
  > *"Now let's look at outbound Agentic Commerce using PayPal Orders v2. Every AI purchase request must pass through our deterministic Budget Guardrail Engine. First, a 19 dollar 50 GPU credit top-up is under our 25 dollar auto-approval threshold, so SentinelPay executes the PayPal Order automatically. Second, a 65 dollar token pack exceeds the threshold: our guardrail intercepts it and routes it to the 1-Click Human Approval queue. With one click, the user approves it and PayPal generates the live Sandbox order. Third, a 450 dollar server request exceeds our 150 dollar monthly cap and is deterministically blocked."*

### Séquence 4 — Commande Naturelle Gemini, Journal SHA-256 & Clôture (2:00 – 2:30)
- **À l'écran :** Barre **Instruction directe en langage naturel** en bas à gauche + **Journal d'audit PayPal & SHA-256** à droite + modale **Clés API**.
- **Action souris :**
  1. Tape dans la barre : `Achète 15$ de crédits GPU via PayPal` et clique sur **Exécuter**.
  2. Survole le **Journal d'audit PayPal & SHA-256** à droite pour montrer les empreintes cryptographiques `SHA256: ...`.
  3. Clique brièvement sur **Clés API** en haut à droite pour montrer l'intégration PayPal Sandbox & Gemini, puis referme.
- **Voix-off :**
  > *"Users can also instruct SentinelPay in natural language via Google Gemini, while every AI decision, guardrail check, and PayPal Request ID is recorded in a tamper-evident SHA-256 hash chain. SentinelPay turns PayPal into the trusted operating system for autonomous Agentic Commerce. Thank you!"*
