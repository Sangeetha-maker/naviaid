import { useState, useRef, useCallback } from 'react'

export interface UseVoiceReturn {
  isListening: boolean
  transcript: string
  error: string | null
  supported: boolean
  startListening: () => void
  stopListening: () => void
}

declare global {
  interface Window {
    SpeechRecognition: any
    webkitSpeechRecognition: any
  }
}

export function useVoice(lang = 'en-IN'): UseVoiceReturn {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<string | null>(null)
  const recogRef = useRef<any>(null)

  const supported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  const startListening = useCallback(() => {
    if (!supported) {
      setError('Speech recognition not supported on this browser.')
      return
    }
    const SpeechRecognition = window.SpeechRecognition ?? window.webkitSpeechRecognition
    const recog = new SpeechRecognition()
    recog.continuous = false
    recog.interimResults = true
    recog.lang = lang

    recog.onstart = () => {
      setIsListening(true)
      setError(null)
      setTranscript('')
    }
    recog.onresult = (e: any) => {
      const text = Array.from<any>(e.results)
        .map((r) => r[0].transcript)
        .join('')
      setTranscript(text)
    }
    recog.onerror = (e: any) => {
      setError(e.error)
      setIsListening(false)
    }
    recog.onend = () => setIsListening(false)

    recogRef.current = recog
    recog.start()
  }, [supported, lang])

  const stopListening = useCallback(() => {
    recogRef.current?.stop()
    setIsListening(false)
  }, [])

  return { isListening, transcript, error, supported, startListening, stopListening }
}
