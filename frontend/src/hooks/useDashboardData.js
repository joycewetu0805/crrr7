import { useCallback, useEffect, useState } from 'react'
import { recupererComptes, recupererStats, recupererTransactions } from '../api/client'

const INTERVALLE_RAFRAICHISSEMENT_MS = 15000

/**
 * Centralise le chargement des donnees du dashboard (stats + historique +
 * comptes) et leur rafraichissement. Un seul hook, utilise une seule fois
 * par <Dashboard /> : c'est suffisant pour un MVP, pas besoin d'un store
 * global pour 3 requetes.
 */
export function useDashboardData() {
  const [stats, setStats] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [comptes, setComptes] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)

  const rafraichir = useCallback(async () => {
    try {
      const [statsData, transactionsData] = await Promise.all([
        recupererStats(),
        recupererTransactions(30),
      ])
      setStats(statsData)
      setTransactions(transactionsData)
      setErreur(null)
    } catch (err) {
      setErreur(err.message)
    } finally {
      setChargement(false)
    }
  }, [])

  useEffect(() => {
    recupererComptes().then(setComptes).catch(() => {})
  }, [])

  useEffect(() => {
    rafraichir()
    const intervalle = setInterval(rafraichir, INTERVALLE_RAFRAICHISSEMENT_MS)
    return () => clearInterval(intervalle)
  }, [rafraichir])

  return { stats, transactions, comptes, chargement, erreur, rafraichir }
}
