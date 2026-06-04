import { MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons'
import type { CSSProperties, PointerEvent, ReactNode } from 'react'
import { useUIStore } from '../../stores/uiStore'

interface LayoutProps {
  left: ReactNode
  center: ReactNode
  right: ReactNode
}

const Layout = ({ left, center, right }: LayoutProps) => {
  const sidebarVisible = useUIStore((state) => state.sidebarVisible)
  const previewVisible = useUIStore((state) => state.previewVisible)
  const leftPaneWidth = useUIStore((state) => state.leftPaneWidth)
  const rightPaneWidth = useUIStore((state) => state.rightPaneWidth)
  const setLeftPaneWidth = useUIStore((state) => state.setLeftPaneWidth)
  const setRightPaneWidth = useUIStore((state) => state.setRightPaneWidth)
  const setSidebarVisible = useUIStore((state) => state.setSidebarVisible)
  const setPreviewVisible = useUIStore((state) => state.setPreviewVisible)
  const style = {
    '--left-pane-track': sidebarVisible ? `${leftPaneWidth}px` : '0px',
    '--left-resize-track': sidebarVisible ? '7px' : '0px',
    '--right-pane-track': previewVisible ? `${rightPaneWidth}px` : '0px',
    '--right-resize-track': previewVisible ? '7px' : '0px',
  } as CSSProperties

  const startResize = (pane: 'left' | 'right') => (event: PointerEvent<HTMLButtonElement>) => {
    event.preventDefault()
    const handlePointerMove = (moveEvent: globalThis.PointerEvent) => {
      if (pane === 'left') {
        setLeftPaneWidth(moveEvent.clientX)
        return
      }
      setRightPaneWidth(window.innerWidth - moveEvent.clientX)
    }
    const stopResize = () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', stopResize)
      document.body.classList.remove('is-resizing-pane')
    }

    document.body.classList.add('is-resizing-pane')
    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', stopResize)
  }

  return (
    <div className="app-shell" style={style}>
      <aside className="app-shell__left" aria-hidden={!sidebarVisible}>
        {left}
      </aside>
      <button
        aria-label="调整左侧会话列表宽度"
        className="app-shell__resize app-shell__resize--left"
        type="button"
        onPointerDown={startResize('left')}
      />
      <main className="app-shell__center">{center}</main>
      <button
        aria-label="调整右侧预览窗格宽度"
        className="app-shell__resize app-shell__resize--right"
        type="button"
        onPointerDown={startResize('right')}
      />
      <aside className="app-shell__right" aria-hidden={!previewVisible}>
        {right}
      </aside>
      {!sidebarVisible && (
        <div className="pane-restore-zone pane-restore-zone--left">
          <button
            aria-label="显示会话列表"
            className="pane-restore pane-restore--left"
            title="显示会话列表"
            type="button"
            onClick={() => setSidebarVisible(true)}
          >
            <MenuUnfoldOutlined />
          </button>
        </div>
      )}
      {!previewVisible && (
        <div className="pane-restore-zone pane-restore-zone--right">
          <button
            aria-label="显示预览窗格"
            className="pane-restore pane-restore--right"
            title="显示预览窗格"
            type="button"
            onClick={() => setPreviewVisible(true)}
          >
            <MenuFoldOutlined />
          </button>
        </div>
      )}
    </div>
  )
}

export default Layout
