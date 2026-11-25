import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { LANGUAGES, useSettingsStore } from '../stores/settings'
import { locale, modelName, PAGE_LANGUAGES, t, voiceLabel } from './index'

beforeEach(() => setActivePinia(createPinia()))

const yours = (language: string) => (useSettingsStore().feedbackLanguage = language)

describe('the texts of the pages', () => {
  it('are in English until the user has another language', () => {
    expect(t('nav.history')).toBe('History')
  })

  it("are in the user's language when the pages are written in it", () => {
    yours('Korean')
    expect(t('nav.history')).toBe('기록')
  })

  it("are written in every language a user's own can be", () => {
    expect(PAGE_LANGUAGES).toEqual(LANGUAGES.map((l) => l.name))
    yours('Japanese')
    expect(t('nav.history')).not.toBe('History')
  })

  it('are in English for a language the pages are not written in', () => {
    yours('Esperanto')
    expect(t('nav.history')).toBe('History')
  })

  it('have their names filled in', () => {
    expect(t('interview.followUp', { n: 1, total: 2 })).toBe('Follow-up 1 / 2')
    yours('Korean')
    expect(t('interview.followUp', { n: 1, total: 2 })).toBe('꼬리 질문 1 / 2')
  })

  it('say one or many by the number', () => {
    expect(t('questions.attempts', { n: 1 })).toBe('1 attempt')
    expect(t('questions.attempts', { n: 3 })).toBe('3 attempts')
    yours('Korean')
    expect(t('questions.attempts', { n: 1 })).toBe('1번 답함')
    expect(t('questions.attempts', { n: 3 })).toBe('3번 답함')
  })

  it('name the speech models', () => {
    expect(modelName('voice', 'Interviewer’s voice')).toBe("Interviewer's voice")
    yours('Korean')
    expect(modelName('speech-to-text', 'Speech recognition')).toBe('음성 인식')
    // One the pages do not know yet keeps the name the backend gave it.
    expect(modelName('translation', 'Translation')).toBe('Translation')
  })

  it('say what a voice is like, and leave its name', () => {
    expect(voiceLabel('Emma · British · female')).toBe('Emma · British · female')
    yours('Korean')
    expect(voiceLabel('Emma · British · female')).toBe('Emma · 영국식 · 여성')
    expect(voiceLabel('Nova · Australian')).toBe('Nova · Australian')
  })
})

describe('the language dates are written in', () => {
  it("is the user's", () => {
    expect(locale()).toBe('en')
    yours('Korean')
    expect(locale()).toBe('ko')
    yours('Traditional Chinese')
    expect(locale()).toBe('zh-TW')
  })

  it('is English for a language that is not listed', () => {
    yours('Esperanto')
    expect(locale()).toBe('en')
  })
})
