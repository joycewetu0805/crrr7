import { infosStatut } from '../common/statutConfig.js'

/**
 * Pastille de statut : icone + libelle, jamais la couleur seule
 * (regle d'accessibilite de la charte data-viz du projet).
 */
export default function StatusBadge({ niveauRisque }) {
  const { label, text, bg, border, Icon } = infosStatut(niveauRisque)

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${text} ${bg} ${border}`}
    >
      <Icon size={13} />
      {label}
    </span>
  )
}
