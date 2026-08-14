import StatusBadge from './StatusBadge.jsx'

const LIBELLES_TYPE = {
  achat_en_ligne: 'Achat en ligne',
  paiement_pos: 'Paiement carte',
  retrait_atm: 'Retrait DAB',
  virement: 'Virement',
}

function formaterDate(dateISO) {
  return new Date(dateISO).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function TransactionsTable({ transactions }) {
  return (
    <div className="rounded-xl border border-border bg-surface">
      <div className="flex items-center justify-between border-b border-border p-4">
        <h3 className="text-sm font-medium text-primary">Transactions récentes</h3>
        <span className="text-xs text-muted">{transactions.length} affichées</span>
      </div>

      {transactions.length === 0 ? (
        <p className="p-6 text-center text-sm text-muted">Aucune transaction pour le moment.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted">
                <th className="px-4 py-2.5 font-medium">Titulaire</th>
                <th className="px-4 py-2.5 font-medium">Type</th>
                <th className="px-4 py-2.5 font-medium">Pays</th>
                <th className="px-4 py-2.5 font-medium">Date</th>
                <th className="px-4 py-2.5 text-right font-medium">Montant</th>
                <th className="px-4 py-2.5 text-right font-medium">Risque</th>
                <th className="px-4 py-2.5 text-right font-medium">Statut</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr
                  key={transaction.transaction_id}
                  className="border-b border-border last:border-0 hover:bg-surface-raised"
                >
                  <td className="px-4 py-2.5 text-primary">{transaction.nom_titulaire}</td>
                  <td className="px-4 py-2.5 text-secondary">
                    {LIBELLES_TYPE[transaction.type_transaction] ?? transaction.type_transaction}
                  </td>
                  <td className="px-4 py-2.5 text-secondary">{transaction.pays_transaction}</td>
                  <td className="tabular px-4 py-2.5 text-muted">
                    {formaterDate(transaction.date_transaction)}
                  </td>
                  <td className="tabular px-4 py-2.5 text-right text-primary">
                    {transaction.montant.toLocaleString('fr-FR', { maximumFractionDigits: 0 })}{' '}
                    {transaction.devise}
                  </td>
                  <td className="tabular px-4 py-2.5 text-right text-muted">
                    {(transaction.probabilite * 100).toFixed(0)}%
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <StatusBadge niveauRisque={transaction.niveau_risque} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
