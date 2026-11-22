import { describe, expect, it } from 'vitest'
import { deviceProblem } from './useCamera'

const failure = (name: string) => Object.assign(new Error('x'), { name })

describe('deviceProblem', () => {
  it('says that no device is connected when none was found', () => {
    expect(deviceProblem('microphone', failure('NotFoundError'))).toBe('No microphone was found.')
    expect(deviceProblem('camera', failure('NotFoundError'))).toBe('No camera was found.')
  })

  it("points at the system's privacy settings when access was refused", () => {
    expect(deviceProblem('microphone', failure('NotAllowedError'))).toBe(
      "Microphone access is turned off. Allow it for this app in your system's privacy settings.",
    )
  })

  it('says another app may hold the device when it cannot be read', () => {
    expect(deviceProblem('camera', failure('NotReadableError'))).toBe(
      'The camera could not be started. Close other apps that use it.',
    )
  })

  it('names any other failure, so it can be reported', () => {
    expect(deviceProblem('microphone', failure('AbortError'))).toBe('The microphone is not available (AbortError).')
    expect(deviceProblem('microphone', 'boom')).toBe('The microphone is not available.')
  })
})
