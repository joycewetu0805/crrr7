/**
 * Carte KPI generique. Contrat : label (sans ":"), value (grand, semi-gras),
 * une icone optionnelle, une couleur d'accent optionnelle pour les valeurs
 * qui portent un jugement (ex: nombre de fraudes en rouge).
 */
export default function StatTile({ label, value, Icon, accentClass = 'text-primary' }) {
  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted">{label}</span>
        {Icon && <Icon size={16} className="text-muted" />}
      </div>
      <p className={`mt-2 text-2xl font-semibold ${accentClass}`}>{value}</p>
    </div>
  )
}
