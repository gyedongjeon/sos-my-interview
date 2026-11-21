import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const config = JSON.parse(readFileSync(join(__dirname, '..', 'package.json'), 'utf8'))

describe('the packaged backend', () => {
  it('ships the Python version pin, so uv installs the Python the tests ran on', () => {
    const backend = config.build.extraResources.find((entry: { to: string }) => entry.to === 'backend')
    expect(backend.filter).toContain('.python-version')
  })
})
