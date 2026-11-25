import { locale } from './i18n'

// Formatting for saved-attempt timestamps (stored in UTC, shown in local time, in the user's language).

/** Local calendar day, e.g. "2026-11-20", used to group attempts by date. */
export function dayKey(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

export const formatDay = (iso: string) =>
  new Date(iso).toLocaleDateString(locale(), { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' })

export const formatTime = (iso: string) =>
  new Date(iso).toLocaleTimeString(locale(), { hour: '2-digit', minute: '2-digit' })
