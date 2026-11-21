// Desktop shell: starts the FastAPI backend, which also serves the built frontend, and shows
// it in a window. The backend is stopped when the app quits.
import { app, BrowserWindow, dialog, session, shell, systemPreferences } from 'electron'
import { type ChildProcess, spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { createServer } from 'node:net'
import { homedir } from 'node:os'
import { delimiter, join } from 'node:path'

// Installing the Python dependencies on the first launch can take a few minutes.
const STARTUP_TIMEOUT_MS = 10 * 60 * 1000

let backend: ChildProcess | null = null
let backendLog = ''
let window: BrowserWindow | null = null
let quitting = false

function paths() {
  if (!app.isPackaged) {
    const root = join(__dirname, '..', '..')
    return { backend: join(root, 'backend'), frontend: join(root, 'frontend', 'dist'), data: null }
  }
  return {
    backend: join(process.resourcesPath, 'backend'),
    frontend: join(process.resourcesPath, 'frontend'),
    // The app bundle is read-only, so the packaged app keeps its files in the user's profile.
    data: join(app.getPath('userData'), 'data'),
  }
}

// Apps opened from Finder do not get the shell's PATH, so look where uv usually lives.
function findUv(): string | null {
  const name = process.platform === 'win32' ? 'uv.exe' : 'uv'
  const folders = [
    ...(process.env.PATH ?? '').split(delimiter),
    join(homedir(), '.local', 'bin'),
    join(homedir(), '.cargo', 'bin'),
    '/opt/homebrew/bin',
    '/usr/local/bin',
  ]
  return folders.map((folder) => join(folder, name)).find((file) => existsSync(file)) ?? null
}

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer()
    server.once('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const address = server.address()
      server.close(() => (address && typeof address === 'object' ? resolve(address.port) : reject(new Error('No free port'))))
    })
  })
}

function startBackend(uv: string, port: number) {
  const { backend: project, frontend, data } = paths()
  const env: NodeJS.ProcessEnv = {
    ...process.env,
    SOS_MY_INTERVIEW_FRONTEND_DIST: frontend,
    // Keep Python from writing bytecode into the app bundle.
    PYTHONDONTWRITEBYTECODE: '1',
  }
  const args = ['run', '--project', project]
  if (data) {
    env.SOS_MY_INTERVIEW_DATA_DIR = data
    env.UV_PROJECT_ENVIRONMENT = join(app.getPath('userData'), 'venv')
    args.push('--frozen')
  }
  args.push('uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port))

  // Its own process group, so quitting can stop uv together with the Python server it runs.
  const child = spawn(uv, args, { cwd: project, env, detached: process.platform !== 'win32' })
  const keep = (chunk: Buffer) => {
    backendLog = (backendLog + chunk.toString()).slice(-4000)
  }
  child.stdout?.on('data', keep)
  child.stderr?.on('data', keep)
  child.on('exit', (code) => {
    backend = null
    if (quitting) return
    dialog.showErrorBox('The interview server stopped', `Exit code ${code}.\n\n${backendLog}`)
    app.quit()
  })
  backend = child
}

function stopBackend() {
  const child = backend
  backend = null
  if (!child?.pid) return
  try {
    if (process.platform === 'win32') child.kill()
    else process.kill(-child.pid, 'SIGTERM')
  } catch {
    // Already gone.
  }
}

async function waitForBackend(url: string) {
  const deadline = Date.now() + STARTUP_TIMEOUT_MS
  while (Date.now() < deadline) {
    if (!backend) throw new Error('The server exited while starting.')
    try {
      if ((await fetch(`${url}/api/health`)).ok) return
    } catch {
      // Not listening yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 300))
  }
  throw new Error('The server did not start in time.')
}

const SPLASH = `data:text/html;charset=utf-8,${encodeURIComponent(`<!doctype html>
<body style="margin:0;height:100vh;display:grid;place-items:center;font:16px system-ui;color:#555;background:#f4f4f5">
<div style="text-align:center"><p style="font-size:20px;color:#222">SOS My Interview</p>
<p>Starting… the first launch sets things up and can take a few minutes.</p></div></body>`)}`

async function main() {
  const uv = findUv()
  if (!uv) {
    dialog.showErrorBox('uv is required', 'Install uv (https://docs.astral.sh/uv/) and open the app again.')
    return app.quit()
  }

  // The page records answers with the webcam and microphone.
  session.defaultSession.setPermissionRequestHandler((_contents, permission, allow) => allow(permission === 'media'))
  if (process.platform === 'darwin') {
    // macOS asks once; startup does not wait for the answer.
    void systemPreferences
      .askForMediaAccess('microphone')
      .then(() => systemPreferences.askForMediaAccess('camera'))
  }

  window = new BrowserWindow({ width: 1280, height: 860, minWidth: 800, minHeight: 600, title: 'SOS My Interview' })
  window.on('closed', () => (window = null))
  // Links to job postings open in the regular browser, not inside the app.
  window.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/.test(url)) shell.openExternal(url)
    return { action: 'deny' }
  })
  await window.loadURL(SPLASH)

  const port = await freePort()
  const url = `http://127.0.0.1:${port}`
  startBackend(uv, port)
  try {
    await waitForBackend(url)
  } catch (e) {
    if (quitting) return
    quitting = true
    stopBackend()
    dialog.showErrorBox('Could not start the interview server', `${(e as Error).message}\n\n${backendLog}`)
    return app.quit()
  }
  await window?.loadURL(url)
}

if (!app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (window?.isMinimized()) window.restore()
    window?.focus()
  })
  app.on('window-all-closed', () => app.quit())
  app.on('before-quit', () => {
    quitting = true
    stopBackend()
  })
  app.whenReady().then(main)
}
