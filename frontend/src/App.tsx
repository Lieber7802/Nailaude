import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Workspace from './pages/Workspace'
import AgentManage from './pages/AgentManage'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/agents" element={<AgentManage />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/" element={<Navigate to="/workspace" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
