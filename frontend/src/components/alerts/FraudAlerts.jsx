import { infosStatut } from '../common/statutConfig.js'
import { CheckCircleIcon } from '../common/icons.jsx'

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
 * Bandeau d'alertes : transactions "suspect" ET "fraude", triees par
 * risque decroissant (fraude d'abord). Chaque ligne garde la couleur/
 * icone de son propre niveau (jamais tout en rouge) pour que l'operateur
 * distingue "a surveiller" de "a bloquer" au premier coup d'oeil.
 */
export default function FraudAlerts({ transactions }) {
  const ordreRisque = { fraude: 0, suspect: 1 }
  const alertes = transactions
    .filter((t) => t.niveau_risque === 'fraude' || t.niveau_risque === 'suspect')
    .sort((a, b) => ordreRisque[a.niveau_risque] - ordreRisque[b.niveau_risque])
    .slice(0, NB_ALERTES_MAX)

  const nbFraudes = alertes.filter((a) => a.niveau_risque === 'fraude').length
  const IconeEntete = infosStatut('fraude').Icon

  return (
    <div className="rounded-xl border border-status-critical/30 bg-status-critical/5 p-4">
      <div className="flex items-center gap-2">
        <IconeEntete size={18} className="text-status-critical" />
        <h3 className="text-sm font-medium text-primary">Alertes de risque</h3>
        {alertes.length > 0 && (
          <span className="rounded-full bg-status-critical/20 px-2 py-0.5 text-xs font-medium text-status-critical">
            {alertes.length}
          </span>
        )}
      </div>

      {alertes.length === 0 ? (
        <div className="mt-3 flex items-center gap-2 text-sm text-secondary">
          <CheckCircleIcon size={16} className="text-status-good" />
          Aucune transaction suspecte ou frauduleuse récemment.
        </div>
      ) : (
        <ul className="mt-3 space-y-2">
          {alertes.map((alerte) => {
            const { text, border, Icon } = infosStatut(alerte.niveau_risque)
            return (
              <li
                key={alerte.transaction_id}
                className={`flex items-center justify-between gap-3 rounded-lg border bg-surface px-3 py-2 text-sm ${border}`}
              >
                <div className="flex min-w-0 items-center gap-2">
                  <Icon size={14} className={`shrink-0 ${text}`} />
                  <div className="min-w-0">
                    <p className="truncate font-medium text-primary">{alerte.nom_titulaire}</p>
                    <p className="text-xs text-muted">
                      {alerte.pays_transaction} · {formaterDate(alerte.date_transaction)}
                    </p>
                  </div>
                </div>
                <div className="shrink-0 text-right">
                  <p className={`tabular font-semibold ${text}`}>
                    {alerte.montant.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}{' '}
                    {alerte.devise}
                  </p>
                  <p className="tabular text-xs text-muted">
                    {(alerte.probabilite * 100).toFixed(0)}% de risque
                  </p>
                </div>
              </li>
            )
          })}
        </ul>
      )}

      {alertes.length > 0 && (
        <p className="mt-3 text-xs text-muted">
          {nbFraudes} fraude{nbFraudes > 1 ? 's' : ''} · {alertes.length - nbFraudes} suspecte
          {alertes.length - nbFraudes > 1 ? 's' : ''}
        </p>
      )}
    </div>
  )
}
