import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'
import { updateProfile } from '../lib/api'
import { CheckCircleIcon, PencilSquareIcon } from '@heroicons/react/24/outline'
import i18n from '../i18n'

export default function Profile() {
  const { t } = useTranslation()
  const { user, setUser, lang, setLang, highContrast, toggleHighContrast, fontScale, setFontScale } = useUserStore()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    name: user?.name ?? '',
    district: user?.district ?? '',
    annual_income: user?.annual_income?.toString() ?? '',
    education: user?.education ?? '',
    occupation: user?.occupation ?? '',
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await updateProfile({
        ...form,
        annual_income: form.annual_income ? parseInt(form.annual_income) : undefined,
      })
      setUser({ ...user!, ...updated, name: form.name })
      setEditing(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch {
      // handle error
    } finally {
      setSaving(false)
    }
  }

  const toggleLang = () => {
    const next = lang === 'en' ? 'ta' : 'en'
    setLang(next)
    i18n.changeLanguage(next)
  }

  if (!user) return null

  return (
    <div className="pb-24 md:pb-8 pt-6 md:pt-20 px-4 md:px-8 max-w-3xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold text-white mb-6">{t('profile')}</h1>

      {/* Avatar card */}
      <div className="card flex items-center gap-4 mb-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-2xl font-bold text-white shadow-lg shrink-0">
          {user.name?.[0]?.toUpperCase() ?? '?'}
        </div>
        <div>
          <h2 className="font-bold text-lg text-white">{user.name}</h2>
          <p className="text-sm text-slate-400">{user.email}</p>
          <span className="inline-block mt-1 px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-medium">
            {user.role}
          </span>
        </div>
      </div>

      {/* Profile form */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-white">Profile Details</h3>
          <button
            onClick={() => editing ? handleSave() : setEditing(true)}
            className={editing ? 'btn-primary text-sm py-1.5 px-3' : 'btn btn-ghost text-sm'}
          >
            {editing ? (
              saving
                ? <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : <><CheckCircleIcon className="w-4 h-4" /> Save</>
            ) : (
              <><PencilSquareIcon className="w-4 h-4" /> Edit</>
            )}
          </button>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          {[
            { key: 'name', label: t('name'), type: 'text' },
            { key: 'district', label: t('district'), type: 'text' },
            { key: 'annual_income', label: t('annual_income'), type: 'number' },
            { key: 'education', label: t('education'), type: 'text' },
            { key: 'occupation', label: t('occupation'), type: 'text' },
          ].map(({ key, label, type }) => (
            <div key={key}>
              <label className="label">{label}</label>
              {editing ? (
                <input
                  className="input"
                  type={type}
                  value={form[key as keyof typeof form]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                />
              ) : (
                <p className="text-white py-2 px-1 border-b border-slate-700/50">
                  {user[key as keyof typeof user]?.toString() || <span className="text-slate-500">—</span>}
                </p>
              )}
            </div>
          ))}
        </div>

        {saved && (
          <p className="flex items-center gap-2 text-green-400 text-sm mt-4">
            <CheckCircleIcon className="w-4 h-4" /> Profile saved!
          </p>
        )}
      </div>

      {/* Accessibility settings */}
      <div className="card">
        <h3 className="font-semibold text-white mb-4">Accessibility & Preferences</h3>
        <div className="flex flex-col gap-4">
          {/* Language */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">Language</span>
            <button
              onClick={toggleLang}
              className="relative w-24 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center px-1 transition-colors"
            >
              <span className={`absolute left-1 transition-transform duration-200 text-xs font-semibold ${lang === 'ta' ? 'translate-x-14' : ''} bg-blue-600 text-white rounded-full px-2 py-1`}>
                {lang === 'en' ? 'EN' : 'தமிழ்'}
              </span>
            </button>
          </div>

          {/* High contrast */}
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-300">High Contrast (WCAG)</span>
            <button
              onClick={toggleHighContrast}
              role="switch"
              aria-checked={highContrast}
              className={`w-11 h-6 rounded-full transition-colors ${highContrast ? 'bg-blue-600' : 'bg-slate-600'} relative`}
            >
              <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform ${highContrast ? 'translate-x-5' : ''}`} />
            </button>
          </div>

          {/* Font scale */}
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm text-slate-300">Text Size ({Math.round(fontScale * 100)}%)</span>
            <input
              type="range" min="0.8" max="1.5" step="0.1"
              value={fontScale}
              onChange={(e) => setFontScale(parseFloat(e.target.value))}
              className="w-32 accent-blue-500"
              aria-label="Text size"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
