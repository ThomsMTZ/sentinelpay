import re

path = "frontend/src/App.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    # IDs
    (
        '<section className="rounded-2xl bg-[#003087] text-white p-6 sm:p-8 shadow-sm space-y-5">',
        '<section id="kpi-banner" className="rounded-2xl bg-[#003087] text-white p-6 sm:p-8 shadow-sm space-y-5">'
    ),
    (
        '<section className="bg-white border border-[#E2E8F0] rounded-2xl p-4 sm:p-5 shadow-[0_1px_2px_rgba(12,18,29,0.03)] space-y-3.5">',
        '<section id="webhook-firewall" className="bg-white border border-[#E2E8F0] rounded-2xl p-4 sm:p-5 shadow-[0_1px_2px_rgba(12,18,29,0.03)] space-y-3.5">'
    ),
    (
        '<div className="lg:col-span-7 space-y-5">',
        '<div id="subscriptions-ledger" className="lg:col-span-7 space-y-5">'
    ),
    (
        '<div className="lg:col-span-5 space-y-5">',
        '<div id="guardrails-panel" className="lg:col-span-5 space-y-5">'
    ),
    (
        '{showCFOModal && cfoBoardpack && (\n        <div className="fixed inset-0 z-50',
        '{showCFOModal && cfoBoardpack && (\n        <div id="cfo-modal" className="fixed inset-0 z-50'
    ),
    (
        '{negotiatingSub && (\n        <div className="fixed inset-0 z-50',
        '{negotiatingSub && (\n        <div id="b2b-modal" className="fixed inset-0 z-50'
    ),

    # KPI Banner
    ('Synthèse financière du portefeuille PayPal', 'PayPal Portfolio Financial Synthesis'),
    ('d’économies annuelles identifiées sur ${kpis.flagged_subscriptions_count} abonnements', 'annual savings identified across ${kpis.flagged_subscriptions_count} subscriptions'),
    ('Portefeuille optimisé : ${formatUSD(animatedRealizedSavings)} économisés cette année', 'Optimized Portfolio: ${formatUSD(animatedRealizedSavings)} saved this year'),
    ('Prélèvements mensuels actifs', 'Active Monthly Commitments'),
    (' / mois</span>', ' / mo</span>'),
    ('Économies déjà validées : {formatUSD(animatedRealizedSavings)}/an', 'Realized Savings: {formatUSD(animatedRealizedSavings)}/yr'),
    ('Exécution PayPal en cours…', 'Executing PayPal Sweep…'),
    ('Optimize ${kpis.flagged_subscriptions_count} abonnements (${formatUSD(\n                        animatedPotentialSavings\n                      )}/an)', 'Optimize ${kpis.flagged_subscriptions_count} Subscriptions (${formatUSD(animatedPotentialSavings)}/yr)'),
    ('Restaurer l’état initial de démo', 'Reset Demo State'),
    ('Score de santé financière PayPal', 'PayPal Financial Health Score'),
    ('Score de santé : {animatedHealthScore}/100', 'Health Score: {animatedHealthScore}/100'),
    ('Avant : <strong>{formatUSD(baselineMonthlySpend)}/mois</strong> → Maintenant :{\' \'}\n                <strong className="text-[#9AE6B4]">{formatUSD(animatedMonthlySpend)}/mois</strong>', 'Before: <strong>{formatUSD(baselineMonthlySpend)}/mo</strong> → Current:{\' \'}\n                <strong className="text-[#9AE6B4]">{formatUSD(animatedMonthlySpend)}/mo</strong>'),
    ('Gain net : +{formatUSD(animatedRealizedSavings)}/an', 'Net Gain: +{formatUSD(animatedRealizedSavings)}/yr'),

    # Webhook Firewall
    ('Pare-feu temps réel PayPal Webhooks', 'Real-Time PayPal Webhook Firewall'),
    ('Surveillance Zero-Trust active', 'Zero-Trust Monitoring Active'),
    ('Intercepte les conversions d’essais gratuits et hausses furtives dès réception du\n                  webhook signé PayPal, suspend l’accord et déclenche le remboursement instantané.', 'Intercepts free trial traps and stealth price hikes upon receiving cryptographically signed PayPal webhooks, suspends the billing agreement, and triggers instant capture refund.'),
    ('Simuler piège fin d’essai 1 $ → 49 $', 'Simulate Trial Trap $1 → $49'),
    ('Simuler hausse furtive +169 % (39 $)', 'Simulate Stealth Hike +169% ($39)'),
    ('Interception Webhook…', 'Intercepting Webhook…'),
    ('Remboursement PayPal exécuté : +\n                    {formatUSD(webhookInterception.intercepted_amount_usd)} recrédités •{\' \'}\n                    {formatUSD(webhookInterception.annual_saved_usd)}/an sauvés', 'Instant PayPal Refund Executed: +\n                    {formatUSD(webhookInterception.intercepted_amount_usd)} refunded •{\' \'}\n                    {formatUSD(webhookInterception.annual_saved_usd)}/yr saved'),
    ('1. Suspension immédiate de l’accord PayPal', '1. Immediate PayPal Agreement Suspension (/suspend)'),
    ('2. Remboursement automatique de la capture ({webhookInterception.descriptor})', '2. Automated Capture Refund ({webhookInterception.descriptor})'),
    ('→ Réf.{\' \'}\n                    {webhookInterception.refund_receipt.paypal_resource_id}', '→ Ref.{\' \'}\n                    {webhookInterception.refund_receipt.paypal_resource_id}'),

    # Subscriptions Ledger
    ('Subscriptions récurrents PayPal', 'PayPal Recurring Subscriptions'),
    ('Cliquez sur une ligne pour inspecter la télémétrie, l’arbitrage IA et le reçu\n                    PayPal', 'Click any row to inspect telemetry, AI arbitrage, and cryptographic PayPal receipts'),
    ('Tous ({subscriptions.length})', 'All ({subscriptions.length})'),
    ('À optimiser ({kpis.flagged_subscriptions_count})', 'Actionable ({kpis.flagged_subscriptions_count})'),
    ('Traités ({subscriptions.filter((s) => s.status !== \'ACTIVE\').length})', 'Optimized ({subscriptions.filter((s) => s.status !== \'ACTIVE\').length})'),
    ('{sub.plan_name} • Accord PayPal{\' \'}\n                              <code className="font-mono text-[11px] text-[#4A5568]">\n                                {sub.paypal_subscription_id}\n                              </code>', '{sub.plan_name} • PayPal Agreement{\' \'}\n                              <code className="font-mono text-[11px] text-[#4A5568]">\n                                {sub.paypal_subscription_id}\n                              </code>'),
    ('<span className="text-xs font-normal text-[#718096]">/mois</span>', '<span className="text-xs font-normal text-[#718096]">/mo</span>'),
    ('Économie : {formatUSD(sub.estimated_annual_savings)}/an', 'Savings: {formatUSD(sub.estimated_annual_savings)}/yr'),
    ('Jours actifs (30 j)', 'Active Days (30d)'),
    ('{sub.telemetry.active_days_last_30d} / 30 days ago', '{sub.telemetry.active_days_last_30d} / 30 days'),
    ('Sièges utilisés', 'Active Seats'),
    ('{sub.telemetry.active_seats} / {sub.telemetry.provisioned_seats}{\' \'}\n                                siège(s)', '{sub.telemetry.active_seats} / {sub.telemetry.provisioned_seats}{\' \'}\n                                seat(s)'),
    ('Coût par jour actif', 'Cost per Active Day'),
    ('Score d’inactivité', 'Waste Score'),
    ('Ancien tarif : {formatUSD(sub.telemetry.previous_monthly_cost)}{\' \'}\n                                      → Tarif actuel : {formatUSD(sub.monthly_cost)}', 'Previous Rate: {formatUSD(sub.telemetry.previous_monthly_cost)}{\' \'}\n                                      → Current Rate: {formatUSD(sub.monthly_cost)}'),
    ('Relevé : {sub.telemetry.raw_paypal_descriptor} • Historique 6m :{\' \'}\n                                    {sub.telemetry.price_history_6m\n                                      .map((p) => formatUSD(p))\n                                      .join(\' → \')}', 'Descriptor: {sub.telemetry.raw_paypal_descriptor} • 6-Month Trend:{\' \'}\n                                    {sub.telemetry.price_history_6m\n                                      .map((p) => formatUSD(p))\n                                      .join(\' → \')}'),
    ('Verrouillage données / contrat actif (Suspension /suspend\n                                    privilégiée)', 'Data Retention / Contract Lock Active (/suspend preferred)'),
    ('Aucun verrouillage de données (Résiliation directe sûre)', 'No Data Lock (Safe Direct /cancel)'),
    ('Diagnostic d’utilisation', 'Usage Telemetry & Rationale'),
    ('Appel API PayPal…', 'Calling PayPal API…'),
    ('{formatUSD(sub.switch_alternative.annual_net_savings)}/an', '{formatUSD(sub.switch_alternative.annual_net_savings)}/yr'),
    (')}/mois)`}', ')}/mo)`}'),
    ('Générer une mise en demeure formelle sur la télémétrie réelle et obtenir -40% de remise entreprise via l\'API PayPal /revise.', 'Generate formal legal notice based on verified telemetry and obtain a 40% enterprise discount via PayPal /revise.'),
    ('SentinelPay AI audite la télémétrie et rédige la mise en demeure formelle…', 'SentinelPay AI is auditing telemetry and generating formal legal notice…'),
    ('Appliquer -40% sur PayPal', 'Apply 40% Discount on PayPal via /revise'),
    ('Ex. « Achète 18 $ de crédits GPU via PayPal » ou « Résilie les abonnements\n                  inactifs »', 'E.g., "Buy $18 in GPU credits via PayPal" or "Cancel idle SaaS subscriptions"'),
    ('Saisissez une instruction d’audit ou d’achat PayPal…', 'Enter an autonomous treasury instruction or purchase order…'),
    ('<span>{commandBusy ? \'Analyse…\' : \'Exécuter\'}</span>', '<span>{commandBusy ? \'Analyzing…\' : \'Execute\'}</span>'),

    # Guardrails Column
    ('En attente d’approbation en 1 clic ({pendingApprovals.length})', 'Pending 1-Click Approvals ({pendingApprovals.length})'),
    ('Validation requise', 'Action Required'),
    ('Création de l’ordre PayPal v2…', 'Creating PayPal Order v2…'),
    ('Utilisé ce mois :{\' \'}\n                    <strong className="text-[#0C121D] tabular-figure">\n                      {formatUSD(kpis.autonomous_budget_spent_usd)}\n                    </strong>', 'Spent this month:{\' \'}\n                    <strong className="text-[#0C121D] tabular-figure">\n                      {formatUSD(kpis.autonomous_budget_spent_usd)}\n                    </strong>'),
    ('Plafond : {formatUSD(monthlyLimit)}', 'Monthly Cap: {formatUSD(monthlyLimit)}'),
    ('Disponible : {formatUSD(liveRemainingBudget)}', 'Remaining: {formatUSD(liveRemainingBudget)}'),
    ('Auto-validation ≤ {formatUSD(autoThreshold)}', 'Auto-Approve ≤ {formatUSD(autoThreshold)}'),
    ('Plafond mensuel ({formatUSD(monthlyLimit)})', 'Monthly Cap ({formatUSD(monthlyLimit)})'),
    ('Seuil sans clic ({formatUSD(autoThreshold)})', 'Zero-Click Threshold ({formatUSD(autoThreshold)})'),
    ('Testez les 3 niveaux de règles budgétaires sur l’endpoint{\' \'}\n                  <code className="font-mono text-[11px]">/v2/checkout/orders</code>', 'Test the 3 policy tiers against the live endpoint{\' \'}\n                  <code className="font-mono text-[11px]">/v2/checkout/orders</code>'),
    ('Recharge crédits API', 'API Credit Top-up'),
    ('Ordre test (${formatUSD(19.5)}) face au seuil ${formatUSD(autoThreshold)}', 'Test order (${formatUSD(19.5)}) vs auto-approval threshold ${formatUSD(autoThreshold)}'),
    ('Pack Tokens Production', 'Production Token Pack'),
    ('Ordre test (${formatUSD(65.0)}) face au seuil ${formatUSD(autoThreshold)}', 'Test order (${formatUSD(65.0)}) vs threshold ${formatUSD(autoThreshold)} (approval required)'),
    ('Instance H100 Mensuelle', 'Dedicated H100 Instance'),
    ('Ordre test (${formatUSD(450.0)}) face au plafond ${formatUSD(monthlyLimit)}', 'Test order (${formatUSD(450.0)}) vs monthly budget limit ${formatUSD(monthlyLimit)} (blocked)'),
    ('Personnaliser un ordre d’achat…', 'Customize purchase order…'),
    ('placeholder="Fournisseur"', 'placeholder="Vendor"'),
    ('placeholder="Service / Ressource"', 'placeholder="Service / Resource"'),
    ('Catégorie non autorisée (Test blocage)', 'Restricted Category (Policy Violation Test)'),
    ('>Commander<', '>Create Order<'),

    # Audit Trail & CFO
    ('Journal d’audit PayPal & SHA-256', 'PayPal Audit Trail & SHA-256 Ledger'),
    ('{audit_trail.length} événements', '{audit_trail.length} events'),
    ('Audit actif', 'Audit Active'),
    ('-{formatUSD(prop.annual_savings_usd)}/an', '-{formatUSD(prop.annual_savings_usd)}/yr'),
    ('Lien Checkout Sandbox', 'Sandbox Checkout Link'),
    ('{formatUSD(cfoBoardpack.kpi_summary.baseline_annual_spend_usd)}/an', '{formatUSD(cfoBoardpack.kpi_summary.baseline_annual_spend_usd)}/yr'),
    ('{formatUSD(cfoBoardpack.kpi_summary.current_annual_spend_usd)}/an', '{formatUSD(cfoBoardpack.kpi_summary.current_annual_spend_usd)}/yr'),
    ('{formatUSD(cfoBoardpack.kpi_summary.realized_annual_savings_usd)}/an', '{formatUSD(cfoBoardpack.kpi_summary.realized_annual_savings_usd)}/yr'),
    ('Matrice des Subscriptions PayPal', 'PayPal Subscriptions Matrix'),
    ('+{formatUSD(row.annual_savings)}/an', '+{formatUSD(row.annual_savings)}/yr'),
    ('/mois)', '/mo)'),
]

count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
    else:
        print(f"NOT FOUND: {old[:50]}...")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully applied {count}/{len(replacements)} replacements.")
