/**
 * Diff utility functions
 */
export function parseDiff(_diffText: string) {
  return _diffText
    .split('\n')
    .filter((line) => line.startsWith('@@'))
    .map((line) => ({ content: line }))
}

export function applyDiff(_original: string, _diffText: string): string {
  return _diffText.trim() ? _original : _original
}
