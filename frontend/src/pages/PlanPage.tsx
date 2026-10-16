import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen, FileText, RotateCcw } from 'lucide-react'
import { api } from '../api/client'
import { ErrorState, Loading, PageTitle } from '../components/ui'

export function PlanPage() {
  const overview = useQuery({ queryKey: ['overview', '7'], queryFn: () => api.overview('7') })
  const documents = useQuery({ queryKey: ['documents'], queryFn: api.documents })
  if (overview.isPending || documents.isPending) return <Loading />
  if (overview.error) return <ErrorState error={overview.error} retry={() => void overview.refetch()} />
  if (documents.error) return <ErrorState error={documents.error} retry={() => void documents.refetch()} />
  const data = overview.data!
  const recommendation = data.recommendation
  return <>
    <PageTitle eyebrow="DIREÇÃO PARA O PRÓXIMO PASSO" title="Estude com um rumo claro." description="Uma rotina simples, ajustada aos temas e às respostas que você já registrou." />
    <section className="plan-recommendation"><span className="eyebrow">PRIORIDADE DA PRÓXIMA SESSÃO</span><h2>{recommendation?.topic_name || 'Explore o estatuto'}</h2><p>{recommendation?.reason || 'Comece pelas competências da Guarda Municipal e avance pelos temas disponíveis.'}</p><Link className="button primary" to={recommendation ? '/questoes?' + new URLSearchParams({ tema: recommendation.topic_slug, modo: recommendation.mode }) : '/questoes'}>Praticar este tema<ArrowRight size={17} aria-hidden="true" /></Link><p className="small muted">A prioridade considera erros pendentes, temas ainda não estudados e aproveitamento. É uma recomendação de prática, não uma previsão de cobrança na prova.</p></section>
    <section className="panel"><div className="panel-heading"><div><span className="eyebrow">SUA ROTINA · {data.daily_minutes} MINUTOS</span><h2>Leia. Pratique. Revise.</h2></div><Link className="text-link" to="/conta">Ajustar minha meta</Link></div><div className="plan-steps"><div><BookOpen aria-hidden="true" /><h3>1. Leia o tema</h3><p>Observe quem pratica o ato, as condições e os limites. Nas regras numéricas, registre prazo, unidade e exceções.</p></div><div><FileText aria-hidden="true" /><h3>2. Responda sem consultar</h3><p>Escolha a alternativa antes de conferir. Depois, leia os comentários de todas as opções e o trecho da fonte.</p></div><div><RotateCcw aria-hidden="true" /><h3>3. Retome seus erros</h3><p>Releia o fundamento antes de tentar de novo. Um acerto posterior resolve a pendência, sem apagar o primeiro resultado.</p></div></div></section>
    <section className="panel"><div className="panel-heading"><div><span className="eyebrow">COMO AS QUESTÕES SÃO ELABORADAS</span><h2>Variedade na prática. Cuidado com a fonte.</h2></div></div><p>Você encontrará texto da lei, situações práticas e comparação entre regras. As provas fornecidas ajudam a variar os enunciados; os gabaritos desta edição se apoiam no estatuto de São Gonçalo de 2026.</p><p className="muted">A V1 cobre uma seleção de artigos. Outras matérias do edital e a leitura integral da legislação continuam necessárias para uma preparação completa.</p><a className="text-link" href="https://selecon.selecao.net.br/informacoes/73/" target="_blank" rel="noreferrer">Consultar edital e publicações oficiais da Selecon<ArrowRight size={16} aria-hidden="true" /></a></section>
    <section className="panel"><div className="panel-heading"><div><span className="eyebrow">BASE DOCUMENTAL</span><h2>Saiba de onde vem o conteúdo</h2></div></div><div className="document-list">{documents.data?.map(doc => <article key={doc.slug}><FileText size={23} aria-hidden="true" /><div><span className={'tag ' + (doc.kind === 'law' ? 'cool' : '')}>{doc.kind === 'law' ? 'Fonte dos gabaritos' : 'Referência de estilo'}</span><h3>{doc.title}</h3><p>{doc.version} · {doc.pages} páginas</p><p className="muted small">{doc.notes}</p></div></article>)}</div><p className="muted small">Os PDFs originais são preservados na documentação do projeto. Os recortes pertinentes aparecem na correção de cada questão.</p></section>
  </>
}
