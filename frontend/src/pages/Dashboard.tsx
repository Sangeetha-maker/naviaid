import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'
import { useRecommendations } from '../hooks/useRecommendations'
import { fetchSaved, fetchRecent, triggerSync } from '../lib/api'
import RecoCard from '../components/RecoCard'
import type { Opportunity } from '../lib/api'
import { ArrowPathIcon, SparklesIcon } from '@heroicons/react/24/outline'

type Tab = 'reco' | 'saved' | 'recent'

export default function Dashboard() {
  const { t } = useTranslation()
  const { user } = useUserStore()
  const { data: recos, loading: recoLoading, error: recoError, refetch } = useRecommendations()
  const [savedOpps, setSavedOpps] = useState<Opportunity[]>([])
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set())
  const [recentOpps, setRecentOpps] = useState<Opportunity[]>([])
  const [savedLoading, setSavedLoading] = useState(false)
  const [recentLoading, setRecentLoading] = useState(false)
  const [tab, setTab] = useState<Tab>('reco')
  const [syncing, setSyncing] = useState(false)
  const [syncResult, setSyncResult] = useState<{ total_synced: number } | null>(null)
  const isAdmin = user?.role === 'admin'

  useEffect(() => {
    // Always fetch saved on mount and tab switch to keep state fresh
    if (tab === 'saved') setSavedLoading(true)
    fetchSaved()
      .then((d) => {
        setSavedOpps(d)
        setSavedIds(new Set(d.map(o => o.id)))
      })
      .catch(() => {})
      .finally(() => { if (tab === 'saved') setSavedLoading(false) })
    if (tab === 'recent') {
      setRecentLoading(true)
      fetchRecent(12)
        .then((d) => setRecentOpps(d))
        .catch(() => {})
        .finally(() => setRecentLoading(false))
    }
  }, [tab])

  const handleSync = async () => {
    setSyncing(true)
    setSyncResult(null)
    try {
      const res = await triggerSync()
      setSyncResult(res)
      // Refresh recent tab after sync
      if (tab === 'recent') {
        setRecentLoading(true)
        fetchRecent(12).then(setRecentOpps).finally(() => setRecentLoading(false))
      }
    } catch (e) {
      // ignore – likely not admin
    } finally {
      setSyncing(false)
    }
  }

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const currentData = tab === 'reco' ? recos : tab === 'saved' ? savedOpps : recentOpps
  const isLoading = tab === 'reco' ? recoLoading : tab === 'saved' ? savedLoading : recentLoading
  const currentError = tab === 'reco' ? recoError : null

  return (
    <div className="pb-24 md:pb-8 pt-6 md:pt-20 px-4 md:px-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            {greeting()}{user?.name ? `, ${user.name.split(' ')[0]}` : ''} 👋
          </h1>
          <p className="text-slate-400 mt-1 text-sm md:text-base">
            {t('my_recommendations')} — personalised for you
          </p>
        </div>

        {/* Sync button – visible to all, only works for admin */}
        <button
          onClick={handleSync}
          disabled={syncing}
          title={isAdmin ? 'Sync live data from external APIs' : 'Admin-only feature'}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all border ${
            isAdmin
              ? 'border-blue-500/40 bg-blue-600/20 text-blue-300 hover:bg-blue-600/40'
              : 'border-slate-700 bg-slate-800/50 text-slate-500 cursor-not-allowed'
          }`}
        >
          {syncing ? (
            <ArrowPathIcon className="w-4 h-4 animate-spin" />
          ) : (
            <SparklesIcon className="w-4 h-4" />
          )}
          {syncing ? 'Syncing…' : '🔄 Sync Live Data'}
        </button>
      </div>

      {/* Sync result banner */}
      {syncResult && (
        <div className="mb-4 px-4 py-3 rounded-xl bg-green-500/10 border border-green-500/30 text-green-400 text-sm">
          ✅ Sync complete — <strong>{syncResult.total_synced}</strong> new opportunities added from live sources!
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-3 md:grid-cols-3 gap-3 mb-8">
        {[
          { label: 'Schemes found', value: recos.length, color: 'from-blue-600 to-indigo-600' },
          { label: t('saved'), value: savedOpps.length || '—', color: 'from-yellow-500 to-orange-500' },
          { label: t('applied'), value: '—', color: 'from-green-500 to-emerald-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card text-center">
            <div className={`text-2xl font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>{value}</div>
            <div className="text-xs text-slate-400 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-800/50 p-1 rounded-xl w-fit mb-6 flex-wrap">
        {([
          ['reco', t('my_recommendations')],
          ['saved', t('saved')],
          ['recent', '🆕 Recently Added'],
        ] as const).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              tab === key
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1,2,3,4,5,6].map((i) => (
            <div key={i} className="skeleton h-52 rounded-2xl" />
          ))}
        </div>
      )}

      {!isLoading && currentError && (
        <div className="text-center py-16">
          <p className="text-red-400 mb-4">{t('error_load')}</p>
          <button onClick={refetch} className="btn-primary">
            <ArrowPathIcon className="w-4 h-4" /> {t('retry')}
          </button>
        </div>
      )}

      {!isLoading && !currentError && currentData.length === 0 && (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">{tab === 'recent' ? '🌐' : '🔍'}</p>
          <p className="text-slate-400">
            {tab === 'recent'
              ? isAdmin
                ? 'No live data yet. Click "🔄 Sync Live Data" to fetch from JSearch, Adzuna & MyScheme!'
                : 'No recently added opportunities yet.'
              : t('no_results')}
          </p>
        </div>
      )}

      {!isLoading && !currentError && currentData.length > 0 && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {currentData.map((opp) => (
            <RecoCard 
              key={opp.id} 
              opp={opp} 
              initialSaved={savedIds.has(opp.id)} 
            />
          ))}
        </div>
      )}
    </div>
  )
}
