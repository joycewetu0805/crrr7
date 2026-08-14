import {
  AlertOctagonIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  ListIcon,
  ShieldIcon,
} from '../common/icons.jsx'
import StatTile from './StatTile.jsx'

function formaterPourcentage(valeur) {
  return `${(valeur * 100).toFixed(1)}%`
}

/**
 * Les 6 indicateurs demandes pour le dashboard : total, analysees,
 * suspectes, frauduleuses, taux de fraude, score de risque moyen.
 */
export default function StatTilesRow({ stats }) {
  if (!stats) return null

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      <StatTile label="Transactions totales" value={stats.total_transactions} Icon={ListIcon} />
      <StatTile
        label="Analysées"
        value={stats.transactions_analysees}
        Icon={CheckCircleIcon}
        accentClass="text-status-good"
      />
      <StatTile
        label="Suspectes"
        value={stats.transactions_suspectes}
        Icon={AlertTriangleIcon}
        accentClass="text-status-warning"
      />
      <StatTile
        label="Frauduleuses"
        value={stats.transactions_frauduleuses}
        Icon={AlertOctagonIcon}
        accentClass="text-status-critical"
      />
      <StatTile
        label="Taux de fraude"
        value={formaterPourcentage(stats.taux_fraude)}
        Icon={ShieldIcon}
        accentClass={stats.taux_fraude > 0.1 ? 'text-status-critical' : 'text-primary'}
      />
      <StatTile
        label="Score de risque moyen"
        value={formaterPourcentage(stats.score_risque_moyen)}
        Icon={ShieldIcon}
        accentClass={stats.score_risque_moyen > 0.3 ? 'text-status-warning' : 'text-primary'}
      />
    </div>
  )
}
