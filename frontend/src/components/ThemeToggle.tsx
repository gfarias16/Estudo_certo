import { useState } from 'react'
import { Moon, Sun } from 'lucide-react'

export function ThemeToggle() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme === 'light' ? 'light' : 'dark')
  const [temporary, setTemporary] = useState(false)
  const next = theme === 'dark' ? 'light' : 'dark'
  const label = `Ativar tema ${next === 'light' ? 'claro' : 'escuro'}`
  function toggle() {
    document.documentElement.dataset.theme = next
    document.documentElement.style.colorScheme = next
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', next === 'dark' ? '#0d1520' : '#142b45')
    setTheme(next)
    try {
      localStorage.setItem('estudo-certo-theme', next)
      setTemporary(false)
    } catch {
      setTemporary(true)
    }
  }
  return <button type="button" className="theme-toggle" onClick={toggle} aria-label={label} title={temporary ? `${label}. Preferência disponível apenas nesta aba.` : label}>
    {theme === 'dark' ? <Sun size={19} aria-hidden="true" /> : <Moon size={19} aria-hidden="true" />}<span>Tema {next === 'light' ? 'claro' : 'escuro'}</span>
  </button>
}
