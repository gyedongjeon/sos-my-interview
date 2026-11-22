// Desktop shell: starts the FastAPI backend, which also serves the built frontend, and shows
// it in a window. The backend is stopped when the app quits.
import { app, BrowserWindow, dialog, Menu, session, shell, systemPreferences } from 'electron'
import { type ChildProcess, spawn } from 'node:child_process'
import { accessSync, constants, existsSync } from 'node:fs'
import { mkdir, rm } from 'node:fs/promises'
import { createServer } from 'node:net'
import { homedir } from 'node:os'
import { join } from 'node:path'
import { backendLaunch, stopCommand } from './backend'
import {
  bundlePath,
  download,
  fetchLatestRelease,
  findUpdate,
  readBundleInfo,
  replaceBlocker,
  swapAfterQuit,
  unpackBundle,
  type Update,
} from './update'
import { findUv } from './uv'

// Installing the Python dependencies on the first launch can take a few minutes.
const STARTUP_TIMEOUT_MS = 10 * 60 * 1000

let backend: ChildProcess | null = null
let backendLog = ''
let window: BrowserWindow | null = null
let quitting = false

function paths() {
  if (!app.isPackaged) {
    const root = join(__dirname, '..', '..')
    return { project: join(root, 'backend'), frontend: join(root, 'frontend', 'dist'), userData: null, python: null }
  }
  return {
    project: join(process.resourcesPath, 'backend'),
    frontend: join(process.resourcesPath, 'frontend'),
    userData: app.getPath('userData'),
    python: shippedPython(),
  }
}

