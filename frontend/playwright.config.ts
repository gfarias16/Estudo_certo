import { randomUUID } from 'node:crypto'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { defineConfig, devices } from '@playwright/test'

process.env.E2E_PASSWORD ||= randomUUID() + 'aZ!'
const python = process.platform === 'win32' ? '..\\.venv\\Scripts\\python.exe' : '../.venv/bin/python'
const systemBrowser = process.platform === 'win32'
  ? ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'].find(existsSync)
  : undefined
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  timeout: 90_000,
  workers: 1,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:8001',
    trace: 'off',
    screenshot: 'off',
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || systemBrowser,
    },
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: python + ' ../scripts/serve_e2e.py', url: 'http://127.0.0.1:8001/health/', reuseExistingServer: false, timeout: 60_000, env: { E2E_PASSWORD: process.env.E2E_PASSWORD } },
  ],
  outputDir: path.resolve('test-results'),
})
