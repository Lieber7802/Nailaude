import { useEffect, useRef } from 'react'

export function useAutoScroll(dependency: unknown) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = containerRef.current
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  }, [dependency])

  return containerRef
}