/** The Python inside the packaged app; only the Windows installer ships one. */
function shippedPython(): string | null {
  const python = join(process.resourcesPath, 'python', 'python.exe')
  return existsSync(python) ? python : null
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
  const { project, frontend, userData, python } = paths()
  const { args, env } = backendLaunch({ project, frontend, userData, port, env: process.env, python })

  // Its own process group, so quitting can stop uv together with the Python server it runs.
  const child = spawn(uv, args, { cwd: project, env, detached: process.platform !== 'win32', windowsHide: true })
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
    const stop = stopCommand(process.platform, child.pid)
    if (stop) spawn(stop.command, stop.args, { stdio: 'ignore', windowsHide: true })
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
<body style="margin:0;height:100vh;display:grid;place-items:center;font:16px system-ui;color:#5b6477;background:#fbf8f3">
<div style="text-align:center"><p style="font-size:14px;letter-spacing:4px;color:#f4541d;margin:0">&middot;&middot;&middot; &ndash;&ndash;&ndash; &middot;&middot;&middot;</p>
<p style="font-size:28px;color:#14213d;margin:8px 0"><b style="color:#f4541d">SOS</b> My Interview</p>
<p>Help is on the way… the first launch sets things up and can take a few minutes.</p></div></body>`)}`

// --- Updates --------------------------------------------------------------------------
// The app is not signed with an Apple developer certificate, so the standard updater cannot be
// used. Instead the app looks for a newer GitHub release and, when asked, replaces itself.

let updating = false

function writable(folder: string): boolean {
  try {
    accessSync(folder, constants.W_OK)
    return true
  } catch {
    return false
  }
}

async function ask(message: string, detail: string, buttons: string[]): Promise<number> {
  const options = { type: 'info' as const, message, detail, buttons, defaultId: 0, cancelId: buttons.length - 1 }
  const { response } = window ? await dialog.showMessageBox(window, options) : await dialog.showMessageBox(options)
  return response
}

/** Look for a newer release. `manual` is true when the user asked, so every outcome is reported. */
async function checkForUpdates(manual: boolean) {
  if (updating) return
  let update: Update | null
  try {
    const release = await fetchLatestRelease(fetch, `SOS-My-Interview/${app.getVersion()}`)
    update = findUpdate(release, app.getVersion(), process.arch)
  } catch (e) {
    // Offline or rate-limited: say so only when the user asked.
    if (manual) await ask('Could not check for updates', (e as Error).message, ['OK'])
    return
  }
  if (!update) {
    if (manual) await ask('You are up to date', `SOS My Interview ${app.getVersion()} is the latest version.`, ['OK'])
    return
  }

  const bundle = bundlePath(app.getPath('exe'))
  // Only the macOS app replaces itself, so elsewhere the reason is given whatever the release holds.
  const blocker =
    update.archive || process.platform !== 'darwin'
      ? replaceBlocker({ packaged: app.isPackaged, platform: process.platform, bundle, writable })
      : 'This release cannot be installed from inside the app.'
  const title = `SOS My Interview ${update.version} is available`
  const have = `You have ${app.getVersion()}.`
  if (blocker || !update.archive || !bundle) {
    const choice = await ask(title, `${have} ${blocker}`, ['Open the Download Page', 'Later'])
    if (choice === 0) void shell.openExternal(update.notesUrl)
    return
  }
  const choice = await ask(
    title,
    `${have} The app will download the new version, replace itself, and open again. Your interviews and settings are kept.`,
    ['Update and Restart', "See What's New", 'Later'],
  )
  if (choice === 1) void shell.openExternal(update.notesUrl)
  if (choice === 0) await installUpdate(update, bundle)
}

async function installUpdate(update: Update, bundle: string) {
  if (!update.archive) return
  updating = true
  const folder = join(app.getPath('userData'), 'updates')
  try {
    await rm(folder, { recursive: true, force: true })
    await mkdir(folder, { recursive: true })
    const zip = join(folder, 'update.zip')
    await download(update.archive, zip, fetch, (fraction) => {
      window?.setProgressBar(fraction)
      window?.setTitle(`SOS My Interview — downloading ${update.version}… ${Math.round(fraction * 100)}%`)
    })
    window?.setTitle(`SOS My Interview — installing ${update.version}…`)
    const installed = await readBundleInfo(bundle)
    const next = await unpackBundle(zip, join(folder, 'unpacked'), { id: installed.id, version: update.version })
    // The swap waits for this process to end, so quitting is what starts it.
    swapAfterQuit(process.pid, bundle, next, join(folder, 'previous.app'), ['/usr/bin/open'])
    app.quit()
  } catch (e) {
    updating = false
    window?.setProgressBar(-1)
    window?.setTitle('SOS My Interview')
    await rm(folder, { recursive: true, force: true })
    const choice = await ask('The update could not be installed', (e as Error).message, ['Open the Download Page', 'Close'])
    if (choice === 0) void shell.openExternal(update.notesUrl)
  }
}

function setMenu() {
  const checkForUpdate = { label: 'Check for Updates…', click: () => void checkForUpdates(true) }
  if (process.platform !== 'darwin') {
    // Windows and Linux have no application menu, so the check sits under Help.
    Menu.setApplicationMenu(
      Menu.buildFromTemplate([
        { label: 'File', submenu: [{ role: 'quit' }] },
        { role: 'editMenu' },
        { role: 'viewMenu' },
        { role: 'windowMenu' },
        { label: 'Help', submenu: [checkForUpdate] },
      ]),
    )
    return
  }
  Menu.setApplicationMenu(
    Menu.buildFromTemplate([
      {
        label: app.name,
        submenu: [
          { role: 'about' },
          checkForUpdate,
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideOthers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' },
        ],
      },
      { role: 'editMenu' },
      { role: 'viewMenu' },
      { role: 'windowMenu' },
    ]),
  )
}

async function main() {
  setMenu()
  // Left over from the update that installed this version.
  void rm(join(app.getPath('userData'), 'updates'), { recursive: true, force: true })
  const uv = findUv({
    path: process.env.PATH,
    home: homedir(),
    platform: process.platform,
    exists: existsSync,
    bundledDir: app.isPackaged ? join(process.resourcesPath, 'uv') : null,
  })
  if (!uv) {
    // Only when running from a checkout: the packaged app ships its own uv.
    dialog.showErrorBox('uv is required', 'Install uv (https://docs.astral.sh/uv/) and open the app again.')
    return app.quit()
  }

  // The packaged app gets its icon from the bundle; from a checkout the Dock would show Electron's.
  if (!app.isPackaged) app.dock?.setIcon(join(__dirname, '..', 'assets', 'icon.png'))

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
  // From a checkout there is nothing to replace, so only the menu item checks there.
  if (app.isPackaged) void checkForUpdates(false)
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
