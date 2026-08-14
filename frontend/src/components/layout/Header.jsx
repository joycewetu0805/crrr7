import { ShieldIcon } from '../common/icons.jsx'

export default function Header({ enLigne }) {
  return (
    <header className="border-b border-border bg-surface/60 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-2.5">
          <ShieldIcon size={26} className="text-accent" />
          <div>
            <h1 className="text-base font-semibold leading-none text-primary sm:text-lg">
              FraudShield
            </h1>
            <p className="mt-1 text-xs text-muted">Détection de fraude en temps réel</p>
          </div>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-secondary">
          <span
            className={`h-2 w-2 rounded-full ${enLigne ? 'bg-status-good' : 'bg-status-critical'}`}
          />
          {enLigne ? 'API connectée' : 'API indisponible'}
        </div>
      </div>
    </header>
  )
}
