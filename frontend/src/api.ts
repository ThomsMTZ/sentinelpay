import { B2BNegotiationResult, BudgetPolicy, CFOBoardpack, DashboardData } from './types';

const API_BASE = '/api/v1';

export async function fetchDashboard(refreshAi = false): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/dashboard?refresh_ai=${refreshAi}`);
  if (!res.ok) throw new Error('Impossible de charger les données du tableau de bord');
  return res.json();
}

export async function remediateSubscription(subscriptionId: string) {
  const res = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/remediate`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Échec de l’opération PayPal sur cet abonnement');
  return res.json();
}

export async function autoSwitchSubscription(subscriptionId: string) {
  const res = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/auto-switch`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Échec du remplacement automatique sur PayPal');
  return res.json();
}

export async function simulatePayPalWebhookTrap(
  scenario: 'TRIAL_CONVERSION' | 'PRICE_HIKE' = 'TRIAL_CONVERSION'
) {
  const res = await fetch(`${API_BASE}/paypal/webhook-simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario }),
  });
  if (!res.ok) throw new Error('Échec de la simulation du webhook PayPal');
  return res.json();
}

export async function executeProposal(proposalId: string) {
  const res = await fetch(`${API_BASE}/proposals/${proposalId}/execute`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Échec de l’exécution de la proposition');
  return res.json();
}

export async function runAutonomousSweep() {
  const res = await fetch(`${API_BASE}/agent/autonomous-sweep`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Échec de l’optimisation groupée');
  return res.json();
}

export async function submitAutonomousPurchase(payload: {
  vendor_name: string;
  item_name: string;
  category: string;
  amount_usd: number;
  justification: string;
  auto_execute_if_allowed: boolean;
}) {
  const res = await fetch(`${API_BASE}/commerce/purchase`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Échec de la création de l’ordre PayPal');
  return res.json();
}

export async function sendAgentCommand(prompt: string, autoExecute = false) {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, auto_execute_safe_actions: autoExecute }),
  });
  if (!res.ok) throw new Error('Échec de la requête');
  return res.json();
}

export async function updateBudgetPolicy(policy: BudgetPolicy) {
  const res = await fetch(`${API_BASE}/guardrails/policy`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(policy),
  });
  if (!res.ok) throw new Error('Impossible de mettre à jour le plafond budgétaire');
  return res.json();
}

export async function seedPayPalSandbox() {
  const res = await fetch(`${API_BASE}/paypal/seed-sandbox`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Échec du provisionnement PayPal Sandbox');
  return res.json();
}

export async function saveCredentials(creds: {
  paypal_client_id?: string;
  paypal_client_secret?: string;
  gemini_api_key?: string;
}) {
  const res = await fetch(`${API_BASE}/config/credentials`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(creds),
  });
  if (!res.ok) throw new Error('Impossible d’enregistrer les identifiants');
  return res.json();
}

export async function resetDemoEnvironment(): Promise<DashboardData> {
  const res = await fetch(`${API_BASE}/demo/reset`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Impossible de réinitialiser l’environnement');
  return res.json();
}

export async function negotiateSubscription(
  subscriptionId: string,
  applyDiscount = false
): Promise<{ negotiation: B2BNegotiationResult; dashboard: DashboardData }> {
  const res = await fetch(`${API_BASE}/subscriptions/${subscriptionId}/negotiate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apply_discount: applyDiscount }),
  });
  if (!res.ok) throw new Error('Échec de la négociation B2B');
  return res.json();
}

export async function fetchCFOBoardpack(): Promise<CFOBoardpack> {
  const res = await fetch(`${API_BASE}/reports/cfo-boardpack`);
  if (!res.ok) throw new Error('Impossible de générer le rapport CFO');
  return res.json();
}

