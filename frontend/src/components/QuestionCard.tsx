import { useRef, useState } from 'react'
import { ArrowRight, BookOpen, Check, CheckCircle2, CircleX } from 'lucide-react'
import { api, type Correction, type Question } from '../api/client'

const styleLabels = { literal: 'Texto da lei', case: 'Situação prática', comparison: 'Comparação de regras' }

export function QuestionCard({ question, onAnswered, onNext, position }: {
  question: Question; onAnswered: () => void; onNext: () => void; position: string
}) {
  const [selected, setSelected] = useState<number | null>(null)
  const [correction, setCorrection] = useState<Correction | null>(null)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  const submission = useRef<{ id: string; choice: number } | null>(null)
  const feedbackRef = useRef<HTMLDivElement>(null)

  async function confirm() {
    if (selected === null || pending) return
    if (!submission.current || submission.current.choice !== selected) {
      submission.current = { id: crypto.randomUUID(), choice: selected }
    }
    setPending(true)
    setError('')
    try {
      const result = await api.submit(question.id, selected, submission.current.id)
      setCorrection(result)
      onAnswered()
      requestAnimationFrame(() => feedbackRef.current?.focus())
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Não foi possível salvar a resposta.')
    } finally { setPending(false) }
  }

  return <article className="question-card">
    <div className="question-meta"><span className="eyebrow">{question.key.toUpperCase()} · {position}</span><span className="tag">{styleLabels[question.style || 'literal']}</span></div>
    <p className="source-label">{question.source_label} <span> / </span> {question.topic.name}</p>
    <fieldset disabled={pending || correction !== null} className="question-fieldset">
      <legend>{question.prompt}</legend>
      <div className="options">{question.options.map((option, index) => {
        const isCorrect = correction?.correct_choice === index
        const isWrong = correction !== null && selected === index && !isCorrect
        return <label key={index} className={'option ' + (isCorrect ? 'correct' : isWrong ? 'incorrect' : selected === index ? 'selected' : '')}>
          <input type="radio" name={'question-' + question.id} value={index} checked={selected === index} onChange={() => setSelected(index)} />
          <span className="option-letter" aria-hidden="true">{String.fromCharCode(65 + index)}</span>
          <span className="option-copy"><span>{option.text}</span>{correction && <small>{correction.options[index].explanation}</small>}</span>
          {isCorrect && <Check size={19} aria-label="Alternativa correta" />}
          {isWrong && <CircleX size={19} aria-label="Sua resposta está incorreta" />}
        </label>
      })}</div>
    </fieldset>
    {error && <p role="alert" className="inline-error">{error} A resposta só aparece como salva após confirmação do servidor.</p>}
    {!correction ? <div className="question-actions"><span className="muted small">Escolha uma alternativa para conferir.</span><button className="button primary" disabled={selected === null || pending} onClick={confirm}>{pending ? 'Salvando resposta…' : 'Confirmar resposta'}<ArrowRight size={17} aria-hidden="true" /></button></div> :
      <div className="correction" ref={feedbackRef} tabIndex={-1}>
        <div className={'feedback-title ' + (correction.is_correct ? 'positive' : 'negative')}>{correction.is_correct ? <CheckCircle2 aria-hidden="true" /> : <CircleX aria-hidden="true" />}<h2>{correction.is_correct ? 'Resposta correta. Continue assim.' : 'Um ponto para revisar.'}</h2></div>
        <p>{correction.explanation}</p>
        <div className="legal-basis"><div className="legal-heading"><BookOpen size={17} aria-hidden="true" /><strong>Confira no estatuto</strong></div>{correction.excerpts.map((excerpt, index) => <div key={index}><p className="small"><strong>{excerpt.reference}</strong> · página {excerpt.page} · {excerpt.document.filename}</p><blockquote>{excerpt.text}</blockquote><p className="muted small">Recorte do documento fornecido; pontuação e ortografia normalizadas.</p></div>)}</div>
        <div className="question-actions"><span className="small muted">Resposta salva no seu histórico.</span><button className="button primary" onClick={onNext}>Próxima questão<ArrowRight size={17} aria-hidden="true" /></button></div>
      </div>}
  </article>
}
