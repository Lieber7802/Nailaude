import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

const Login = lazy(() => import('./pages/Login'))
const Workspace = lazy(() => import('./pages/Workspace'))
const AgentManage = lazy(() => import('./pages/AgentManage'))
const Settings = lazy(() => import('./pages/Settings'))

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/agents" element={<AgentManage />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/" element={<Navigate to="/workspace" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App
