import { describe, expect, it } from 'vitest'
import { backendLaunch } from '../src/backend'

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

  it('leaves a checkout to its own defaults', () => {
    const { args, env } = backendLaunch({ ...options, userData: null })
    expect(env.SOS_MY_INTERVIEW_DATA_DIR).toBeUndefined()
    expect(env.UV_PROJECT_ENVIRONMENT).toBeUndefined()
    expect(args).not.toContain('--frozen')
    expect(args).not.toContain('--no-dev')
  })
})
