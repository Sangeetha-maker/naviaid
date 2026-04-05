import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'
import type { Opportunity } from '../lib/api'
import { saveOpportunity, unsaveOpportunity, markApplied } from '../lib/api'
import {
  BookmarkIcon,
  BookmarkSlashIcon,
  CheckCircleIcon,
  ArrowTopRightOnSquareIcon,
  CalendarIcon,
  CurrencyRupeeIcon,
} from '@heroicons/react/24/outline'
import { BookmarkIcon as BookmarkSolid } from '@heroicons/react/24/solid'
import clsx from 'clsx'

const CATEGORY_COLORS: Record<string, string> = {
  scholarship: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  job: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  health: 'bg-green-500/20 text-green-300 border-green-500/30',
  loan: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  housing: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  agriculture: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  skill_training: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
}

interface RecoCardProps {
  opp: Opportunity
  initialSaved?: boolean
  initialApplied?: boolean
  onApplied?: () => void
}

export default function RecoCard({ opp, initialSaved = false, initialApplied = false, onApplied }: RecoCardProps) {
  const { t } = useTranslation()
  const { lang, token } = useUserStore()
  const [saved, setSaved] = useState(initialSaved)
  const [applied, setApplied] = useState(initialApplied)
  const [loadingSave, setLoadingSave] = useState(false)
  const [loadingApply, setLoadingApply] = useState(false)

  // update state if props change from dashboard refetches
  useEffect(() => { setSaved(initialSaved) }, [initialSaved])
  useEffect(() => { setApplied(initialApplied) }, [initialApplied])

  const title = lang === 'ta' && opp.title_ta ? opp.title_ta : opp.title
  const description = lang === 'ta' && opp.description_ta ? opp.description_ta : opp.description
  const catColor = CATEGORY_COLORS[opp.category] ?? 'bg-slate-500/20 text-slate-300 border-slate-500/30'

  const scoreColor =
    (opp.match_score ?? 0) >= 80
      ? 'bg-green-500/20 text-green-300 border-green-500/30'
      : (opp.match_score ?? 0) >= 50
      ? 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
      : 'bg-slate-500/20 text-slate-300 border-slate-500/30'

  const handleSave = async () => {
    if (!token) return
    setLoadingSave(true)
    try {
      if (saved) {
        await unsaveOpportunity(opp.id)
        setSaved(false)
      } else {
        await saveOpportunity(opp.id)
        setSaved(true)
      }
    } catch {
      // silently fail
    } finally {
      setLoadingSave(false)
    }
  }

  const handleApplied = async () => {
    if (!token) return
    setLoadingApply(true)
    try {
      await markApplied(opp.id)
      setApplied(true)
      onApplied?.()  // notify parent to refresh the applied count
    } catch {
      // silently fail
    } finally {
      setLoadingApply(false)
    }
  }

  return (
    <article
      className="card flex flex-col gap-3 group"
      aria-label={title}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className={clsx('category-chip', catColor)}>
            {t(opp.category)}
          </span>
          {opp.match_score !== undefined && (
            <span className={clsx('score-badge border', scoreColor)}>
              {opp.match_score}% {t('match_score')}
            </span>
          )}
        </div>

        {/* Save button */}
        {token && (
          <button
            onClick={handleSave}
            disabled={loadingSave}
            aria-label={saved ? 'Unsave' : 'Save'}
            aria-pressed={saved}
            className="shrink-0 p-1.5 rounded-lg text-slate-400 hover:text-yellow-400 transition-colors"
          >
            {saved ? (
              <BookmarkSolid className="w-5 h-5 text-yellow-400" />
            ) : (
              <BookmarkIcon className="w-5 h-5" />
            )}
          </button>
        )}
      </div>

      {/* Title */}
      <h3 className="font-semibold text-white text-base leading-snug group-hover:text-blue-300 transition-colors">
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className="text-sm text-slate-400 line-clamp-2">{description}</p>
      )}

      {/* Meta row */}
      <div className="flex flex-wrap gap-3 text-xs text-slate-500 mt-1">
        {opp.benefit && (
          <span className="flex items-center gap-1">
            <CurrencyRupeeIcon className="w-3.5 h-3.5 text-green-400" />
            <span className="text-green-300">{opp.benefit}</span>
          </span>
        )}
        {opp.deadline && (
          <span className="flex items-center gap-1">
            <CalendarIcon className="w-3.5 h-3.5 text-red-400" />
            <span className="text-red-300">{opp.deadline}</span>
          </span>
        )}
      </div>

      {/* Eligibility */}
      {opp.eligibility_summary && (
        <p className="text-xs text-slate-500 border-t border-slate-700/50 pt-2 mt-1">
          <span className="font-medium text-slate-400">{t('eligibility')}: </span>
          {opp.eligibility_summary}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-2 mt-auto pt-2">
        {opp.apply_url && (
          <a
            href={opp.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex-1 text-sm gap-1.5"
            aria-label={`Apply for ${title}`}
          >
            <ArrowTopRightOnSquareIcon className="w-4 h-4" />
            {t('apply_now')}
          </a>
        )}
        {token && !applied && (
          <button
            onClick={handleApplied}
            disabled={loadingApply}
            className="btn btn-ghost text-sm"
            aria-label="Mark as applied"
          >
            <CheckCircleIcon className="w-4 h-4" />
            {t('applied')}
          </button>
        )}
        {applied && (
          <span className="flex items-center gap-1 text-green-400 text-sm px-2">
            <CheckCircleIcon className="w-4 h-4" />
            {t('applied')}
          </span>
        )}
      </div>
    </article>
  )
}
