import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'
import {
  HomeIcon,
  MagnifyingGlassIcon,
  Squares2X2Icon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  LanguageIcon,
} from '@heroicons/react/24/outline'
import i18n from '../i18n'
import clsx from 'clsx'

const links = [
  { to: '/dashboard', labelKey: 'dashboard', Icon: Squares2X2Icon },
  { to: '/search', labelKey: 'search', Icon: MagnifyingGlassIcon },
  { to: '/profile', labelKey: 'profile', Icon: UserIcon },
]

export default function Navbar() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, lang, setLang, highContrast, toggleHighContrast, logout } = useUserStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleLang = () => {
    const next = lang === 'en' ? 'ta' : 'en'
    setLang(next)
    i18n.changeLanguage(next)
  }

  return (
    <>
      {/* Top bar – desktop */}
      <nav
        className="hidden md:flex fixed top-0 left-0 right-0 h-16 bg-slate-900/95 backdrop-blur border-b border-slate-700/50 z-50 items-center px-6 gap-4"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 mr-6 select-none" aria-label="NaviAid home">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
            <span className="text-white font-bold text-sm">N</span>
          </div>
          <span className="font-bold text-lg text-white tracking-tight">NaviAid</span>
        </Link>

        {/* Links */}
        <div className="flex gap-1 flex-1">
          {links.map(({ to, labelKey, Icon }) => (
            <Link
              key={to}
              to={to}
              className={clsx(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                location.pathname.startsWith(to)
                  ? 'bg-blue-600/20 text-blue-400'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              )}
            >
              <Icon className="w-4 h-4" />
              {t(labelKey)}
            </Link>
          ))}
          {user?.role === 'admin' && (
            <Link
              to="/admin"
              className={clsx(
                'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                location.pathname.startsWith('/admin')
                  ? 'bg-orange-600/20 text-orange-400'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              )}
            >
              <Cog6ToothIcon className="w-4 h-4" />
              {t('admin')}
            </Link>
          )}
        </div>

        {/* Utility buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleLang}
            title="Toggle language"
            aria-label="Toggle language"
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <LanguageIcon className="w-5 h-5" />
          </button>
          <button
            onClick={toggleHighContrast}
            title={highContrast ? 'Normal contrast' : 'High contrast'}
            aria-label="Toggle contrast"
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            {highContrast ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
          </button>
          {user ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-red-400 hover:bg-red-900/20 transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-4 h-4" />
              {t('logout')}
            </button>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors"
            >
              {t('login')}
            </Link>
          )}
        </div>
      </nav>

      {/* Bottom tab bar – mobile */}
      <nav
        className="md:hidden fixed bottom-0 left-0 right-0 bg-slate-900/95 backdrop-blur border-t border-slate-700/50 z-50"
        aria-label="Mobile navigation"
      >
        <div className="flex justify-around py-2">
          <Link
            to="/"
            className={clsx(
              'flex flex-col items-center gap-0.5 px-4 py-2 rounded-xl transition-colors text-xs',
              location.pathname === '/'
                ? 'text-blue-400'
                : 'text-slate-500 hover:text-slate-300'
            )}
          >
            <HomeIcon className="w-6 h-6" />
            {t('home')}
          </Link>
          {links.map(({ to, labelKey, Icon }) => (
            <Link
              key={to}
              to={to}
              className={clsx(
                'flex flex-col items-center gap-0.5 px-4 py-2 rounded-xl transition-colors text-xs',
                location.pathname.startsWith(to)
                  ? 'text-blue-400'
                  : 'text-slate-500 hover:text-slate-300'
              )}
            >
              <Icon className="w-6 h-6" />
              {t(labelKey)}
            </Link>
          ))}
        </div>
      </nav>
    </>
  )
}
