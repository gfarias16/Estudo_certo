import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, Check, CheckCheck, ChevronRight, Clock3, ListChecks, Target, TrendingUp } from 'lucide-react'
import { api } from '../api/client'
import { EmptyState, ErrorState, Loading, PageTitle, Percent } from '../components/ui'

export function Dashboard({ name }: { name: string }) {
  const { data, isPending, error, refetch } = useQuery({ queryKey: ['overview', '7'], queryFn: () => api.overview('7') })
  if (isPending) return <Loading />
  if (error) return <ErrorState error={error} retry={() => void refetch()} />
  if (!data) return null
  const coverage = data.available_questions ? Math.round(data.answered_unique / data.available_questions * 100) : 0
  const recommendation = data.recommendation
  const studyLink = recommendation ? '/questoes?' + new URLSearchParams({ modo: recommendation.mode, tema: recommendation.topic_slug }) : '/questoes'
  return <>
    <PageTitle eyebrow="UM POUCO TODOS OS DIAS" title={'Vamos avançar, ' + name + '.'} description="Cada questão é uma oportunidade de entender melhor o estatuto." action={<span className="date-label">{new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long', timeZone: 'America/Sao_Paulo' })}</span>} />
    <section className="study-banner"><div><div className="banner-label"><span className="status-dot" />SEU FOCO AGORA</div><h2>{data.pending_errors ? 'Transforme seus erros em próximos acertos.' : 'Construa uma base sólida, artigo por artigo.'}</h2><p>{recommendation ? recommendation.topic_name : 'Estatuto da Guarda Municipal de São Gonçalo'}</p><Link className="button primary" to={studyLink}>{data.answered_unique ? 'Continuar estudando' : 'Começar a estudar'}<ArrowRight size={17} aria-hidden="true" /></Link></div><div className="banner-note"><BookOpen size={28} strokeWidth={1.5} aria-hidden="true" /><span>LEI Nº 1.625/2026</span><strong>Conheça a regra.<br />Entenda o fundamento.</strong><small>Questões comentadas e referências ao texto da lei.</small></div></section>
    <div className="section-heading"><h2>Seu estudo em números</h2><span className="small muted">Tentativas dos últimos 7 dias</span></div>
    <div className="stats-grid">
      <Stat label="Questões respondidas" value={data.total_attempts} detail="tentativas no período" icon={<ListChecks size={20} />} />
      <Stat label="Aproveitamento" value={<Percent value={data.accuracy} />} detail={data.total_attempts ? data.correct + ' acertos no período' : 'a primeira resposta inicia sua análise'} icon={<Target size={20} />} />
      <Stat label="Erros para revisar" value={data.pending_errors} detail="pendências atuais, em todo o histórico" icon={<BookOpen size={20} />} />
      <Stat label="Cobertura do catálogo" value={coverage + '%'} detail={data.answered_unique + ' de ' + data.available_questions + ' questões distintas'} icon={<TrendingUp size={20} />} />
    </div>
    <div className="dashboard-columns"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">PASSO A PASSO</span><h2>Uma sessão que cabe no seu dia.</h2></div><Clock3 size={21} aria-hidden="true" /></div><p className="muted">Sua meta atual é de {data.daily_minutes} minutos. O importante é manter o ritmo.</p><ol className="routine-list"><li><span className="step-number">01</span><div><strong>Leia com atenção</strong><span>Releia os artigos do tema escolhido.</span></div><span className="small muted">{Math.round(data.daily_minutes / 3)} min</span></li><li><span className="step-number">02</span><div><strong>Pratique e confira</strong><span>Responda e entenda cada comentário.</span></div><span className="small muted">{Math.round(data.daily_minutes / 2)} min</span></li><li><span className="step-number">03</span><div><strong>Feche com uma revisão</strong><span>Retome os pontos que merecem atenção.</span></div><span className="small muted">{data.daily_minutes - Math.round(data.daily_minutes / 3) - Math.round(data.daily_minutes / 2)} min</span></li></ol><Link to="/plano" className="text-link">Ver meu plano de estudo<ArrowRight size={16} aria-hidden="true" /></Link></section>
      <section className="panel coverage-panel"><div className="panel-heading"><div><span className="eyebrow">SEU PONTO DE PARTIDA</span><h2>{data.today_attempts ? 'Seu estudo de hoje já começou.' : 'Hoje é um bom dia para começar.'}</h2></div><CheckCheck size={22} aria-hidden="true" /></div><div className="today-total"><strong>{data.today_attempts}</strong><span>respostas registradas hoje</span></div><div className="progress-track" role="progressbar" aria-label="Cobertura do catálogo" aria-valuenow={coverage} aria-valuemin={0} aria-valuemax={100}><span style={{ width: coverage + '%' }} /></div><p className="small muted">{data.available_questions} questões autorais disponíveis. A cobertura representa o catálogo, não todos os artigos do estatuto.</p><Link className="text-link" to="/desempenho">Acompanhar minha evolução<ArrowRight size={16} aria-hidden="true" /></Link></section></div>
    <section className="panel topics-panel"><div className="panel-heading"><div><span className="eyebrow">MAPA DO ESTATUTO</span><h2>Onde concentrar sua atenção</h2></div><Link className="text-link" to="/questoes">Todos os temas<ArrowRight size={16} aria-hidden="true" /></Link></div>
      {data.available_questions ? <div className="topic-list">{data.topics.filter(t => t.available).map(topic => <Link key={topic.slug} className="topic-row" to={'/questoes?tema=' + topic.slug}><span className={'topic-icon ' + (topic.pending_errors ? 'attention' : '')}>{topic.answered === topic.available ? <Check size={18} aria-hidden="true" /> : <BookOpen size={18} aria-hidden="true" />}</span><div><strong>{topic.name}</strong><span>{topic.answered} de {topic.available} questões estudadas{topic.pending_errors ? ' · ' + topic.pending_errors + ' para revisar' : ''}</span></div><span className="topic-result">{topic.insufficient_sample ? 'Construindo a base' : <Percent value={topic.accuracy} />}</span><ChevronRight size={17} aria-hidden="true" /></Link>)}</div> : <EmptyState title="O catálogo está sendo preparado."><p>As questões aparecerão aqui após a importação pelo responsável.</p></EmptyState>}
    </section>
  </>
}

function Stat({ label, value, detail, icon }: { label: string; value: React.ReactNode; detail: string; icon: React.ReactNode }) {
  return <section className="stat-card"><div><span>{label}</span><span className="stat-icon" aria-hidden="true">{icon}</span></div><strong>{value}</strong><p>{detail}</p></section>
}
