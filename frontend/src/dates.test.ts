import { describe, expect, it } from 'vitest'
import { dayKey } from './dates'

// Built from local-time parts, so the tests hold in any time zone.
const iso = (...parts: [number, number, number, number, number]) => new Date(...parts).toISOString()

describe('dayKey', () => {
  it('is the local calendar day, zero-padded', () => {
    expect(dayKey(iso(2026, 0, 5, 9, 0))).toBe('2026-01-05')
  })

  it('groups a late-night and an early-morning attempt on their own local days', () => {
    expect(dayKey(iso(2026, 10, 20, 23, 59))).toBe('2026-11-20')
    expect(dayKey(iso(2026, 10, 21, 0, 1))).toBe('2026-11-21')
  })
})
