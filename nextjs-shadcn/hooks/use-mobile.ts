import { useCallback, useSyncExternalStore } from "react"

const MOBILE_BREAKPOINT = 768

function isMobileWidth() {
  return window.innerWidth < MOBILE_BREAKPOINT
}

export function useIsMobile() {
  const subscribe = useCallback(
    (callback: () => void) => {
      const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
      mql.addEventListener("change", callback)
      return () => mql.removeEventListener("change", callback)
    },
    []
  )
  // useSyncExternalStore 替代 effect + setState，避免级联渲染
  return useSyncExternalStore(subscribe, isMobileWidth, () => false)
}
