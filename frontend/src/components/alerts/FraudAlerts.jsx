import { AlertOctagonIcon, CheckCircleIcon } from '../common/icons.jsx'

const NB_ALERTES_MAX = 5

function formaterDate(dateISO) {
  return new Date(dateISO).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Bandeau d'alertes : transactions classees "fraude", les plus recentes
 * d'abord. C'est la zone que le jury regarde en premier lors de la demo.
 */
export default function FraudAlerts({ transactions }) {
  const alertes = transactions
    .filter((t) => t.niveau_risque === 'fraude')
    .slice(0, NB_ALERTES_MAX)

  return (
    <div className="rounded-xl border border-status-critical/30 bg-status-critical/5 p-4">
      <div className="flex items-center gap-2">
        <AlertOctagonIcon size={18} className="text-status-critical" />
        <h3 className="text-sm font-medium text-primary">Alertes de fraude</h3>
        {alertes.length > 0 && (
          <span className="rounded-full bg-status-critical/20 px-2 py-0.5 text-xs font-medium text-status-critical">
            {alertes.length}
          </span>
        )}
      </div>

      {alertes.length === 0 ? (
        <div className="mt-3 flex items-center gap-2 text-sm text-secondary">
          <CheckCircleIcon size={16} className="text-status-good" />
          Aucune fraude détectée récemment.
        </div>
      ) : (
        <ul className="mt-3 space-y-2">
          {alertes.map((alerte) => (
            <li
              key={alerte.transaction_id}
              className="flex items-center justify-between gap-3 rounded-lg border border-status-critical/20 bg-surface px-3 py-2 text-sm"
            >
              <div className="min-w-0">
                <p className="truncate font-medium text-primary">{alerte.nom_titulaire}</p>
                <p className="text-xs text-muted">
                  {alerte.pays_transaction} · {formaterDate(alerte.date_transaction)}
                </p>
              </div>
              <div className="shrink-0 text-right">
                <p className="tabular font-semibold text-status-critical">
                  {alerte.montant.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}{' '}
                  {alerte.devise}
                </p>
                <p className="tabular text-xs text-muted">
                  {(alerte.probabilite * 100).toFixed(0)}% de risque
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
