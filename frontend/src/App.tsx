import { useEffect, useState, type FormEvent } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { BookOpen, ChartNoAxesCombined, ChevronRight, ClipboardList, LayoutDashboard, LogOut, Settings2, ShieldCheck, Target } from 'lucide-react'
import { api, type Session } from './api/client'
import { ErrorState, Loading } from './components/ui'
import { Dashboard } from './pages/Dashboard'
import { StudyPage } from './pages/StudyPage'
import { ProgressPage } from './pages/ProgressPage'
import { PlanPage } from './pages/PlanPage'
import { AccountPage } from './pages/AccountPage'
import { ThemeToggle } from './components/ThemeToggle'

const navigation = [
  { to: '/inicio', label: 'Meu estudo', icon: LayoutDashboard },
  { to: '/questoes', label: 'Questões', icon: BookOpen },
  { to: '/erros', label: 'Caderno de erros', icon: ClipboardList },
  { to: '/desempenho', label: 'Desempenho', icon: ChartNoAxesCombined },
  { to: '/plano', label: 'Plano de estudo', icon: Target },
]

function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [pending, setPending] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault()
    setPending(true)
    setError('')
    try { onLogin(await api.login(username.trim(), password)) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Não foi possível entrar.') }
    finally { setPending(false); setPassword('') }
  }
  return <div className="login-shell">
    <section className="login-story"><div className="brand"><span className="brand-mark">e.</span><span>estudo<span className="brand-light">certo</span></span></div><div><span className="eyebrow light">PREPARAÇÃO COM FUNDAMENTO</span><h1>Conhecer a lei.<br />Entender o erro.<br /><em>Avançar de verdade.</em></h1><p>Seu espaço para estudar o Estatuto da Guarda Municipal de São Gonçalo, uma questão de cada vez.</p></div><div className="login-source"><ShieldCheck size={22} aria-hidden="true" /><span>Lei nº 1.625/2026<br /><small>Questões autorais com fundamento no estatuto.</small></span></div></section>
    <main className="login-main"><form onSubmit={submit} className="login-form"><ThemeToggle /><span className="eyebrow">SEU PRÓXIMO PASSO</span><h2>Bom ter você por aqui.</h2><p className="muted">Entre para continuar a sua preparação.</p><label htmlFor="username">Usuário</label><input id="username" autoComplete="username" required maxLength={150} value={username} onChange={e => setUsername(e.target.value)} autoCapitalize="none" />
      <label htmlFor="password">Senha</label><input id="password" type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} />
      {error && <p role="alert" className="inline-error">{error}</p>}
      <button className="button primary" disabled={pending}>{pending ? 'Entrando…' : 'Entrar no meu estudo'}<ChevronRight size={18} aria-hidden="true" /></button>
      <p className="small muted login-help">Acesso privado. Para criar sua conta ou recuperar a senha, fale com o responsável pelo sistema.</p>
    </form><p className="small muted">Material independente de estudo. Sem vínculo oficial com a Guarda ou a banca.</p></main>
  </div>
}

export function App() {
  const queryClient = useQueryClient()
  const session = useQuery({ queryKey: ['session'], queryFn: api.session, staleTime: Infinity })
  const location = useLocation()
  const [logoutError, setLogoutError] = useState('')
  const [loggingOut, setLoggingOut] = useState(false)
  useEffect(() => {
    function expired() {
      queryClient.setQueryData<Session>(['session'], previous => previous ? { ...previous, user: null } : undefined)
      queryClient.removeQueries({ predicate: query => query.queryKey[0] !== 'session' })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
    }
    window.addEventListener('study:session-expired', expired)
    return () => window.removeEventListener('study:session-expired', expired)
  }, [queryClient])
  useEffect(() => {
    const label = navigation.find(item => item.to === location.pathname)?.label || 'Minha conta'
    document.title = label + ' · Estudo Certo'
  }, [location.pathname])
  async function leave() {
    setLoggingOut(true)
    setLogoutError('')
    try {
      await api.logout()
      queryClient.clear()
      await queryClient.fetchQuery({ queryKey: ['session'], queryFn: api.session })
    } catch (cause) { setLogoutError(cause instanceof Error ? cause.message : 'Não foi possível sair.') }
    finally { setLoggingOut(false) }
  }
  if (session.isPending) return <Loading label="Preparando seu espaço de estudo…" />
  if (session.error) return <main className="standalone"><ErrorState error={session.error} retry={() => void session.refetch()} /></main>
  if (!session.data?.user) return <Login onLogin={data => { queryClient.removeQueries({ predicate: query => query.queryKey[0] !== 'session' }); queryClient.setQueryData(['session'], data) }} />
  const user = session.data.user
  return <div className="app-shell">
    <a href="#main" className="skip-link">Pular para o conteúdo</a>
    <aside className="sidebar"><NavLink to="/inicio" className="brand" aria-label="Estudo Certo, início"><span className="brand-mark">e.</span><span>estudo<span className="brand-light">certo</span></span></NavLink><div className="workspace-label"><span className="eyebrow light">SUA PREPARAÇÃO</span><strong>Guarda Municipal</strong><span>São Gonçalo · RJ</span></div>
      <nav aria-label="Navegação principal">{navigation.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => 'nav-item ' + (isActive ? 'active' : '')}><Icon size={19} aria-hidden="true" /><span>{label}</span></NavLink>)}</nav>
      <div className="sidebar-footer"><span className="edition">ESTATUTO GMS · EDIÇÃO 2026</span><p>Consistência hoje.<br />Mais segurança na próxima questão.</p><NavLink to="/conta" className="account-link"><span className="avatar">{user.display_name.slice(0, 1).toUpperCase()}</span><span>{user.display_name}<small>Minha conta</small></span><Settings2 size={17} aria-hidden="true" /></NavLink><button className="logout-button" onClick={leave} disabled={loggingOut}><LogOut size={16} aria-hidden="true" />{loggingOut ? 'Saindo…' : 'Sair da conta'}</button>{logoutError && <p role="alert">{logoutError}</p>}</div>
    </aside>
    <div className="main-column"><header className="topbar"><span className="breadcrumb">Sua preparação <ChevronRight size={14} aria-hidden="true" /><strong>Estatuto GMS</strong></span><span className="private-label"><span className="status-dot" />Espaço privado</span><ThemeToggle /><div className="mobile-tools"><NavLink to="/conta" aria-label="Minha conta"><Settings2 size={20} aria-hidden="true" /></NavLink><button aria-label="Sair da conta" onClick={leave} disabled={loggingOut}><LogOut size={20} aria-hidden="true" /></button></div></header>
      <main id="main" className="main-content" tabIndex={-1}><Routes>
        <Route path="/inicio" element={<Dashboard name={user.display_name} />} />
        <Route path="/questoes" element={<StudyPage key={location.pathname + location.search} errorsOnly={false} />} />
        <Route path="/erros" element={<StudyPage key={location.pathname + location.search} errorsOnly />} />
        <Route path="/desempenho" element={<ProgressPage />} />
        <Route path="/plano" element={<PlanPage />} />
        <Route path="/conta" element={<AccountPage />} />
        <Route path="*" element={<Navigate to="/inicio" replace />} />
      </Routes><footer className="page-footer"><span>Estudo Certo · Preparação com fundamento.</span><span>Material autoral e independente.</span></footer></main>
    </div>
  </div>
}
