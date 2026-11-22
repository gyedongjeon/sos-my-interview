import { describe, expect, it } from 'vitest'
import { backendLaunch, stopCommand } from '../src/backend'

const options = {
  project: '/App/Resources/backend',
  frontend: '/App/Resources/frontend',
  userData: '/Users/me/Library/Application Support/SOS My Interview' as string | null,
  port: 51234,
  env: { PATH: '/usr/bin', HOME: '/Users/me' },
}

describe('backendLaunch', () => {
  it('runs the server through uv on the given port', () => {
    const { args } = backendLaunch(options)
    expect(args.slice(0, 3)).toEqual(['run', '--project', '/App/Resources/backend'])
    expect(args.slice(-6)).toEqual(['uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '51234'])
  })

  it('keeps the caller environment and tells the backend where the built frontend is', () => {
    const { env } = backendLaunch(options)
    expect(env.PATH).toBe('/usr/bin')
    expect(env.SOS_MY_INTERVIEW_FRONTEND_DIST).toBe('/App/Resources/frontend')
    expect(env.PYTHONDONTWRITEBYTECODE).toBe('1')
  })

  it('keeps the packaged app\'s data and Python packages in its own folder, without the test tools', () => {
    const { args, env } = backendLaunch(options)
    expect(env.SOS_MY_INTERVIEW_DATA_DIR).toBe('/Users/me/Library/Application Support/SOS My Interview/data')
    expect(env.UV_PROJECT_ENVIRONMENT).toBe('/Users/me/Library/Application Support/SOS My Interview/venv')
    expect(args).toContain('--frozen')
    expect(args).toContain('--no-dev')
  })

  it("keeps uv's downloads in the same folder, so removing that folder removes everything", () => {
    const { env } = backendLaunch(options)
    expect(env.UV_CACHE_DIR).toBe('/Users/me/Library/Application Support/SOS My Interview/uv-cache')
    expect(env.UV_PYTHON_INSTALL_DIR).toBe('/Users/me/Library/Application Support/SOS My Interview/python')
  })

  it('leaves the choice of Python to the project, which pins it for every way of running', () => {
    // backend/.python-version is shipped with the app; see tests/package.test.ts.
    expect(backendLaunch(options).args).not.toContain('--python')
  })

  it('leaves a checkout to its own defaults', () => {
    const { args, env } = backendLaunch({ ...options, userData: null })
    expect(env.SOS_MY_INTERVIEW_DATA_DIR).toBeUndefined()
    expect(env.UV_PROJECT_ENVIRONMENT).toBeUndefined()
    expect(env.UV_CACHE_DIR).toBeUndefined()
    expect(env.UV_PYTHON_INSTALL_DIR).toBeUndefined()
    expect(args).not.toContain('--frozen')
    expect(args).not.toContain('--no-dev')
    expect(args).not.toContain('--python')
  })
})

describe('backendLaunch with a Python shipped in the app', () => {
  const python = 'C:\\Programs\\sos\\resources\\python\\python.exe'

  it('runs on that Python and downloads none, so the first launch does not depend on that download', () => {
    const { env } = backendLaunch({ ...options, python })
    expect(env.UV_PYTHON).toBe(python)
    expect(env.UV_PYTHON_DOWNLOADS).toBe('never')
  })

  it('lets uv fetch the pinned Python where none is shipped', () => {
    const { env } = backendLaunch(options)
    expect(env.UV_PYTHON).toBeUndefined()
    expect(env.UV_PYTHON_DOWNLOADS).toBeUndefined()
  })
})

describe('stopCommand', () => {
  it('ends the whole process tree on Windows, where uv and the Python server are separate processes', () => {
    expect(stopCommand('win32', 4321)).toEqual({ command: 'taskkill', args: ['/pid', '4321', '/T', '/F'] })
  })

  it('needs no command elsewhere, where the process group is signalled', () => {
    expect(stopCommand('darwin', 4321)).toBeNull()
    expect(stopCommand('linux', 4321)).toBeNull()
  })
})
