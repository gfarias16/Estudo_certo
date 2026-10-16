import { AlertCircle, ArrowRight, LoaderCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

export function Loading({ label = 'Carregando seu estudo…' }: { label?: string }) {
  return <div className="state-box" role="status"><LoaderCircle className="spin" aria-hidden="true" /><p>{label}</p></div>
}

export function ErrorState({ error, retry }: { error: Error; retry?: () => void }) {
  return <div className="error-box" role="alert"><AlertCircle size={20} aria-hidden="true" /><div><strong>Não foi possível carregar</strong><p>{error.message}</p>{retry && <button className="button secondary compact" onClick={retry}>Tentar novamente</button>}</div></div>
}

export function EmptyState({ title, children, action }: { title: string; children: ReactNode; action?: { to: string; label: string } }) {
  return <div className="empty-state"><span className="eyebrow">UM PASSO DE CADA VEZ</span><h2>{title}</h2><div className="muted">{children}</div>{action && <Link className="button primary" to={action.to}>{action.label}<ArrowRight size={16} aria-hidden="true" /></Link>}</div>
}

export function PageTitle({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div>{action}</div>
}

export function Percent({ value }: { value: number | null | undefined }) {
  return <>{value == null ? '—' : value.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%'}</>
}
