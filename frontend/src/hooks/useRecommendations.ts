import { useState, useEffect } from 'react'
import { fetchRecommendations, type Opportunity } from '../lib/api'

export function useRecommendations() {
  const [data, setData] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const recs = await fetchRecommendations()
      setData(recs)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to load recommendations'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return { data, loading, error, refetch: load }
}
