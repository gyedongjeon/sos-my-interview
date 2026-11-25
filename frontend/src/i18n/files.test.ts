import { describe, expect, it } from 'vitest'
import en from './en'

// Every file of texts next to this one, by its name: the pages in a language (`ko.ts`).
const pages = import.meta.glob<Record<string, string>>(['./*.ts', '!./en.ts', '!./index.ts', '!./*.test.ts'], {
  eager: true,
  import: 'default',
})

const keys = Object.keys(en) as (keyof typeof en)[]
const names = (text: string) => new Set([...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]))

describe.each(Object.entries(pages))('the texts of the pages in %s', (_file, texts) => {
  it('have every text', () => {
    expect(Object.keys(texts).sort()).toEqual([...keys].sort())
    for (const key of keys) expect(texts[key].trim(), key).not.toBe('')
  })

  it('have the same names to fill in, in each form', () => {
    for (const key of keys) {
      for (const form of texts[key].split(' | ')) expect(names(form), key).toEqual(names(en[key]))
    }
  })

  it('say one and many only where English does', () => {
    for (const key of keys) {
      expect(texts[key].split(' | ').length, key).toBeLessThanOrEqual(en[key].split(' | ').length)
    }
  })

  it('keep the dot that joins a text to the one before it', () => {
    for (const key of keys) {
      if (en[key].startsWith(' · ')) expect(texts[key].startsWith(' · '), key).toBe(true)
    }
  })
})
