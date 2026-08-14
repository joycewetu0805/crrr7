import { AlertOctagonIcon, AlertTriangleIcon, CheckCircleIcon } from './icons.jsx'

/**
 * Source unique de verite pour l'affichage des 3 niveaux de risque.
 * Utilisee par le badge, le tableau, les graphiques et les alertes :
 * un statut = toujours la meme couleur, la meme icone, le meme libelle.
 * (Couleurs reservees "status", voir la charte data-viz du projet.)
 */
export const STATUTS = {
  legitime: {
    label: 'Légitime',
    color: 'var(--color-status-good)',
    text: 'text-status-good',
    bg: 'bg-status-good/15',
    border: 'border-status-good/30',
    Icon: CheckCircleIcon,
  },
  suspect: {
    label: 'Suspect',
    color: 'var(--color-status-warning)',
    text: 'text-status-warning',
    bg: 'bg-status-warning/15',
    border: 'border-status-warning/30',
    Icon: AlertTriangleIcon,
  },
  fraude: {
    label: 'Fraude',
    color: 'var(--color-status-critical)',
    text: 'text-status-critical',
    bg: 'bg-status-critical/15',
    border: 'border-status-critical/30',
    Icon: AlertOctagonIcon,
  },
}

export function infosStatut(niveauRisque) {
  return STATUTS[niveauRisque] ?? STATUTS.legitime
}
