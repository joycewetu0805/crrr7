import { useState } from 'react'
import { analyserTransaction } from '../../api/client.js'
import StatusBadge from './StatusBadge.jsx'

const TYPES_TRANSACTION = [
  { valeur: 'achat_en_ligne', label: 'Achat en ligne' },
  { valeur: 'paiement_pos', label: 'Paiement carte' },
  { valeur: 'retrait_atm', label: 'Retrait DAB' },
  { valeur: 'virement', label: 'Virement' },
]

const CANAUX = [
  { valeur: 'web', label: 'Web' },
  { valeur: 'mobile', label: 'Mobile' },
  { valeur: 'pos', label: 'Terminal (POS)' },
  { valeur: 'atm', label: 'DAB' },
]

const PAYS = [
  'France',
  'Belgique',
  'Allemagne',
  'Espagne',
  'Italie',
  'Nigeria',
  'Russie',
  'Roumanie',
  'Ukraine',
]

const ETAT_INITIAL = {
  compte_id: '',
  montant: '',
  type_transaction: 'achat_en_ligne',
  canal: 'web',
  pays_transaction: 'France',
  marchand: '',
}

/**
 * Formulaire de demonstration : soumet une transaction a POST /api/predict
 * et affiche le verdict immediatement. C'est le moment-cle de la demo
 * devant un jury (feature indispensable identifiee des la phase
 * d'architecture du projet).
 */
export default function NewTransactionForm({ comptes, onAnalysed }) {
  const [valeurs, setValeurs] = useState(ETAT_INITIAL)
  const [envoi, setEnvoi] = useState(false)
  const [resultat, setResultat] = useState(null)
  const [erreur, setErreur] = useState(null)

  function majChamp(champ, valeur) {
    setValeurs((precedent) => ({ ...precedent, [champ]: valeur }))
  }

  async function soumettre(evenement) {
    evenement.preventDefault()
    setEnvoi(true)
    setErreur(null)
    setResultat(null)

    try {
      const reponse = await analyserTransaction({
        ...valeurs,
        compte_id: Number(valeurs.compte_id),
        montant: Number(valeurs.montant),
        marchand: valeurs.marchand || null,
      })
      setResultat(reponse)
      onAnalysed?.()
    } catch (err) {
      setErreur(err.message)
    } finally {
      setEnvoi(false)
    }
  }

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <h3 className="text-sm font-medium text-primary">Analyser une nouvelle transaction</h3>

      <form onSubmit={soumettre} className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <label className="text-xs text-secondary">
          Compte
          <select
            required
            value={valeurs.compte_id}
            onChange={(e) => majChamp('compte_id', e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary"
          >
            <option value="" disabled>
              Choisir un compte
            </option>
            {comptes.map((compte) => (
              <option key={compte.id} value={compte.id}>
                {compte.nom_titulaire} ({compte.pays})
              </option>
            ))}
          </select>
        </label>

        <label className="text-xs text-secondary">
          Montant (EUR)
          <input
            required
            type="number"
            min="0.5"
            step="0.01"
            value={valeurs.montant}
            onChange={(e) => majChamp('montant', e.target.value)}
            placeholder="ex : 1500"
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary placeholder:text-muted"
          />
        </label>

        <label className="text-xs text-secondary">
          Type
          <select
            value={valeurs.type_transaction}
            onChange={(e) => majChamp('type_transaction', e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary"
          >
            {TYPES_TRANSACTION.map((type) => (
              <option key={type.valeur} value={type.valeur}>
                {type.label}
              </option>
            ))}
          </select>
        </label>

        <label className="text-xs text-secondary">
          Canal
          <select
            value={valeurs.canal}
            onChange={(e) => majChamp('canal', e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary"
          >
            {CANAUX.map((canal) => (
              <option key={canal.valeur} value={canal.valeur}>
                {canal.label}
              </option>
            ))}
          </select>
        </label>

        <label className="text-xs text-secondary">
          Pays de la transaction
          <select
            value={valeurs.pays_transaction}
            onChange={(e) => majChamp('pays_transaction', e.target.value)}
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary"
          >
            {PAYS.map((pays) => (
              <option key={pays} value={pays}>
                {pays}
              </option>
            ))}
          </select>
        </label>

        <label className="text-xs text-secondary">
          Marchand (optionnel)
          <input
            type="text"
            value={valeurs.marchand}
            onChange={(e) => majChamp('marchand', e.target.value)}
            placeholder="ex : Amazon"
            className="mt-1 w-full rounded-lg border border-border bg-page px-3 py-2 text-sm text-primary placeholder:text-muted"
          />
        </label>

        <button
          type="submit"
          disabled={envoi}
          className="col-span-1 mt-1 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 sm:col-span-2"
        >
          {envoi ? 'Analyse en cours…' : 'Analyser la transaction'}
        </button>
      </form>

      {erreur && (
        <p className="mt-3 rounded-lg border border-status-critical/30 bg-status-critical/10 px-3 py-2 text-sm text-status-critical">
          {erreur}
        </p>
      )}

      {resultat && (
        <div className="mt-3 flex items-center justify-between rounded-lg border border-border bg-page px-3 py-2.5">
          <div>
            <p className="text-xs text-muted">Résultat du modèle</p>
            <p className="tabular text-sm text-secondary">
              Probabilité de fraude : {(resultat.probabilite * 100).toFixed(1)}%
            </p>
          </div>
          <StatusBadge niveauRisque={resultat.niveau_risque} />
        </div>
      )}
    </div>
  )
}
