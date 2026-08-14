import { useState } from 'react'
import { infosStatut } from '../common/statutConfig.js'

const NB_BARRES = 12
const HAUTEUR_ZONE_PX = 140

function formaterMontant(valeur, devise) {
  return `${valeur.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} ${devise}`
}

function formaterHeure(dateISO) {
  return new Date(dateISO).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

/**
 * Comparer une grandeur (le montant) transaction par transaction, colore
 * par statut (etat) plutot que par magnitude : chaque barre porte sa
 * propre couleur de risque. Bare hover tooltip par barre (regle
 * d'interaction de la charte data-viz du projet).
 */
export default function MontantsRecents({ transactions }) {
  const [survolIndex, setSurvolIndex] = useState(null)

  const recentes = [...transactions].reverse().slice(-NB_BARRES)

  if (recentes.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-4">
        <h3 className="text-sm font-medium text-primary">Montants des transactions récentes</h3>
        <p className="mt-6 text-center text-sm text-muted">Aucune transaction pour le moment.</p>
      </div>
    )
  }

  const montantMax = Math.max(...recentes.map((t) => t.montant))

  return (
    <div className="relative rounded-xl border border-border bg-surface p-4">
      <h3 className="text-sm font-medium text-primary">Montants des transactions récentes</h3>

      <div
        className="mt-6 flex items-end gap-1.5"
        style={{ height: HAUTEUR_ZONE_PX }}
        onMouseLeave={() => setSurvolIndex(null)}
      >
        {recentes.map((transaction, index) => {
          const { color } = infosStatut(transaction.niveau_risque)
          const hauteur = Math.max((transaction.montant / montantMax) * HAUTEUR_ZONE_PX, 3)
          return (
            <div
              key={transaction.transaction_id}
              className="group relative flex-1 cursor-default"
              onMouseEnter={() => setSurvolIndex(index)}
            >
              <div
                className="mx-auto w-full max-w-6 rounded-t transition-opacity group-hover:opacity-80"
                style={{ height: hauteur, backgroundColor: color }}
              />
              {survolIndex === index && (
                <div className="absolute bottom-full left-1/2 z-10 mb-2 w-max -translate-x-1/2 rounded-lg border border-border bg-surface-raised px-2.5 py-1.5 text-xs shadow-lg">
                  <p className="font-medium text-primary">
                    {formaterMontant(transaction.montant, transaction.devise)}
                  </p>
                  <p className="text-muted">
                    {transaction.nom_titulaire} · {formaterHeure(transaction.date_transaction)}
                  </p>
                </div>
              )}
            </div>
          )
        })}
      </div>
      <div className="mt-2 h-px bg-gridline" />
      <p className="mt-2 text-xs text-muted">
        {recentes.length} dernières transactions · survolez une barre pour le détail
      </p>
    </div>
  )
}
