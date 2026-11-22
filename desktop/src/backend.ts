// How the Python backend is started: the arguments for uv and the environment it runs in.
import { join } from 'node:path'

export interface BackendOptions {
  /** The folder with the backend's pyproject.toml. */
  project: string
  /** The built frontend the backend serves. */
  frontend: string
  /** The packaged app's own folder in the user's profile; null when running from a checkout. */
  userData: string | null
  port: number
  env: NodeJS.ProcessEnv
  /** The Python shipped inside the app, where there is one; otherwise uv downloads it. */
  python?: string | null
}

export function backendLaunch({ project, frontend, userData, port, env, python }: BackendOptions) {
  const launchEnv: NodeJS.ProcessEnv = {
    ...env,
    SOS_MY_INTERVIEW_FRONTEND_DIST: frontend,
    // Keep Python from writing bytecode into the app bundle.
    PYTHONDONTWRITEBYTECODE: '1',
  }
  if (python) {
    // Shipped with the Windows app: in the sister app's Windows trial, downloading Python from
    // inside the app stalled every time.
    launchEnv.UV_PYTHON = python
    launchEnv.UV_PYTHON_DOWNLOADS = 'never'
  }
  const args = ['run', '--project', project]
  if (userData) {
    // The app bundle is read-only, so the packaged app keeps its files in the user's profile.
    launchEnv.SOS_MY_INTERVIEW_DATA_DIR = join(userData, 'data')
    launchEnv.UV_PROJECT_ENVIRONMENT = join(userData, 'venv')
    // uv's download cache and the Python it installs would otherwise go to shared folders in
    // the home folder; here, removing the app's folder removes everything the app put on disk.
    launchEnv.UV_CACHE_DIR = join(userData, 'uv-cache')
    launchEnv.UV_PYTHON_INSTALL_DIR = join(userData, 'python')
    // The packaged app needs only what runs the server, not the test tools.
    args.push('--frozen', '--no-dev')
  }
  args.push('uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port))
  return { args, env: launchEnv }
}

/**
 * The command that stops the backend, where one is needed. On Windows uv starts the Python
 * server as a process of its own and ending uv leaves it running, so the whole tree is ended.
 * Elsewhere the backend runs in its own process group, which is signalled instead.
 */
export function stopCommand(platform: NodeJS.Platform, pid: number): { command: string; args: string[] } | null {
  return platform === 'win32' ? { command: 'taskkill', args: ['/pid', String(pid), '/T', '/F'] } : null
}
