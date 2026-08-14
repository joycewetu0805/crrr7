/**
 * FRAUDSHIELD - Client API.
 *
 * Chemins relatifs ("/api/...") : en dev, Vite les redirige vers le
 * backend FastAPI (voir vite.config.js) ; en production, le frontend
 * est servi par le meme domaine que l'API (ou un reverse proxy), donc
 * aucune configuration d'URL n'est necessaire.
 */

async function requeteJSON(chemin, options) {
  const reponse = await fetch(chemin, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!reponse.ok) {
    const corps = await reponse.json().catch(() => null)
    const message = corps?.detail ?? `Erreur HTTP ${reponse.status}`
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message))
  }

  return reponse.json()
}

export function recupererStats() {
  return requeteJSON('/api/stats')
}

export function recupererTransactions(limite = 20) {
  return requeteJSON(`/api/transactions?limite=${limite}`)
}

export function recupererComptes() {
  return requeteJSON('/api/comptes')
}

export function analyserTransaction(transaction) {
  return requeteJSON('/api/predict', {
    method: 'POST',
    body: JSON.stringify(transaction),
  })
}
