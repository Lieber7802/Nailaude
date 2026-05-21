import { useState, useCallback } from 'react'

export function useStreamMessage() {
  const [content, setContent] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  const startStream = useCallback(() => {
    setContent('')
    setIsStreaming(true)
  }, [])

  const appendDelta = useCallback((delta: string) => {
    setContent((prev) => prev + delta)
  }, [])

  const endStream = useCallback(() => {
    setIsStreaming(false)
  }, [])

  return { content, isStreaming, startStream, appendDelta, endStream }
}
