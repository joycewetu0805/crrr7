export function EtatChargement() {
  return (
    <div className="flex h-64 items-center justify-center text-sm text-muted">
      Chargement du dashboard…
    </div>
  )
}

export function EtatErreur({ message, onReessayer }) {
  return (
    <div className="mx-auto mt-10 max-w-md rounded-xl border border-status-critical/30 bg-status-critical/10 p-5 text-center">
      <p className="text-sm font-medium text-status-critical">Impossible de contacter l'API</p>
      <p className="mt-1 text-xs text-secondary">{message}</p>
      <p className="mt-2 text-xs text-muted">
        Vérifiez que le backend tourne (<code>uvicorn app.main:app --reload</code> dans{' '}
        <code>backend/</code>).
      </p>
      {onReessayer && (
        <button
          onClick={onReessayer}
          className="mt-3 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white hover:opacity-90"
        >
          Réessayer
        </button>
      )}
    </div>
  )
}
