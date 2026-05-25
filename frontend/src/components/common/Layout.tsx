import type { ReactNode } from 'react'

interface LayoutProps {
  left: ReactNode
  center: ReactNode
  right: ReactNode
}

const Layout = ({ left, center, right }: LayoutProps) => {
  return (
    <div className="app-shell">
      <aside className="app-shell__left">{left}</aside>
      <main className="app-shell__center">{center}</main>
      <aside className="app-shell__right">{right}</aside>
    </div>
  )
}

export default Layout
