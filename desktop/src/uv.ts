// Finding the `uv` program that runs the Python backend.
import { delimiter, join } from 'node:path'

export interface UvLookup {
  /** The PATH environment variable. */
  path: string | undefined
  home: string
  platform: NodeJS.Platform
  exists: (file: string) => boolean
}

/** Apps opened from Finder do not get the shell's PATH, so also look where uv usually lives. */
export function findUv({ path, home, platform, exists }: UvLookup): string | null {
  const name = platform === 'win32' ? 'uv.exe' : 'uv'
  const folders = [
    ...(path ?? '').split(delimiter),
    join(home, '.local', 'bin'),
    join(home, '.cargo', 'bin'),
    '/opt/homebrew/bin',
    '/usr/local/bin',
  ]
  return folders.map((folder) => join(folder, name)).find(exists) ?? null
}
