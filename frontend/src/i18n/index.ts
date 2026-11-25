import { getActivePinia } from 'pinia'
import { LANGUAGES, useSettingsStore } from '../stores/settings'
import bn from './bn'
import de from './de'
import en from './en'
import es from './es'
import fr from './fr'
import hi from './hi'
import id from './id'
import it from './it'
import ja from './ja'
import ko from './ko'
import pl from './pl'
import pt from './pt'
import ru from './ru'
import th from './th'
import tr from './tr'
import uk from './uk'
import vi from './vi'
import zhHans from './zh-Hans'
import zhHant from './zh-Hant'

/** A text of the pages, by its key in `en.ts`. */
export type MessageKey = keyof typeof en

// The languages the pages are written in, by the name the user's language is saved under (see
// LANGUAGES in the settings store): every one of them. A language without a file here would be
// shown the English pages. To add one, write a file like `ko.ts` and list it here.
const MESSAGES: Record<string, Record<MessageKey, string>> = {
  English: en,
  Korean: ko,
  Japanese: ja,
  'Simplified Chinese': zhHans,
  'Traditional Chinese': zhHant,
  Spanish: es,
  French: fr,
  German: de,
  Portuguese: pt,
  Italian: it,
  Polish: pl,
  Russian: ru,
  Ukrainian: uk,
  Turkish: tr,
  Vietnamese: vi,
  Indonesian: id,
  Thai: th,
  Hindi: hi,
  Bengali: bn,
}

/** The names of the user's languages the pages are written in. */
export const PAGE_LANGUAGES = Object.keys(MESSAGES)

// Read while a page is drawn, so the page is drawn again when the user's language changes.
// English where there is no store to ask (a function used on its own, as in a test).
const language = () => (getActivePinia() ? useSettingsStore().feedbackLanguage : 'English')

/**
 * A text of the pages in the user's language, with `{name}` filled in from `values`. A text
 * written as "one | many" is chosen by `values.n`.
 */
export function t(key: MessageKey, values: Record<string, string | number> = {}): string {
  let text = (MESSAGES[language()] ?? en)[key] ?? en[key]
  const forms = text.split(' | ')
  if (forms.length === 2) text = forms[values.n === 1 ? 0 : 1]
  return text.replace(/\{(\w+)\}/g, (whole, name: string) => (name in values ? String(values[name]) : whole))
}

/** The BCP 47 tag dates and times are written in: the user's language, else English. */
export function locale(): string {
  return LANGUAGES.find((l) => l.name === language())?.locale ?? 'en'
}

/** A speech model by its id, named in the user's language. */
export function modelName(id: string, fallback: string): string {
  const key = `models.${id}`
  return key in en ? t(key as MessageKey) : fallback
}

/** A voice's label ("Emma · British · female"): its name as it is, and what is said of it in the
 * user's language. */
export function voiceLabel(label: string): string {
  return label
    .split(' · ')
    .map((part, i) => {
      const key = `voice.${part}`
      return i > 0 && key in en ? t(key as MessageKey) : part
    })
    .join(' · ')
}
