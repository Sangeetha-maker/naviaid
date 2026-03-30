import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { searchOpportunities, type Opportunity, type SearchParams } from '../lib/api'
import RecoCard from '../components/RecoCard'
import VoiceInput from '../components/VoiceInput'
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon, XMarkIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

const CATEGORIES = ['', 'scholarship', 'job', 'health', 'loan', 'housing', 'agriculture', 'skill_training']

export default function Search() {
  const { t } = useTranslation()
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [results, setResults] = useState<Opportunity[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(false)
  const [showVoice, setShowVoice] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  const doSearch = useCallback(async (params: SearchParams) => {
    setLoading(true)
    try {
      const res = await searchOpportunities({ limit: 12, ...params })
      setResults(res.items)
      setTotal(res.total)
      setPage(res.page)
      setPages(res.pages)
    } catch {
      setResults([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    doSearch({ q: query || undefined, category: category || undefined, page })
  }, [doSearch, page])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    doSearch({ q: query || undefined, category: category || undefined, page: 1 })
  }

  const handleVoice = (text: string) => {
    setQuery(text)
    setShowVoice(false)
    setPage(1)
    doSearch({ q: text || undefined, category: category || undefined, page: 1 })
  }

  return (
    <div className="pb-24 md:pb-8 pt-6 md:pt-20 px-4 md:px-8 max-w-6xl mx-auto">
      <h1 className="text-2xl md:text-3xl font-bold text-white mb-6">{t('search')}</h1>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            className="input pl-10 pr-4"
            placeholder={t('search_placeholder')}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search"
          />
        </div>
        <button
          type="button"
          onClick={() => setShowVoice((v) => !v)}
          aria-label={t('voice_search')}
          className={clsx('btn btn-ghost px-3', showVoice && 'bg-blue-600/20 text-blue-400')}
        >
          🎤
        </button>
        <button
          type="button"
          onClick={() => setShowFilters((v) => !v)}
          className={clsx('btn btn-ghost px-3', showFilters && 'bg-blue-600/20 text-blue-400')}
          aria-label="Toggle filters"
        >
          <AdjustmentsHorizontalIcon className="w-5 h-5" />
        </button>
        <button type="submit" className="btn-primary px-6">Search</button>
      </form>

      {/* Voice panel */}
      {showVoice && (
        <div className="mb-4 p-4 bg-slate-800/60 rounded-2xl border border-slate-700/50 flex flex-col items-center gap-3">
          <VoiceInput onTranscript={handleVoice} />
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <div className="mb-4 p-4 bg-slate-800/60 rounded-2xl border border-slate-700/50">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-slate-300">{t('filters')}</span>
            <button onClick={() => { setCategory(''); setShowFilters(false) }}
              className="text-xs text-slate-500 hover:text-slate-300">
              <XMarkIcon className="w-4 h-4 inline" /> {t('clear_filters')}
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => (
              <button key={cat}
                onClick={() => setCategory(cat)}
                className={clsx('px-3 py-1.5 rounded-xl text-sm border transition-colors',
                  category === cat
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-blue-500')}
              >
                {cat ? t(cat) : 'All'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Results header */}
      {!loading && (
        <p className="text-sm text-slate-400 mb-4">
          {total} {t('results')} {query && `for "${query}"`}
        </p>
      )}

      {/* Grid */}
      {loading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1,2,3,4,5,6].map((i) => <div key={i} className="skeleton h-52 rounded-2xl" />)}
        </div>
      ) : results.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">🔍</p>
          <p className="text-slate-400">{t('no_results')}</p>
        </div>
      ) : (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((opp) => <RecoCard key={opp.id} opp={opp} />)}
          </div>
          {pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {Array.from({ length: pages }, (_, i) => i + 1).map((p) => (
                <button key={p}
                  onClick={() => setPage(p)}
                  className={clsx('w-9 h-9 rounded-lg text-sm font-medium transition-colors',
                    page === p ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700')}
                >{p}</button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
