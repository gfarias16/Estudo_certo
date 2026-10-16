import { useState, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import { ErrorState, Loading, PageTitle } from '../components/ui'

export function AccountPage() {
  const overview = useQuery({ queryKey: ['overview', '7'], queryFn: () => api.overview('7') })
  if (overview.isPending) return <Loading />
  if (overview.error) return <ErrorState error={overview.error} retry={() => void overview.refetch()} />
  return <><PageTitle eyebrow="DO SEU JEITO" title="Minha conta" description="Ajuste o tempo de estudo e mantenha seu acesso protegido." /><div className="settings-grid"><GoalForm initial={overview.data!.daily_minutes} /><PasswordForm /></div></>
}

function GoalForm({ initial }: { initial: number }) {
  const [minutes, setMinutes] = useState(initial)
  const [pending, setPending] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()
  async function submit(event: FormEvent) {
    event.preventDefault(); setPending(true); setMessage(''); setError('')
    try { await api.profile(minutes); await queryClient.invalidateQueries({ queryKey: ['overview'] }); setMessage('Meta de estudo atualizada.') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível atualizar.') }
    finally { setPending(false) }
  }
  return <form className="panel settings-form" onSubmit={submit}><h2>Seu tempo de estudo</h2><p className="muted">Uma sugestão de rotina, sem cronômetro obrigatório.</p><label htmlFor="daily-minutes">Minutos por dia</label><input id="daily-minutes" type="number" min={10} max={120} required value={minutes} onChange={e => setMinutes(e.target.valueAsNumber)} /><button className="button primary" disabled={pending}>{pending ? 'Salvando…' : 'Salvar meta'}</button>{message && <p role="status" className="positive">{message}</p>}{error && <p role="alert" className="inline-error">{error}</p>}</form>
}

function PasswordForm() {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [pending, setPending] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  async function submit(event: FormEvent) {
    event.preventDefault(); setMessage(''); setError('')
    if (next !== confirm) { setError('As novas senhas não coincidem.'); return }
    setPending(true)
    try { const data = await api.password(current, next); setMessage(data.detail); setCurrent(''); setNext(''); setConfirm('') }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível alterar a senha.') }
    finally { setPending(false) }
  }
  return <form className="panel settings-form" onSubmit={submit}><h2>Alterar senha</h2><p className="muted">Use pelo menos oito caracteres e evite dados pessoais.</p><label htmlFor="current-password">Senha atual</label><input id="current-password" type="password" autoComplete="current-password" required value={current} onChange={e => setCurrent(e.target.value)} /><label htmlFor="new-password">Nova senha</label><input id="new-password" type="password" autoComplete="new-password" required minLength={8} value={next} onChange={e => setNext(e.target.value)} /><label htmlFor="confirm-password">Confirme a nova senha</label><input id="confirm-password" type="password" autoComplete="new-password" required minLength={8} value={confirm} onChange={e => setConfirm(e.target.value)} /><button className="button primary" disabled={pending}>{pending ? 'Alterando…' : 'Alterar senha'}</button>{message && <p role="status" className="positive">{message}</p>}{error && <p role="alert" className="inline-error">{error}</p>}</form>
}
