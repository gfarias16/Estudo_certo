import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { ArrowRight, BookOpen, Info } from 'lucide-react'
import { api, type Mode } from '../api/client'
import { QuestionCard } from '../components/QuestionCard'
import { EmptyState, ErrorState, Loading, PageTitle } from '../components/ui'

export function StudyPage({ errorsOnly }: { errorsOnly: boolean }) {
  const [params, setParams] = useSearchParams()
  const requestedMode = params.get('modo')
  const mode: Mode = errorsOnly ? 'errors' : requestedMode === 'unseen' || requestedMode === 'errors' ? requestedMode : 'all'
  const topic = params.get('tema') || ''
  const [page, setPage] = useState(1)
  const [index, setIndex] = useState(0)
  const [completed, setCompleted] = useState(false)
  const queryClient = useQueryClient()
  const topics = useQuery({ queryKey: ['topics'], queryFn: api.topics })
  const questions = useQuery({ queryKey: ['questions', mode, topic, page], queryFn: () => api.questions(mode, topic, page) })
  const question = questions.data?.results[index]
  function filter(name: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) next.set(name, value); else next.delete(name)
    setParams(next)
  }
  function next() {
    if (questions.data && index + 1 < questions.data.results.length) setIndex(index + 1)
    else {
      setCompleted(true)
      void queryClient.invalidateQueries({ queryKey: ['questions'] })
    }
  }
  function continueBlock() {
    setCompleted(false)
    setIndex(0)
    if (mode === 'all' && questions.data?.next) setPage(page + 1)
    else { setPage(1); void questions.refetch() }
  }
  return <>
    <PageTitle eyebrow={errorsOnly ? 'REVISAR TAMBÉM É AVANÇAR' : 'PRÁTICA COM FUNDAMENTO'} title={errorsOnly ? 'Caderno de erros' : 'Uma questão de cada vez.'} description={errorsOnly ? 'Retome os pontos que merecem atenção. Um novo acerto resolve a pendência e preserva o histórico.' : 'Escolha um tema, responda e confira a explicação diretamente no estatuto.'} />
    <section className="filter-bar" aria-label="Filtros de questões"><div><label htmlFor="topic">Tema do estatuto</label><select id="topic" value={topic} onChange={e => filter('tema', e.target.value)}><option value="">Todos os temas</option>{topics.data?.map(item => <option key={item.slug} value={item.slug}>{item.name}</option>)}</select></div>{!errorsOnly && <div><label htmlFor="mode">Quero praticar</label><select id="mode" value={mode} onChange={e => filter('modo', e.target.value)}><option value="all">Todas as questões</option><option value="unseen">Ainda não respondidas</option><option value="errors">Meus erros pendentes</option></select></div>}<span className="filter-count">{questions.data ? questions.data.count + ' questões na seleção' : 'Consultando catálogo…'}</span></section>
    {topics.error && <ErrorState error={topics.error} retry={() => void topics.refetch()} />}
    {questions.isPending ? <Loading label="Buscando as questões desta seleção…" /> : questions.error ? <ErrorState error={questions.error} retry={() => void questions.refetch()} /> :
      completed ? <section className="empty-state"><span className="eyebrow">BLOCO CONCLUÍDO</span><h2>Mais um passo na sua preparação.</h2><p className="muted">As respostas estão no seu histórico. Continue com outro bloco ou acompanhe seu desempenho.</p><button className="button primary" onClick={continueBlock}>Continuar praticando<ArrowRight size={17} aria-hidden="true" /></button><a className="text-link" href="/desempenho">Ver meu desempenho</a></section> :
      question ? <div className="study-layout"><QuestionCard key={question.id} question={question} position={(index + 1) + ' de ' + questions.data!.results.length + ' neste bloco'} onNext={next} onAnswered={() => { void queryClient.invalidateQueries({ queryKey: ['overview'] }) }} />
        <aside className="study-aside"><BookOpen size={24} aria-hidden="true" /><span className="eyebrow">COMO APROVEITAR MELHOR</span><h2>Entenda por que cada alternativa está certa ou errada.</h2><p>O gabarito aparece depois da confirmação, junto com o artigo e a página do documento.</p><div className="aside-rule" /><Info size={18} aria-hidden="true" /><p className="small">Questões autorais inspiradas em formatos de concurso. A referência normativa é a Lei nº 1.625/2026.</p></aside></div> :
      <EmptyState title={mode === 'errors' ? 'Nenhum erro pendente nesta seleção.' : mode === 'unseen' ? 'Você já passou por todas as questões desta seleção.' : 'Nenhuma questão nesta seleção.'} action={{ to: '/questoes', label: 'Explorar o catálogo' }}><p>{mode === 'errors' ? 'Continue praticando para fortalecer o que aprendeu. Os erros anteriores seguem registrados no desempenho.' : 'Escolha outro tema ou revise o que já estudou.'}</p></EmptyState>}
  </>
}
