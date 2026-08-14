import { STATUTS } from '../common/statutConfig.js'

/**
 * Part-a-tout : repartition des transactions analysees par niveau de
 * risque. Barre empilee horizontale (forme recommandee pour un
 * "part-to-whole" a 3 categories courtes) + legende, jamais un simple
 * camembert sans repere.
 */
export default function RepartitionRisque({ stats }) {
  if (!stats || stats.transactions_analysees === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-4">
        <h3 className="text-sm font-medium text-primary">Répartition par niveau de risque</h3>
        <p className="mt-6 text-center text-sm text-muted">Aucune transaction analysée.</p>
      </div>
    )
  }

  const legitimes =
    stats.transactions_analysees - stats.transactions_suspectes - stats.transactions_frauduleuses

  const segments = [
    { cle: 'legitime', valeur: legitimes },
    { cle: 'suspect', valeur: stats.transactions_suspectes },
    { cle: 'fraude', valeur: stats.transactions_frauduleuses },
  ]

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <h3 className="text-sm font-medium text-primary">Répartition par niveau de risque</h3>

      <div className="mt-5 flex h-6 gap-0.5 bg-page">
        {segments.map(({ cle, valeur }, index) => {
          if (valeur === 0) return null
          const pourcentage = (valeur / stats.transactions_analysees) * 100
          const estPremier = index === 0 || segments.slice(0, index).every((s) => s.valeur === 0)
          const estDernier = segments.slice(index + 1).every((s) => s.valeur === 0)
          return (
            <div
              key={cle}
              title={`${STATUTS[cle].label} : ${valeur} (${pourcentage.toFixed(1)}%)`}
              style={{
                width: `${pourcentage}%`,
                backgroundColor: STATUTS[cle].color,
              }}
              className={`${estPremier ? 'rounded-l-full' : ''} ${estDernier ? 'rounded-r-full' : ''}`}
            />
          )
        })}
      </div>

      <ul className="mt-4 flex flex-wrap gap-x-5 gap-y-2">
        {segments.map(({ cle, valeur }) => (
          <li key={cle} className="flex items-center gap-2 text-xs text-secondary">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: STATUTS[cle].color }}
            />
            {STATUTS[cle].label}
            <span className="tabular text-muted">
              {valeur} · {((valeur / stats.transactions_analysees) * 100).toFixed(1)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
