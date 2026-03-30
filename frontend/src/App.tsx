import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import { useUserStore } from './stores/userStore'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Onboard from './pages/Onboard'
import Dashboard from './pages/Dashboard'
import Search from './pages/Search'
import Profile from './pages/Profile'

// Guard: requires auth
function RequireAuth() {
  const { token } = useUserStore()
  if (!token) return <Navigate to="/login" replace />
  return <Outlet />
}

// Layout – adds navbar and font scale
function Layout() {
  const { highContrast, fontScale } = useUserStore()
  useEffect(() => {
    document.documentElement.style.fontSize = `${fontScale * 16}px`
    document.body.classList.toggle('high-contrast', highContrast)
  }, [highContrast, fontScale])
  return (
    <div>
      <Navbar />
      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Root layout */}
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/search" element={<Search />} />

          {/* Auth-protected */}
          <Route element={<RequireAuth />}>
            <Route path="/onboard" element={<Onboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
