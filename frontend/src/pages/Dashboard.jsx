import Header from '../components/layout/Header.jsx'
import StatTilesRow from '../components/stats/StatTilesRow.jsx'
import RepartitionRisque from '../components/charts/RepartitionRisque.jsx'
import MontantsRecents from '../components/charts/MontantsRecents.jsx'
import FraudAlerts from '../components/alerts/FraudAlerts.jsx'
import TransactionsTable from '../components/transactions/TransactionsTable.jsx'
import NewTransactionForm from '../components/transactions/NewTransactionForm.jsx'
import { EtatChargement, EtatErreur } from '../components/common/EtatChargement.jsx'
import { useDashboardData } from '../hooks/useDashboardData.js'

export default function Dashboard() {
  const { stats, transactions, comptes, chargement, erreur, rafraichir } = useDashboardData()

  return (
    <div className="min-h-full">
      <Header enLigne={!erreur} />

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
        {chargement && <EtatChargement />}

        {erreur && !chargement && <EtatErreur message={erreur} onReessayer={rafraichir} />}

        {!chargement && !erreur && (
          <div className="flex flex-col gap-4">
            <StatTilesRow stats={stats} />

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <FraudAlerts transactions={transactions} />
              </div>
              <NewTransactionForm comptes={comptes} onAnalysed={rafraichir} />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <RepartitionRisque stats={stats} />
              <MontantsRecents transactions={transactions} />
            </div>

            <TransactionsTable transactions={transactions} />
          </div>
        )}
      </main>
    </div>
  )
}
