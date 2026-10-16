import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { QuestionCard } from './QuestionCard'
import { api, type Correction, type Question } from '../api/client'

vi.mock('../api/client', () => ({ api: { submit: vi.fn() } }))
const question: Question = {
  id: 1, key: 'gms-001', revision: 1, prompt: 'Qual a regra para estudo?',
  topic: { slug: 'fundamentos', name: 'Fundamentos', discipline: 'Estatuto GMS', position: 0 },
  options: [{ text: 'Alternativa um' }, { text: 'Alternativa dois' }, { text: 'Alternativa três' }, { text: 'Alternativa quatro' }],
  style: 'literal', last_correct: null, source_label: 'Questão autoral',
}
const correction: Correction = {
  id: 1, request_id: '00000000-0000-4000-8000-000000000001',
  selected_choice: 0, is_correct: true, correct_choice: 0,
  explanation: 'Fundamento conferido no texto.',
  options: question.options.map(option => ({ ...option, explanation: 'Comentário fundamentado.' })),
  excerpts: [], created_at: '2026-10-15T12:00:00Z',
}

describe('Questão e confirmação do servidor', () => {
  beforeEach(() => { vi.mocked(api.submit).mockReset() })
  it('exige seleção e só exibe a correção após persistência confirmada', async () => {
    let resolve!: (value: Correction) => void
    vi.mocked(api.submit).mockReturnValue(new Promise(done => { resolve = done }))
    const saved = vi.fn()
    render(<QuestionCard question={question} onAnswered={saved} onNext={vi.fn()} position="1" />)
    expect(screen.getByRole('button', { name: 'Confirmar resposta' })).toBeDisabled()
    fireEvent.click(screen.getByRole('radio', { name: /Alternativa um/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar resposta' }))
    expect(screen.getByRole('button', { name: 'Salvando resposta…' })).toBeDisabled()
    expect(screen.queryByText('Resposta salva no seu histórico.')).not.toBeInTheDocument()
    resolve(correction)
    await screen.findByText('Resposta salva no seu histórico.')
    expect(saved).toHaveBeenCalledOnce()
  })
  it('mantém o mesmo identificador ao repetir envio após falha de comunicação', async () => {
    vi.mocked(api.submit).mockRejectedValueOnce(new Error('Falha de comunicação')).mockResolvedValueOnce(correction)
    render(<QuestionCard question={question} onAnswered={vi.fn()} onNext={vi.fn()} position="1" />)
    fireEvent.click(screen.getByRole('radio', { name: /Alternativa um/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar resposta' }))
    await screen.findByRole('alert')
    expect(screen.queryByText('Resposta salva no seu histórico.')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Confirmar resposta' }))
    await waitFor(() => expect(api.submit).toHaveBeenCalledTimes(2))
    expect(vi.mocked(api.submit).mock.calls[0][2]).toEqual(vi.mocked(api.submit).mock.calls[1][2])
  })
})
