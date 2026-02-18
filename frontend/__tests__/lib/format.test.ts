import { describe, it, expect } from 'vitest'
import { formatFileSize, formatDate } from '@/lib/format'

describe('formatFileSize', () => {
  it('formats bytes correctly', () => {
    expect(formatFileSize(0)).toBe('0 B')
    expect(formatFileSize(500)).toBe('500.0 B')
    expect(formatFileSize(1024)).toBe('1.0 KB')
    expect(formatFileSize(1536)).toBe('1.5 KB')
    expect(formatFileSize(1048576)).toBe('1.0 MB')
    expect(formatFileSize(1073741824)).toBe('1.0 GB')
  })
})

describe('formatDate', () => {
  it('formats date strings', () => {
    const result = formatDate('2024-01-15T10:30:00Z')
    expect(result).toContain('2024')
    expect(result).toContain('Jan')
  })
})
